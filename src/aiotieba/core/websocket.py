from __future__ import annotations

import asyncio
import contextlib
import dataclasses as dcs
import gzip
import time
import weakref
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

import aiohttp
import yarl
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms

from ..__version__ import __version__
from ..enums import WsStatus
from ..helper import timeout

if TYPE_CHECKING:
    from .account import Account
    from .net import NetCore

TypeWebsocketCallback = Callable[["WsCore", bytes, int], Awaitable[None]]

WS_URL = yarl.URL.build(scheme="ws", host="im.tieba.baidu.com", port=8000)


def pack_ws_bytes(
    account: Account, data: bytes, cmd: int, req_id: int, *, compress: bool = False, encrypt: bool = True
) -> bytes:
    """
    打包数据并添加9字节头部

    Args:
        account (Account): 贴吧的用户参数容器
        data (bytes): 待发送的websocket数据
        cmd (int): 请求的cmd类型
        req_id (int): 请求的id
        compress (bool, optional): 是否需要gzip压缩. Defaults to False.
        encrypt (bool, optional): 是否需要aes加密. Defaults to True.

    Returns:
        bytes: 打包后的websocket数据
    """

    flag = 0x08

    if compress:
        flag |= 0b01000000
        data = gzip.compress(data, compresslevel=6, mtime=0)
    if encrypt:
        flag |= 0b10000000
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        data = padder.update(data) + padder.finalize()
        encryptor = account.aes_ecb_chiper.encryptor()
        data = encryptor.update(data) + encryptor.finalize()

    data = b"".join([
        flag.to_bytes(1, "big"),
        cmd.to_bytes(4, "big"),
        req_id.to_bytes(4, "big"),
        data,
    ])

    return data


def parse_ws_bytes(account: Account, data: bytes) -> tuple[bytes, int, int]:
    """
    对websocket返回数据进行解包

    Args:
        account (Account): 贴吧的用户参数容器
        data (bytes): 接收到的websocket数据

    Returns:
        tuple[bytes, int, int]: 解包后的websocket数据 依次为数据、cmd类型、请求id
    """

    data_view = memoryview(data)
    flag = data_view[0]
    cmd = int.from_bytes(data_view[1:5], "big")
    req_id = int.from_bytes(data_view[5:9], "big")

    data = data_view[9:].tobytes()
    if flag & 0b10000000:
        decryptor = account.aes_ecb_chiper.decryptor()
        data = decryptor.update(data) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(data) + unpadder.finalize()
    if flag & 0b01000000:
        data = gzip.decompress(data)

    return data, cmd, req_id


@dcs.dataclass
class MsgIDPair:
    """
    长度为2的msg_id队列 记录新旧msg_id
    """

    last_id: int = 0
    curr_id: int = 0

    def update_msg_id(self, curr_id: int) -> None:
        """
        更新msg_id

        Args:
            curr_id (int): 当前消息的msg_id
        """

        self.last_id = self.curr_id
        self.curr_id = curr_id


@dcs.dataclass
class PrivChatCursors:
    """
    与某个用户的私信会话游标

    Attributes:
        local_msg_id (int): 本端最后一次发送使用的local_msg_id 由服务端回显
        pulled_msg_id (int): 已拉取到的最新msg_id
        sent_msg_id (int): 最近一次上报的已读位置msg_id
        read_msg_id (int): 对方已读到的最新msg_id
    """

    local_msg_id: int = 0
    pulled_msg_id: int = 0
    sent_msg_id: int = 0
    read_msg_id: int = 0


