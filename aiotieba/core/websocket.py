import asyncio
import binascii
import dataclasses as dcs
import gzip
import time
import weakref
from typing import Awaitable, Callable, Dict, Optional, Tuple

import aiohttp
import yarl
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from ..enums import WsStatus
from ..exception import HTTPStatusError
from ..helper import randbytes_nosec, timeout
from .account import Account
from .net import NetCore

TypeWebsocketCallback = Callable[["WsCore", bytes, int], Awaitable[None]]


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
        data = pad(data, AES.block_size)
        data = account.aes_ecb_chiper.encrypt(data)

    data = b''.join(
        [
            flag.to_bytes(1, 'big'),
            cmd.to_bytes(4, 'big'),
            req_id.to_bytes(4, 'big'),
            data,
        ]
    )

    return data


def parse_ws_bytes(account: Account, data: bytes) -> Tuple[bytes, int, int]:
    """
    对websocket返回数据进行解包

    Args:
        account (Account): 贴吧的用户参数容器
        data (bytes): 接收到的websocket数据

    Returns:
        bytes: 解包后的websocket数据
        int: 对应请求的cmd类型
        int: 对应请求的id
    """

    data_view = memoryview(data)
    flag = data_view[0]
    cmd = int.from_bytes(data_view[1:5], 'big')
    req_id = int.from_bytes(data_view[5:9], 'big')

    data = data_view[9:].tobytes()
    if flag & 0b10000000:
        data = account.aes_ecb_chiper.decrypt(data)
        data = unpad(data, AES.block_size)
    if flag & 0b01000000:
        data = gzip.decompress(data)

    return data, cmd, req_id


@dcs.dataclass
class MsgIDPair:
    """
    长度为2的msg_id队列 记录新旧msg_id
    """

    last_id: int
    curr_id: int

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

    priv_gid: Optional[int] = None
    gid2mid: Optional[Dict[int, MsgIDPair]] = None

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


@dcs.dataclass
class WsResponse:
    """
    websocket响应

    Args:
        future (asyncio.Future): 用于等待读事件到来的Future
        req_id (int): 请求id
        read_timeout (float): 读超时时间
        loop (asyncio.AbstractEventLoop): 事件循环
    """

    future: asyncio.Future
    req_id: int
    read_timeout: float
    loop: asyncio.AbstractEventLoop

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


@dcs.dataclass
class WsWaiter:
    """
    websocket等待映射
    """

    waiter: weakref.WeakValueDictionary
    req_id: int
    read_timeout: float
    loop: asyncio.AbstractEventLoop

    def __init__(self, read_timeout: float, loop: asyncio.AbstractEventLoop) -> None:
        self.waiter = weakref.WeakValueDictionary()
        self.req_id = int(time.time())
        self.read_timeout = read_timeout
        self.loop = loop
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


@dcs.dataclass
class WsCore:
    """
    保存websocket接口相关状态的核心容器
    """

    account: Account
    net_core: NetCore
    waiter: WsWaiter
    callbacks: Dict[int, TypeWebsocketCallback]
    websocket: aiohttp.ClientWebSocketResponse
    ws_dispatcher: asyncio.Task
    mid_manager: MsgIDManager
    _status: WsStatus
    loop: asyncio.AbstractEventLoop

    def __init__(self, account: Account, net_core: NetCore, loop: asyncio.AbstractEventLoop) -> None:
        self.account = account
        self.net_core = net_core
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

        self.waiter = WsWaiter(self.net_core.timeout.ws_read, self.loop)
        self.mid_manager = MsgIDManager()

        from aiohttp import hdrs

        ws_url = yarl.URL.build(scheme="ws", host="im.tieba.baidu.com", port=8000)
        sec_key_bytes = binascii.b2a_base64(randbytes_nosec(16), newline=False)
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
            proxy=self.net_core.proxy.url,
            proxy_auth=self.net_core.proxy.auth,
            ssl=False,
        )

        response = await self.net_core.req2res(request, False, 2 * 1024)

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
                self.net_core.timeout.ws_keepalive,
                True,
                True,
                self.loop,
                receive_timeout=self.net_core.timeout.ws_read,
                heartbeat=self.net_core.timeout.ws_heartbeat,
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
            async with timeout(self.net_core.timeout.ws_send, self.loop):
                await self.websocket.send_bytes(req_data)
        except asyncio.TimeoutError as err:
            response.future.cancel()
            raise asyncio.TimeoutError("Timeout to send") from err
        except BaseException:
            response.future.cancel()
        else:
            return response
