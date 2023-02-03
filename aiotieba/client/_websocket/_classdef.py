import asyncio
import binascii
import time
import weakref
from typing import Awaitable, Callable, Dict, Optional

import aiohttp
import async_timeout
import yarl
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from .._core import TbCore
from ._helper import pack_ws_bytes, parse_ws_bytes

_REQ_ID = None


TypeWebsocketCallback = Callable[[bytes, int], Awaitable[None]]


async def _default_callback(ws: "Websocket", data: bytes, req_id: int) -> None:
    """
    接收到消息时触发的默认回调
    """

    res_future = ws._res_waiter.get(req_id, None)
    if res_future:
        res_future.set_result(data)


class Websocket(object):
    """
    管理贴吧websocket请求

    Args:
        connector (aiohttp.TCPConnector): 使用的TCP连接器
        core (TbCore): 贴吧核心容器
    """

    __slots__ = [
        '_core',
        '_res_waiter',
        '_callback',
        '_client_ws',
        '_websocket',
        '_ws_dispatcher',
    ]

    def __init__(self, connector: aiohttp.TCPConnector, core: TbCore) -> None:
        self._core = core
        self._res_waiter = weakref.WeakValueDictionary()
        self._callback: Dict[int, TypeWebsocketCallback] = {}

        global _REQ_ID
        if _REQ_ID is None:
            _REQ_ID = int(time.time())

        timeout = aiohttp.ClientTimeout(connect=3.0, sock_read=12.0, sock_connect=3.2)
        ws_headers = {
            aiohttp.hdrs.HOST: "im.tieba.baidu.com:8000",
            aiohttp.hdrs.SEC_WEBSOCKET_EXTENSIONS: "im_version=2.3",
            aiohttp.hdrs.SEC_WEBSOCKET_VERSION: "13",
            'cuid': f"{self._core.cuid}|com.baidu.tieba_mini{self._core.post_version}",
        }
        self._client_ws = aiohttp.ClientSession(
            connector=connector,
            loop=core._loop,
            headers=ws_headers,
            connector_owner=False,
            raise_for_status=True,
            timeout=timeout,
            read_bufsize=256 * 1024,  # 256KiB
        )
        self._websocket: aiohttp.ClientWebSocketResponse = None
        self._ws_dispatcher: asyncio.Task = None

    async def close(self) -> None:
        if self._websocket is not None:
            await self._websocket.close()
            if not self._ws_dispatcher.done():
                self._ws_dispatcher.cancel()

    async def __ws_dispatch(self) -> None:
        """
        分发从贴吧websocket接收到的数据
        """

        try:
            async for msg in self._websocket:
                data, cmd, req_id = parse_ws_bytes(self._core, msg.data)
                res_callback = self._callback.get(cmd, _default_callback)
                await res_callback(self, data, req_id)

        except asyncio.CancelledError:
            return

    async def __create_websocket(self, heartbeat: Optional[float] = 800.0) -> None:
        """
        建立weboscket连接

        Args:
            heartbeat (float, optional): 定时ping的间隔秒数. Defaults to 800.0.

        Raises:
            aiohttp.WSServerHandshakeError: websocket握手失败
        """

        if self._ws_dispatcher is not None and not self._ws_dispatcher.done():
            self._ws_dispatcher.cancel()

        self._websocket = await self._client_ws._ws_connect(
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
            TiebaServerError: 服务端返回错误
        """

        if not self.is_aviliable:
            await self.__create_websocket(heartbeat=None)

            from ._api import pack_proto, parse_body

            pub_key = binascii.a2b_base64(
                b"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwQpwBZxXJV/JVRF/uNfyMSdu7YWwRNLM8+2xbniGp2iIQHOikPpTYQjlQgMi1uvq1kZpJ32rHo3hkwjy2l0lFwr3u4Hk2Wk7vnsqYQjAlYlK0TCzjpmiI+OiPOUNVtbWHQiLiVqFtzvpvi4AU7C1iKGvc/4IS45WjHxeScHhnZZ7njS4S1UgNP/GflRIbzgbBhyZ9kEW5/OO5YfG1fy6r4KSlDJw4o/mw5XhftyIpL+5ZBVBC6E1EIiP/dd9AbK62VV1PByfPMHMixpxI3GM2qwcmFsXcCcgvUXJBa9k6zP8dDQ3csCM2QNT+CQAOxthjtp/TFWaD7MzOdsIYb3THwIDAQAB"
            )
            pub_key = RSA.import_key(pub_key)
            rsa_chiper = PKCS1_v1_5.new(pub_key)
            secret_key = rsa_chiper.encrypt(self._core.aes_ecb_sec_key)

            proto = pack_proto(self._core, secret_key)

            body = await self.send(proto, cmd=1001, compress=False, encrypt=False, timeout=5.0)
            parse_body(body)

    @property
    def is_aviliable(self) -> bool:
        """
        websocket是否可用

        Returns:
            bool: True则websocket可用 反之不可用
        """

        return not (self._websocket is None or self._websocket.closed or self._websocket._writer.transport.is_closing())

    async def send(
        self, data: bytes, cmd: int, *, compress: bool = True, encrypt: bool = True, timeout: float
    ) -> bytes:
        """
        将protobuf序列化结果打包发送

        Args:
            data (bytes): 待发送的数据
            cmd (int): 请求的cmd类型
            compress (bool, optional): 是否需要gzip压缩. Defaults to False.
            encrypt (bool, optional): 是否需要aes加密. Defaults to False.

        Returns:
            bytes: 响应
        """

        global _REQ_ID
        _REQ_ID += 1
        req_id = _REQ_ID

        req_data = pack_ws_bytes(self._core, data, cmd, req_id, compress, encrypt)

        res_future = asyncio.Future()
        self._res_waiter[req_id] = res_future

        await self._websocket.send_bytes(req_data)

        try:
            with async_timeout.timeout(timeout):
                res_data = await res_future
        except asyncio.TimeoutError:
            del self._res_waiter[req_id]
            raise asyncio.TimeoutError("Timeout to read")
        else:
            del self._res_waiter[req_id]
            return res_data
