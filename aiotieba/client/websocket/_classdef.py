import asyncio
import binascii
import time
from typing import Any, Awaitable, Callable, Dict, Optional

import aiohttp
import async_timeout
import yarl
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from .._core import TbCore
from .._helper import pack_ws_bytes, parse_ws_bytes

TypeWebsocketCallback = Callable[[bytes, int], Awaitable[None]]


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

    async def read(self, read_timeout: float = 5.0) -> bytes:
        """
        读取websocket响应

        Args:
            read_timeout (float, optional): 读取超时时间. Defaults to 5.0.

        Returns:
            bytes

        Raises:
            asyncio.TimeoutError: 读取超时
        """

        try:
            with async_timeout.timeout(read_timeout):
                return await self._future
        except asyncio.TimeoutError as err:
            self._cancel()
            raise asyncio.TimeoutError("Timeout to read") from err


class WsWaiter(object):
    """
    websocket事件等待器

    Args:
        loop (asyncio.AbstractEventLoop): 事件循环
    """

    __slots__ = [
        '_loop',
        '_waiter',
    ]

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._waiter: Dict[int, asyncio.Future] = {}

    def __get_callback(self, req_id: int) -> Callable[[asyncio.Future], Any]:
        def done_callback(_):
            del self._waiter[req_id]

        return done_callback

    def register(self, req_id: int) -> WsResponse:
        """
        将一个req_id注册到等待器 此方法会创建Future对象

        Args:
            req_id (int): 请求id

        Returns:
            WsResponse: websocket响应
        """

        data_future = self._loop.create_future()
        data_future.add_done_callback(self.__get_callback(req_id))
        self._waiter[req_id] = data_future
        return WsResponse(data_future)

    def set_done(self, req_id: int, data: bytes) -> None:
        """
        将req_id对应的Future设置为已完成

        Args:
            req_id (int): 请求id
            data (bytes): 填入的数据
        """

        data_future = self._waiter.get(req_id, None)
        if data_future is None:
            return
        data_future.set_result(data)


