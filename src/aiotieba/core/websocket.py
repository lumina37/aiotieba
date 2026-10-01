from __future__ import annotations

import asyncio
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
class MsgIDManager:
    """
    msg_id管理器
    """

    priv_gid: int = 0
    gid2mid: dict[int, MsgIDPair] = dcs.field(default_factory=lambda: {0: MsgIDPair()})

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

    def get_record_id(self) -> int:
        """
        获取record_id

        Returns:
            int: record_id
        """

        return self.get_msg_id(self.priv_gid) * 100 + 1


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
        weakref.finalize(self, self.__cancel_all)

    def __cancel_all(self) -> None:
        for ws_resp in self.waiter.values():
            ws_resp.future.cancel()

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
        if ws_resp is None:
            return
        ws_resp.future.set_result(data)


@dcs.dataclass
class WsCore:
    """
    保存websocket接口相关状态的核心容器
    """

    account: Account
    net_core: NetCore
    session: aiohttp.ClientSession
    waiter: WsWaiter
    callbacks: dict[int, TypeWebsocketCallback]
    websocket: aiohttp.ClientWebSocketResponse
    ws_dispatcher: asyncio.Task
    mid_manager: MsgIDManager
    _status: WsStatus
    loop: asyncio.AbstractEventLoop

    def __init__(self, account: Account, net_core: NetCore) -> None:
        self.set_account(account)
        self.net_core = net_core
        self.session: aiohttp.ClientSession = None

        self.callbacks: dict[int, TypeWebsocketCallback] = {}
        self.websocket: aiohttp.ClientWebSocketResponse = None
        self.ws_dispatcher: asyncio.Task = None

        self._status = WsStatus.CLOSED

        self.loop = asyncio.get_running_loop()

    def set_account(self, new_account: Account) -> None:
        self.account = new_account

    async def connect(self) -> None:
        """
        建立weboscket连接

        Raises:
            aiohttp.WSServerHandshakeError: websocket握手失败
        """

        self._status = WsStatus.CONNECTING

        self.waiter = WsWaiter(self.net_core.timeout.ws_read)
        self.mid_manager = MsgIDManager()

        from aiohttp import hdrs

        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None

        if self.session is None:
            self.session = aiohttp.ClientSession(
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
            self.websocket = await self.session.ws_connect(
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
            self.websocket = None
            self._status = WsStatus.CLOSED
            raise

        if self.ws_dispatcher is not None and not self.ws_dispatcher.done():
            self.ws_dispatcher.cancel()
        self.ws_dispatcher = self.loop.create_task(self.__ws_dispatch(), name="ws_dispatcher")

    async def close(self) -> None:
        if self.websocket is not None:
            await self.websocket.close()
            if self.ws_dispatcher is not None and not self.ws_dispatcher.done():
                self.ws_dispatcher.cancel()
            self.websocket = None
        self._status = WsStatus.CLOSED

        if self.session is not None:
            await self.session.close()
            self.session = None

    def __default_callback(self, req_id: int, data: bytes) -> None:
        self.waiter.set_done(req_id, data)

    async def __ws_dispatch(self) -> None:
        try:
            async for msg in self.websocket:
                data, cmd, req_id = parse_ws_bytes(self.account, msg.data)
                res_callback = self.callbacks.get(cmd, None)
                if res_callback is None:
                    self.__default_callback(req_id, data)
                else:
                    self.loop.create_task(res_callback(self, data, req_id))

        except asyncio.CancelledError:
            self._status = WsStatus.CLOSED
        except Exception:
            self._status = WsStatus.CLOSED
            if self.websocket is not None:
                await self.websocket.close()

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
        """

        response = self.waiter.new()
        req_data = pack_ws_bytes(self.account, data, cmd, response.req_id, compress=compress, encrypt=encrypt)

        try:
            async with timeout(self.net_core.timeout.ws_send, self.loop):
                await self.websocket.send_bytes(req_data)
        except TimeoutError as err:
            response.future.cancel()
            raise TimeoutError("Timeout to send") from err
        except BaseException:
            response.future.cancel()
        else:
            return response
