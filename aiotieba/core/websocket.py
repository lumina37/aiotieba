import asyncio
import binascii
import secrets
import time
import weakref
from typing import Awaitable, Callable, Dict

import aiohttp
import yarl

from ..exception import HTTPStatusError
from ..helper import WsStatus, timeout
from ..request.common import req2res
from ..request.websocket import pack_ws_bytes, parse_ws_bytes
from .account import Account
from .network import Network

TypeWebsocketCallback = Callable[["WsCore", bytes, int], Awaitable[None]]


class MsgIDPair(object):
    """
    长度为2的msg_id队列 记录新旧msg_id
    """

    __slots__ = [
        'last_id',
        'curr_id',
    ]

    def __init__(self, last_id: int, curr_id: int) -> None:
        self.last_id = last_id
        self.curr_id = curr_id

    def update_msg_id(self, curr_id: int) -> None:
        """
        更新msg_id

        Args:
            curr_id (int): 当前消息的msg_id
        """

        self.last_id = self.curr_id
        self.curr_id = curr_id


class MsgIDManager(object):
    """
    msg_id管理器
    """

    __slots__ = [
        'priv_gid',
        'gid2mid',
    ]

    def __init__(self) -> None:
        self.priv_gid: int = None
        self.gid2mid: Dict[int, MsgIDPair] = None

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
            mid_pair = MsgIDPair(msg_id, msg_id)

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


class WsResponse(object):
    """
    websocket响应

    Args:
        data_future (asyncio.Future): 用于等待读事件到来的Future
        req_id (int): 请求id
        read_timeout (float): 读超时时间
        loop (asyncio.AbstractEventLoop): 事件循环
    """

    __slots__ = [
        '__weakref__',
        'future',
        'req_id',
        'read_timeout',
        'loop',
    ]

    def __init__(self, req_id: int, read_timeout: float, loop: asyncio.AbstractEventLoop) -> None:
        self.future = loop.create_future()
        self.req_id = req_id
        self.read_timeout = read_timeout
        self.loop = loop

    async def read(self) -> bytes:
        """
        读取websocket响应

        Returns:
            bytes

        Raises:
            asyncio.TimeoutError: 读取超时
        """

        try:
            async with timeout(self.read_timeout, self.loop):
                return await self.future
        except asyncio.TimeoutError as err:
            self.future.cancel()
            raise asyncio.TimeoutError("Timeout to read") from err
        except BaseException:
            self.future.cancel()
            raise


class WsWaiter(object):
    """
    websocket等待映射
    """

    __slots__ = [
        '__weakref__',
        'waiter',
        'req_id',
        'read_timeout',
        'loop',
    ]

    def __init__(self, loop: asyncio.AbstractEventLoop, read_timeout: float) -> None:
        self.loop = loop
        self.read_timeout = read_timeout
        self.waiter = weakref.WeakValueDictionary()
        self.req_id = int(time.time())
        weakref.finalize(self, self.__cancel_all)

    def __cancel_all(self) -> None:
        for ws_resp in self.waiter.values():
            ws_resp.future.cancel()

    def new(self) -> WsResponse:
        """
        创建一个可用于等待数据的响应对象

        Args:
            req_id (int): 请求id

        Returns:
            WsResponse: websocket响应
        """

        self.req_id += 1
        ws_resp = WsResponse(self.req_id, self.read_timeout, self.loop)
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


class WsCore(object):
    """
    保存websocket接口相关状态的核心容器
    """

    __slots__ = [
        'account',
        'network',
        'waiter',
        'callbacks',
        'websocket',
        'ws_dispatcher',
        'mid_manager',
        '_status',
        '_req_id',
        'loop',
    ]

    def __init__(self, account: Account, network: Network, loop: asyncio.AbstractEventLoop) -> None:
        self.account = account
        self.network = network
        self.loop = loop

        self.callbacks: Dict[int, TypeWebsocketCallback] = {}
        self.websocket: aiohttp.ClientWebSocketResponse = None
        self.ws_dispatcher: asyncio.Task = None

        self._status = WsStatus.CLOSED

    async def connect(self) -> None:
        """
        建立weboscket连接

        Raises:
            aiohttp.WSServerHandshakeError: websocket握手失败
        """

        self._status = WsStatus.CONNECTING

        self.waiter = WsWaiter(self.loop, self.network.time.ws_read)
        self.mid_manager = MsgIDManager()

        from aiohttp import hdrs

        ws_url = yarl.URL.build(scheme="ws", host="im.tieba.baidu.com", port=8000)
        sec_key_bytes = binascii.b2a_base64(secrets.token_bytes(16), newline=False)
        headers = {
            hdrs.UPGRADE: "websocket",
            hdrs.CONNECTION: "upgrade",
            hdrs.SEC_WEBSOCKET_EXTENSIONS: "im_version=2.3",
            hdrs.SEC_WEBSOCKET_VERSION: "13",
            hdrs.SEC_WEBSOCKET_KEY: sec_key_bytes.decode('ascii'),
            hdrs.ACCEPT_ENCODING: "gzip",
            hdrs.HOST: "im.tieba.baidu.com:8000",
        }
        request = aiohttp.ClientRequest(
            hdrs.METH_GET,
            ws_url,
            headers=headers,
            loop=self.loop,
            proxy=self.network.proxy,
            proxy_auth=self.network.proxy_auth,
            ssl=False,
        )

        response = await req2res(request, self.network, False, 2 * 1024)

        if response.status != 101:
            raise HTTPStatusError(response.status, response.reason)

        try:
            conn = response.connection
            conn_proto = conn.protocol
            transport = conn.transport
            reader = aiohttp.FlowControlDataQueue(conn_proto, 1 << 16, loop=self.loop)
            conn_proto.set_parser(aiohttp.http.WebSocketReader(reader, 4 * 1024 * 1024), reader)
            writer = aiohttp.http.WebSocketWriter(conn_proto, transport, use_mask=True)
        except BaseException:
            response.close()
            raise
        else:
            self.websocket = aiohttp.ClientWebSocketResponse(
                reader,
                writer,
                'chat',
                response,
                self.network.time.ws_keepalive,
                True,
                True,
                self.loop,
                receive_timeout=self.network.time.ws_read,
                heartbeat=self.network.time.ws_heartbeat,
            )

        if self.ws_dispatcher is not None and not self.ws_dispatcher.done():
            self.ws_dispatcher.cancel()
        self.ws_dispatcher = self.loop.create_task(self.__ws_dispatch(), name="ws_dispatcher")

    async def close(self) -> None:
        if self.status == WsStatus.OPEN:
            await self.websocket.close()
            self.ws_dispatcher.cancel()
        self._status = WsStatus.CLOSED

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

    @property
    def status(self) -> WsStatus:
        """
        websocket状态
        """

        if self._status != WsStatus.CLOSED and self.websocket._writer.transport.is_closing():
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
            asyncio.TimeoutError: 发送超时
        """

        response = self.waiter.new()
        req_data = pack_ws_bytes(self.account, data, cmd, response.req_id, compress=compress, encrypt=encrypt)

        try:
            async with timeout(self.network.time.ws_send, self.loop):
                await self.websocket.send_bytes(req_data)
        except asyncio.TimeoutError as err:
            response.future.cancel()
            raise asyncio.TimeoutError("Timeout to send") from err
        except BaseException:
            response.future.cancel()
        else:
            return response