class Websocket(object):
    """
    管理贴吧websocket请求

    Args:
        connector (aiohttp.TCPConnector): 使用的TCP连接器
        core (TbCore): 贴吧核心容器
    """

    __slots__ = [
        '_core',
        '_connector',
        '_waiter',
        'callback',
        '_websocket',
        '_ws_dispatcher',
        '_req_id',
        'uid2rid',
        '_default_record_id',
        'gid2mid',
    ]

    def __init__(self, connector: aiohttp.TCPConnector, core: TbCore) -> None:
        self._core = core
        self._connector = connector
        self._websocket: aiohttp.ClientWebSocketResponse = None
        self._ws_dispatcher: asyncio.Task = None

    async def close(self) -> None:
        if self._websocket is not None:
            await self._websocket.close()
            self._ws_dispatcher.cancel()

    def __default_callback(self, req_id: int, data: bytes) -> None:
        self._waiter.set_done(req_id, data)

    async def __ws_dispatch(self) -> None:
        try:
            async for msg in self._websocket:
                data, cmd, req_id = parse_ws_bytes(self._core, msg.data)
                res_callback = self.callback.get(cmd, None)
                if res_callback is None:
                    self.__default_callback(req_id, data)
                else:
                    self._core._loop.create_task(res_callback(self, data, req_id))

        except asyncio.CancelledError:
            return

    async def _create_websocket(self, heartbeat: Optional[float] = 800.0) -> None:
        """
        建立weboscket连接

        Args:
            heartbeat (float, optional): 定时ping的间隔秒数. Defaults to 800.0.

        Raises:
            aiohttp.WSServerHandshakeError: websocket握手失败
        """

        if self._ws_dispatcher is not None and not self._ws_dispatcher.done():
            self._ws_dispatcher.cancel()

        timeout = aiohttp.ClientTimeout(connect=3.0, sock_read=12.0, sock_connect=3.2)
        ws_headers = {
            aiohttp.hdrs.HOST: "im.tieba.baidu.com:8000",
            aiohttp.hdrs.SEC_WEBSOCKET_EXTENSIONS: "im_version=2.3",
            aiohttp.hdrs.SEC_WEBSOCKET_VERSION: "13",
            'cuid': f"{self._core.cuid}|com.baidu.tieba_mini{self._core.post_version}",
        }
        client_ws = aiohttp.ClientSession(
            connector=self._connector,
            loop=self._core._loop,
            headers=ws_headers,
            connector_owner=False,
            raise_for_status=True,
            timeout=timeout,
            read_bufsize=64 * 1024,
        )
        self._websocket = await client_ws._ws_connect(
            yarl.URL.build(scheme="ws", host="im.tieba.baidu.com", port=8000),
            heartbeat=heartbeat,
            proxy=self._core._proxy,
            proxy_auth=self._core._proxy_auth,
            ssl=False,
        )

        self._ws_dispatcher = asyncio.create_task(self.__ws_dispatch(), name="ws_dispatcher")

    async def init_websocket(self) -> None:
        """
        初始化weboscket连接对象并发送初始化信息

        Raises:
            aiohttp.WSServerHandshakeError: websocket握手失败
            asyncio.TimeoutError: 发送初始化信息超时
        """

        if not self.is_aviliable:
            await self._create_websocket(heartbeat=None)

            self._waiter = WsWaiter(self._core._loop)
            self.callback: Dict[int, TypeWebsocketCallback] = {}
            self._req_id = int(time.time())
            self._default_record_id = 0

            pub_key = binascii.a2b_base64(
                b"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwQpwBZxXJV/JVRF/uNfyMSdu7YWwRNLM8+2xbniGp2iIQHOikPpTYQjlQgMi1uvq1kZpJ32rHo3hkwjy2l0lFwr3u4Hk2Wk7vnsqYQjAlYlK0TCzjpmiI+OiPOUNVtbWHQiLiVqFtzvpvi4AU7C1iKGvc/4IS45WjHxeScHhnZZ7njS4S1UgNP/GflRIbzgbBhyZ9kEW5/OO5YfG1fy6r4KSlDJw4o/mw5XhftyIpL+5ZBVBC6E1EIiP/dd9AbK62VV1PByfPMHMixpxI3GM2qwcmFsXcCcgvUXJBa9k6zP8dDQ3csCM2QNT+CQAOxthjtp/TFWaD7MzOdsIYb3THwIDAQAB"
            )
            pub_key = RSA.import_key(pub_key)
            rsa_chiper = PKCS1_v1_5.new(pub_key)
            secret_key = rsa_chiper.encrypt(self._core.aes_ecb_sec_key)

            from .. import get_group_msg, init_websocket

            proto = init_websocket.pack_proto(self._core, secret_key)
            resp = await self.send(proto, cmd=init_websocket.CMD, compress=False, encrypt=False, send_timeout=5.0)
            groups = init_websocket.parse_body(await resp.read())
            for group in groups:
                if group._group_type == get_group_msg.GroupType.PRIVATE_MSG:
                    self._default_record_id = group._last_msg_id * 1e2 + 1
            self.uid2rid = {}
            self.gid2mid = {g._group_id: g._last_msg_id for g in groups}

    @property
    def is_aviliable(self) -> bool:
        """
        websocket是否可用

        Note:
            True则websocket可用 反之不可用
        """

        return not (self._websocket is None or self._websocket.closed or self._websocket._writer.transport.is_closing())

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

    @property
    def record_id(self) -> int:
        """
        获取用作请求参数的记录id
        """

        return self._record_id

    async def send(
        self, data: bytes, cmd: int, *, compress: bool = False, encrypt: bool = True, send_timeout: float = 3.0
    ) -> WsResponse:
        """
        将protobuf序列化结果打包发送

        Args:
            data (bytes): 待发送的数据
            cmd (int): 请求的cmd类型
            compress (bool, optional): 是否需要gzip压缩. Defaults to False.
            encrypt (bool, optional): 是否需要aes加密. Defaults to True.
            send_timeout (float, optional): 发送超时时间. Defaults to 3.0.

        Returns:
            WsResponse: websocket响应对象

        Raises:
            asyncio.TimeoutError: 发送超时
        """

        req_id = self.req_id
        req_data = pack_ws_bytes(self._core, data, cmd, req_id, compress=compress, encrypt=encrypt)
        response = self._waiter.register(req_id)

        try:
            with async_timeout.timeout(send_timeout):
                await self._websocket.send_bytes(req_data)
        except asyncio.TimeoutError as err:
            response._cancel()
            raise asyncio.TimeoutError("Timeout to send") from err
        else:
            return response
