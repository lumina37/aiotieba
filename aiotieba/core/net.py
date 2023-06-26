import asyncio
from typing import Callable, Optional, Tuple, Union

import aiohttp
import yarl

from ..exception import HTTPStatusError
from ..helper import timeout


def check_status_code(response: aiohttp.ClientResponse) -> None:
    if response.status != 200:
        raise HTTPStatusError(response.status, response.reason)


TypeHeadersChecker = Callable[[aiohttp.ClientResponse], None]


class TimeConfig(object):
    """
    各种时间设置

    Note:
        所有时间均以秒为单位
    """

    __slots__ = [
        '_http',
        '_http_keepalive',
        '_ws_send',
        '_ws_read',
        '_ws_keepalive',
        '_ws_heartbeat',
        '_dns_ttl',
    ]

    def __init__(
        self,
        http_acquire_conn: float = 4.0,
        http_read: float = 12.0,
        http_connect: float = 3.0,
        http_keepalive: float = 30.0,
        ws_send: float = 3.0,
        ws_read: float = 8.0,
        ws_keepalive: float = 300.0,
        ws_heartbeat: Optional[float] = None,
        dns_ttl: float = 600.0,
    ) -> None:
        self._http = aiohttp.ClientTimeout(connect=http_acquire_conn, sock_read=http_read, sock_connect=http_connect)
        self._http_keepalive = http_keepalive
        self._ws_send = ws_send
        self._ws_read = ws_read
        self._ws_keepalive = ws_keepalive
        self._ws_heartbeat = ws_heartbeat
        self._dns_ttl = dns_ttl

    @property
    def http(self) -> aiohttp.ClientTimeout:
        """
        与aiohttp兼容的超时设置
        """

        return self._http

    @property
    def http_acquire_conn(self) -> float:
        """
        从连接池获取一个可用连接的超时时间
        """

        return self._http.connect

    @http_acquire_conn.setter
    def http_acquire_conn(self, new_val: float) -> None:
        self._http.connect = new_val

    @property
    def http_read(self) -> float:
        """
        从发送http请求到读取全部响应的超时时间
        """

        return self._http.sock_read

    @http_read.setter
    def http_read(self, new_val: float) -> None:
        self._http.sock_read = new_val

    @property
    def http_connect(self) -> float:
        """
        新建一个socket连接的超时时间
        """

        return self._http.sock_connect

    @http_connect.setter
    def http_connect(self, new_val: float) -> None:
        self._http.sock_connect = new_val

    @property
    def http_keepalive(self) -> float:
        """
        http长连接的保持时间
        """

        return self._http_keepalive

    @http_keepalive.setter
    def http_keepalive(self, new_val: float) -> None:
        self._http_keepalive = new_val

    @property
    def ws_send(self) -> float:
        """
        websocket发送数据的超时时间
        """

        return self._ws_send

    @ws_send.setter
    def ws_send(self, new_val: float) -> None:
        self._ws_send = new_val

    @property
    def ws_read(self) -> float:
        """
        从发送websocket数据到结束等待响应的超时时间
        """

        return self._ws_read

    @ws_read.setter
    def ws_read(self, new_val: float) -> None:
        self._ws_read = new_val

    @property
    def ws_keepalive(self) -> float:
        """
        websocket在长达ws_keepalive的时间内未发生IO则发送close信号关闭连接
        """

        return self._ws_keepalive

    @ws_keepalive.setter
    def ws_keepalive(self, new_val: float) -> None:
        self._ws_keepalive = new_val

    @property
    def ws_heartbeat(self) -> Optional[float]:
        """
        websocket心跳间隔
        """

        return self._ws_heartbeat

    @ws_heartbeat.setter
    def ws_heartbeat(self, new_val: Optional[float]) -> None:
        self._ws_heartbeat = new_val

    @property
    def dns_ttl(self) -> float:
        """
        dns的本地缓存超时时间
        """

        return self._dns_ttl

    @dns_ttl.setter
    def dns_ttl(self, new_val: float) -> None:
        self._dns_ttl = new_val


class NetCore(object):
    """
    网络请求相关容器

    Args:
        connector (aiohttp.TCPConnector): 用于生成TCP连接的连接器
        time_cfg (TimeConfig, optional): 各种时间设置. Defaults to TimeConfig().
        proxy (tuple[yarl.URL, aiohttp.BasicAuth], optional): 输入一个 (http代理地址, 代理验证) 的元组以手动设置代理. Defaults to (None, None).
    """

    __slots__ = [
        'connector',
        'time_cfg',
        'proxy',
        'proxy_auth',
    ]

    def __init__(
        self,
        connector: aiohttp.TCPConnector,
        time_cfg: TimeConfig = TimeConfig(),
        proxy: Union[Tuple[yarl.URL, aiohttp.BasicAuth], Tuple[None, None]] = (None, None),
    ) -> None:
        self.connector = connector
        self.time_cfg = time_cfg
        self.proxy, self.proxy_auth = proxy

    async def req2res(
        self, request: aiohttp.ClientRequest, read_until_eof: bool = True, read_bufsize: int = 64 * 1024
    ) -> aiohttp.ClientResponse:
        """
        发送http请求并返回ClientResponse

        Args:
            request (aiohttp.ClientRequest): 待发送的请求

            read_until_eof (bool, optional): 是否读取到EOF就中止. Defaults to True.
            read_bufsize (int, optional): 读缓冲区大小 以字节为单位. Defaults to 64KiB.

        Returns:
            ClientResponse: 响应
        """

        # 获取TCP连接
        try:
            async with timeout(self.time_cfg.http_connect, self.connector._loop):
                conn = await self.connector.connect(request, [], self.time_cfg.http)
        except asyncio.TimeoutError as exc:
            raise aiohttp.ServerTimeoutError(f"Connection timeout to host {request.url}") from exc

        # 设置响应解析流程
        conn.protocol.set_response_params(
            read_until_eof=read_until_eof,
            auto_decompress=True,
            read_timeout=self.time_cfg.http_read,
            read_bufsize=read_bufsize,
        )

        # 发送请求
        try:
            response = await request.send(conn)
        except BaseException:
            conn.close()
            raise
        try:
            await response.start(conn)
        except BaseException:
            response.close()
            raise

        return response

    async def send_request(
        self,
        request: aiohttp.ClientRequest,
        read_bufsize: int = 64 * 1024,
        headers_checker: TypeHeadersChecker = check_status_code,
    ) -> bytes:
        """
        简单发送http请求
        不包含重定向和身份验证功能

        Args:
            request (aiohttp.ClientRequest): 待发送的请求
            read_bufsize (int, optional): 读缓冲区大小 以字节为单位. Defaults to 64KiB.
            headers_checker (TypeHeadersChecker, optional): headers检查函数. Defaults to check_status_code.

        Returns:
            bytes: body
        """

        response = await self.req2res(request, True, read_bufsize)

        # 检查headers
        headers_checker(response)

        # 读取响应
        response._body = await response.content.read()
        body = response._body

        # 释放连接
        response.release()

        return body