@dcs.dataclass
class MsgIDManager:
    """
    msg_id管理器
    """

    priv_gid: int = 0
    gid2mid: dict[int, MsgIDPair] = dcs.field(default_factory=lambda: {0: MsgIDPair()})
    uid2cursors: dict[int, PrivChatCursors] = dcs.field(default_factory=dict)

    def update_msg_id(self, group_id: int, msg_id: int) -> None:
        """
        更新group_id对应的msg_id

        Args:
            group_id (int): 消息组id
            msg_id (int): 当前消息的msg_id
        """

        mid_pair = self.gid2mid.get(group_id, None)
        if mid_pair is not None:
            mid_pair.update_msg_id(msg_id)
        else:
            self.gid2mid[group_id] = MsgIDPair(msg_id, msg_id)

    def get_msg_id(self, group_id: int) -> int:
        """
        获取group_id对应的msg_id

        Args:
            group_id (int): 消息组id

        Returns:
            int: 上一条消息的msg_id
        """

        return self.gid2mid[group_id].last_id

    def get_cursors(self, user_id: int) -> PrivChatCursors:
        """
        获取与某个用户的私信会话游标 不存在时创建

        Args:
            user_id (int): 用户的user_id

        Returns:
            PrivChatCursors: 私信会话游标
        """

        cursors = self.uid2cursors.get(user_id, None)
        if cursors is None:
            cursors = PrivChatCursors()
            self.uid2cursors[user_id] = cursors

        return cursors

    def get_local_msg_id(self, user_id: int) -> int:
        """
        获取下一条私信的local_msg_id

        Args:
            user_id (int): 接收方的user_id

        Returns:
            int: local_msg_id
        """

        cursors = self.get_cursors(user_id)
        base = max(cursors.local_msg_id, cursors.pulled_msg_id * 100)

        return base + 1

    def update_local_msg_id(self, user_id: int, local_msg_id: int) -> None:
        """
        更新最近一次发送使用的local_msg_id

        Args:
            user_id (int): 接收方的user_id
            local_msg_id (int): 发送时使用的local_msg_id
        """

        cursors = self.get_cursors(user_id)
        if local_msg_id > cursors.local_msg_id:
            cursors.local_msg_id = local_msg_id

    def update_pulled_msg_id(self, user_id: int, msg_id: int) -> None:
        """
        更新已拉取到的最新msg_id

        Args:
            user_id (int): 对端的user_id
            msg_id (int): 拉取到的msg_id
        """

        cursors = self.get_cursors(user_id)
        if msg_id > cursors.pulled_msg_id:
            cursors.pulled_msg_id = msg_id

    def update_sent_msg_id(self, user_id: int, msg_id: int) -> None:
        """
        更新最近一次上报的已读位置msg_id

        Args:
            user_id (int): 对端的user_id
            msg_id (int): 上报的已读位置msg_id
        """

        cursors = self.get_cursors(user_id)
        if msg_id > cursors.sent_msg_id:
            cursors.sent_msg_id = msg_id

    def update_read_msg_id(self, user_id: int, msg_id: int) -> None:
        """
        更新对方已读到的最新msg_id

        Args:
            user_id (int): 对端的user_id
            msg_id (int): 对方已读位置msg_id
        """

        cursors = self.get_cursors(user_id)
        if msg_id > cursors.read_msg_id:
            cursors.read_msg_id = msg_id


@dcs.dataclass
class WsResponse:
    """
    websocket响应

    Args:
        future (asyncio.Future): 用于等待读事件到来的Future
        req_id (int): 请求id
        read_timeout (float): 读超时时间
    """

    loop: asyncio.AbstractEventLoop
    future: asyncio.Future
    req_id: int
    read_timeout: float

    def __init__(self, req_id: int, read_timeout: float) -> None:
        self.loop = asyncio.get_running_loop()
        self.future = self.loop.create_future()
        self.req_id = req_id
        self.read_timeout = read_timeout

    async def read(self) -> bytes:
        """
        读取websocket响应

        Returns:
            bytes

        Raises:
            TimeoutError: 读取超时
        """

        try:
            async with timeout(self.read_timeout, self.loop):
                return await self.future
        except TimeoutError as err:
            self.future.cancel()
            raise TimeoutError("Timeout to read") from err
        except BaseException:
            self.future.cancel()
            raise


