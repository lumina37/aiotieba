import asyncio
import time
from typing import Any, Awaitable, Callable, Dict, Optional

import aiohttp
import async_timeout
import yarl

from .._helper import DEFAULT_TIMEOUT, pack_ws_bytes, parse_ws_bytes
from . import TbCore

DEFAULT_SEND_TIMEOUT = 3.0
DEFAULT_READ_TIMEOUT = 5.0

TypeWebsocketCallback = Callable[["WsCore", bytes, int], Awaitable[None]]


class WsResponse(object):
    """
    websocket响应

    Args:
        data_future (asyncio.Future): 用于等待读事件到来的Future
    """

    __slots__ = ['_future']

    def __init__(self, data_future: asyncio.Future) -> None:
        self._future = data_future

    def _cancel(self) -> None:
        self._future.cancel()

    async def read(self) -> bytes:
        """
        读取websocket响应

        Returns:
            bytes

        Raises:
            asyncio.TimeoutError: 读取超时
        """

        try:
            with async_timeout.timeout(DEFAULT_READ_TIMEOUT):
                return await self._future
        except asyncio.TimeoutError as err:
            self._cancel()
            raise asyncio.TimeoutError("Timeout to read") from err


class MsgIDPair(object):

    __slots__ = [
        'last_id',
        'curr_id',
    ]

    def __init__(self, last_id: int, curr_id: int) -> None:
        self.last_id = last_id
        self.curr_id = curr_id

    def set_msg_id(self, curr_id: int) -> None:
        self.last_id = self.curr_id
        self.curr_id = curr_id


class MsgIDManager(object):

    __slots__ = [
        'priv_gid',
        'gid2mid',
    ]

    def __init__(self) -> None:
        self.priv_gid: int = None
        self.gid2mid: Dict[int, MsgIDPair] = None

    def set_msg_id(self, group_id: int, msg_id: int) -> None:
        mid_pair = self.gid2mid.get(group_id, None)
        if mid_pair is not None:
            mid_pair.set_msg_id(msg_id)
        else:
            mid_pair = MsgIDPair(msg_id, msg_id)

    def get_msg_id(self, group_id: int) -> int:
        return self.gid2mid[group_id].last_id

    def get_record_id(self) -> int:
        """
        获取record_id

        Returns:
            int: record_id
        """

        return self.get_msg_id(self.priv_gid) * 100 + 1


class WsCore(object):
    """
    保存websocket接口相关状态的核心容器
    """

    __slots__ = [
        'core',
        'connector',
        'heartbeat',
        'waiter',
        'callbacks',
        '_client_ws',
        'websocket',
        'ws_dispatcher',
        '_req_id',
        'mid_manager',
        'loop',
    ]

    def __init__(
        self,
        core: TbCore,
        connector: aiohttp.TCPConnector,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        heartbeat: Optional[float] = None,
    ) -> None:
        self.core: TbCore = core
        self.connector: aiohttp.TCPConnector = connector
        self.loop: asyncio.AbstractEventLoop = loop
        self.heartbeat: float = heartbeat

        self.callbacks: Dict[int, TypeWebsocketCallback] = {}
        self._client_ws: aiohttp.ClientSession = None
        self.websocket: aiohttp.ClientWebSocketResponse = None

    async def __websocket_connect(self) -> None:
        self.websocket = await self._client_ws._ws_connect(
            yarl.URL.build(scheme="ws", host="im.tieba.baidu.com", port=8000),
            heartbeat=self.heartbeat,
            proxy=self.core._proxy,
            proxy_auth=self.core._proxy_auth,
            ssl=False,
        )
        self.ws_dispatcher = self.loop.create_task(self.__ws_dispatch(), name="ws_dispatcher")

    async def connect(self) -> None:
        """
        建立weboscket连接

        Raises:
            aiohttp.WSServerHandshakeError: websocket握手失败
        """

        self.waiter: Dict[int, asyncio.Future] = {}
        self._req_id = int(time.time())
        self.mid_manager: MsgIDManager = MsgIDManager()

        ws_headers = {
            aiohttp.hdrs.HOST: "im.tieba.baidu.com:8000",
            aiohttp.hdrs.SEC_WEBSOCKET_EXTENSIONS: "im_version=2.3",
            aiohttp.hdrs.SEC_WEBSOCKET_VERSION: "13",
            'cuid': f"{self.core.cuid}|com.baidu.tieba_mini{self.core.post_version}",
        }
        self._client_ws = aiohttp.ClientSession(
            connector=self.connector,
            loop=self.loop,
            headers=ws_headers,
            connector_owner=False,
            raise_for_status=True,
            timeout=DEFAULT_TIMEOUT,
            read_bufsize=64 * 1024,
        )

        await self.__websocket_connect()

    async def reconnect(self) -> None:
        """
        重新建立weboscket连接

        Raises:
            aiohttp.WSServerHandshakeError: websocket握手失败
        """

        if not self.ws_dispatcher.done():
            self.ws_dispatcher.cancel()
        await self.__websocket_connect()

    async def close(self) -> None:
        if self._client_ws is None:
            return
        await self._client_ws.close()
        if self.is_aviliable:
            await self.websocket.close()
            self.ws_dispatcher.cancel()

    def __default_callback(self, req_id: int, data: bytes) -> None:
        self.set_done(req_id, data)

    def __generate_callback(self, req_id: int) -> Callable[[asyncio.Future], Any]:
        def done_callback(_):
            del self.waiter[req_id]

        return done_callback

    def register(self, req_id: int) -> WsResponse:
        """
        将一个req_id注册到等待器 此方法会创建Future对象

        Args:
            req_id (int): 请求id

        Returns:
            WsResponse: websocket响应
        """

        data_future = self.loop.create_future()
        data_future.add_done_callback(self.__generate_callback(req_id))
        self.waiter[req_id] = data_future
        return WsResponse(data_future)

    def set_done(self, req_id: int, data: bytes) -> None:
        """
        将req_id对应的Future设置为已完成

        Args:
            req_id (int): 请求id
            data (bytes): 填入的数据
        """

        data_future = self.waiter.get(req_id, None)
        if data_future is None:
            return
        data_future.set_result(data)

    async def __ws_dispatch(self) -> None:
        try:
            async for msg in self.websocket:
                data, cmd, req_id = parse_ws_bytes(self.core, msg.data)
                res_callback = self.callbacks.get(cmd, None)
                if res_callback is None:
                    self.__default_callback(req_id, data)
                else:
                    self.loop.create_task(res_callback(self, data, req_id))

        except asyncio.CancelledError:
            return

    @property
    def is_aviliable(self) -> bool:
        """
        websocket是否可用
        """

        return not (self.websocket is None or self.websocket.closed or self.websocket._writer.transport.is_closing())

    @property
    def req_id(self) -> int:
        """
        用作请求参数的id

        Note:
            每个websocket请求都有一个唯一的req_id
            每次调用都会使其自增1
        """

        self._req_id += 1
        return self._req_id

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
            asyncio.TimeoutError: 发送超时
        """

        req_id = self.req_id
        req_data = pack_ws_bytes(self.core, data, cmd, req_id, compress=compress, encrypt=encrypt)
        response = self.register(req_id)

        try:
            with async_timeout.timeout(DEFAULT_SEND_TIMEOUT):
                await self.websocket.send_bytes(req_data)
        except asyncio.TimeoutError as err:
            response._cancel()
            raise asyncio.TimeoutError("Timeout to send") from err
        else:
            return response
