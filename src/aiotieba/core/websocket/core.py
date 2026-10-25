from __future__ import annotations

import asyncio
import contextlib
import dataclasses as dcs
import time
import weakref
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

import aiohttp
import yarl

from ...__version__ import __version__
from ...enums import WsStatus
from ...helper import timeout
from .helper import pack_ws_bytes, parse_ws_bytes
from .msgid import MsgIDManager

if TYPE_CHECKING:
    from ..account import Account
    from ..net import NetCore

TypeWebsocketCallback = Callable[["WsCore", bytes, int], Awaitable[None]]

WS_URL = yarl.URL.build(scheme="ws", host="im.tieba.baidu.com", port=8000)


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