@dcs.dataclass
class WsWaiter:
    """
    websocket等待映射
    """

    loop: asyncio.AbstractEventLoop
    waiter: weakref.WeakValueDictionary
    req_id: int
    read_timeout: float

    def __init__(self, read_timeout: float) -> None:
        self.loop = asyncio.get_running_loop()
        self.waiter = weakref.WeakValueDictionary()
        self.req_id = int(time.time())
        self.read_timeout = read_timeout

    def new(self) -> WsResponse:
        """
        创建一个可用于等待数据的响应对象

        Returns:
            WsResponse: websocket响应
        """

        self.req_id += 1
        ws_resp = WsResponse(self.req_id, self.read_timeout)
        self.waiter[self.req_id] = ws_resp
        return ws_resp

    def set_done(self, req_id: int, data: bytes) -> None:
        """
        将req_id对应的响应Future设置为已完成

        Args:
            req_id (int): 请求id
            data (bytes): 填入的数据
        """

        ws_resp: WsResponse = self.waiter.get(req_id, None)
        if ws_resp is None or ws_resp.future.done():
            return
        ws_resp.future.set_result(data)

    def fail_all(self, err: BaseException) -> None:
        """
        使所有等待中的响应以异常结束

        Args:
            err (BaseException): 异常
        """

        for ws_resp in list(self.waiter.values()):
            if not ws_resp.future.done():
                ws_resp.future.set_exception(err)


