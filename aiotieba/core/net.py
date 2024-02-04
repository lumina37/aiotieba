import asyncio
import dataclasses as dcs
from typing import Callable, Tuple, Union

import aiohttp
import yarl

from ..config import ProxyConfig, TimeConfig
from ..exception import HTTPStatusError
from ..helper import timeout


def check_status_code(response: aiohttp.ClientResponse) -> None:
    if response.status != 200:
        raise HTTPStatusError(response.status, response.reason)


TypeHeadersChecker = Callable[[aiohttp.ClientResponse], None]


@dcs.dataclass
class NetCore:
    """
    网络请求相关容器

    Args:
        connector (aiohttp.TCPConnector): 用于生成TCP连接的连接器
        time_cfg (TimeConfig, optional): 各种时间设置. Defaults to TimeConfig().
        proxy_cfg (ProxyConfig, optional): Defaults to ProxyConfig().
    """

    connector: aiohttp.TCPConnector
    time_cfg: TimeConfig
    proxy_cfg: ProxyConfig

    def __init__(
        self,
        connector: aiohttp.TCPConnector,
        time_cfg: TimeConfig = TimeConfig,
        proxy_cfg: ProxyConfig = ProxyConfig,
    ) -> None:
        self.connector = connector

        if not isinstance(time_cfg, TimeConfig):
            time_cfg = TimeConfig()
        self.time_cfg = time_cfg

        if not isinstance(proxy_cfg, ProxyConfig):
            proxy_cfg = TimeConfig()
        self.proxy_cfg = proxy_cfg

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