@dcs.dataclass
class WsCore:
    """
    保存websocket接口相关状态的核心容器
    """

    account: Account
    net_core: NetCore
    client_version: str
    session: aiohttp.ClientSession | None
    waiter: WsWaiter | None
    callbacks: dict[int, TypeWebsocketCallback]
    websocket: aiohttp.ClientWebSocketResponse | None
    ws_dispatcher: asyncio.Task | None
    callback_tasks: set[asyncio.Task]
    mid_manager: MsgIDManager
    _status: WsStatus
    loop: asyncio.AbstractEventLoop

    def __init__(self, account: Account, net_core: NetCore, client_version: str) -> None:
        self.set_account(account)
        self.net_core = net_core
        self.client_version = client_version
        self.session = None

        self.waiter = None
        self.callbacks: dict[int, TypeWebsocketCallback] = {}
        self.websocket = None
        self.ws_dispatcher = None
        self.callback_tasks: set[asyncio.Task] = set()
        self.mid_manager = MsgIDManager()

        self._status = WsStatus.CLOSED

        self.loop = asyncio.get_running_loop()

    def set_account(self, new_account: Account) -> None:
        self.account = new_account

    async def connect(self) -> None:
        """
        建立websocket连接

        Raises:
            aiohttp.WSServerHandshakeError: websocket握手失败
            aiohttp.ServerDisconnectedError: 连接在握手期间被关闭
        """

        await self.close()

        self._status = WsStatus.CONNECTING
        self.waiter = WsWaiter(self.net_core.timeout.ws_read)
        self.mid_manager = MsgIDManager()

        from aiohttp import hdrs

        session = self.session = aiohttp.ClientSession(
            connector=self.net_core.connector,
            connector_owner=False,
            cookie_jar=aiohttp.DummyCookieJar(),
            skip_auto_headers={hdrs.ACCEPT},
        )

        proxy = self.net_core.proxy
        if proxy.auth is None:
            proxy_headers = None
        else:
            proxy_headers = {"Proxy-Authorization": aiohttp.encode_basic_auth(proxy.auth.login, proxy.auth.password)}

        try:
            self.websocket = await session.ws_connect(
                WS_URL,
                headers={
                    hdrs.SEC_WEBSOCKET_EXTENSIONS: "im_version=2.3",
                    hdrs.ACCEPT_ENCODING: "gzip",
                    hdrs.USER_AGENT: f"aiotieba/{__version__}",
                },
                timeout=self.net_core.timeout.ws_timeout,
                autoclose=True,
                autoping=True,
                heartbeat=self.net_core.timeout.ws_heartbeat,
                ssl=False,
                compress=0,
                proxy=proxy.url,
                proxy_headers=proxy_headers,
            )
        except BaseException:
            await self.close()
            raise

        websocket = self.websocket
        waiter = self.waiter
        if websocket is None or waiter is None:
            await self.close()
            raise aiohttp.ServerDisconnectedError("websocket连接已关闭")

        self.ws_dispatcher = self.loop.create_task(self.__ws_dispatch(websocket, waiter), name="ws_dispatcher")

    async def close(self) -> None:
        """
        关闭连接并终止后台任务
        """

        if self._status is WsStatus.CLOSED and self.websocket is None and self.session is None:
            return

        self._status = WsStatus.CLOSED

        websocket, self.websocket = self.websocket, None
        dispatcher, self.ws_dispatcher = self.ws_dispatcher, None
        session, self.session = self.session, None
        waiter, self.waiter = self.waiter, None

        if waiter is not None:
            waiter.fail_all(aiohttp.ServerDisconnectedError("websocket连接已关闭"))

        try:
            if websocket is not None:
                with contextlib.suppress(Exception):
                    await websocket.close()

            if dispatcher is not None and not dispatcher.done():
                dispatcher.cancel()
                with contextlib.suppress(asyncio.CancelledError, Exception):
                    await dispatcher

            current_task = asyncio.current_task()
            callback_tasks = [task for task in self.callback_tasks if task is not current_task]
            self.callback_tasks.clear()

            for task in callback_tasks:
                task.cancel()
            if callback_tasks:
                await asyncio.gather(*callback_tasks, return_exceptions=True)

        finally:
            if session is not None:
                await session.close()

    async def __ws_dispatch(self, websocket: aiohttp.ClientWebSocketResponse, waiter: WsWaiter) -> None:
        try:
            async for msg in websocket:
                if msg.type is not aiohttp.WSMsgType.BINARY:
                    continue

                data, cmd, req_id = parse_ws_bytes(self.account, msg.data)
                res_callback = self.callbacks.get(cmd, None)
                if res_callback is None:
                    waiter.set_done(req_id, data)
                else:
                    task = self.loop.create_task(res_callback(self, data, req_id))
                    self.callback_tasks.add(task)
                    task.add_done_callback(self.callback_tasks.discard)

        except asyncio.CancelledError:
            raise
        except Exception:
            with contextlib.suppress(Exception):
                await websocket.close()
        finally:
            self._status = WsStatus.CLOSED
            waiter.fail_all(aiohttp.ServerDisconnectedError("websocket连接已断开"))

    @property
    def status(self) -> WsStatus:
        """
        websocket状态

        Returns:
            WsStatus: 当前的websocket状态
        """

        if self._status != WsStatus.CLOSED and (self.websocket is None or self.websocket.closed):
            self._status = WsStatus.CLOSED
        return self._status

    async def send(self, data: bytes, cmd: int, *, compress: bool = False, encrypt: bool = True) -> WsResponse:
        """
        将protobuf序列化结果打包发送

        Args:
            data (bytes): 待发送的数据
            cmd (int): 请求的cmd类型
            compress (bool, optional): 是否需要gzip压缩. Defaults to False.
            encrypt (bool, optional): 是否需要aes加密. Defaults to True.

        Returns:
            WsResponse: websocket响应对象

        Raises:
            TimeoutError: 发送超时
            aiohttp.ServerDisconnectedError: 连接未建立或已关闭
        """

        waiter = self.waiter
        websocket = self.websocket
        if waiter is None or websocket is None or websocket.closed:
            raise aiohttp.ServerDisconnectedError("websocket连接未建立")

        response = waiter.new()
        req_data = pack_ws_bytes(self.account, data, cmd, response.req_id, compress=compress, encrypt=encrypt)

        try:
            async with timeout(self.net_core.timeout.ws_send, self.loop):
                await websocket.send_bytes(req_data)
        except TimeoutError as err:
            response.future.cancel()
            raise TimeoutError("Timeout to send") from err
        except BaseException:
            response.future.cancel()
            raise
        else:
            return response
