from __future__ import annotations

import asyncio
import dataclasses as dcs
from collections.abc import Callable
from typing import TYPE_CHECKING

import aiohttp

from ..config import ProxyConfig, TimeoutConfig
from ..exception import HTTPStatusError
from ..helper import timeout

if TYPE_CHECKING:
    from ssl import SSLContext


def check_status_code(response: aiohttp.ClientResponse) -> None:
    if response.status != 200:
        raise HTTPStatusError(response.status, response.reason)


TypeHeadersChecker = Callable[[aiohttp.ClientResponse], None]


@dcs.dataclass(slots=True)
class NetCore:
    """
    负责HTTP请求发送与TCP+TLS连接创建

    Args:
        connector (aiohttp.TCPConnector): 用于HTTP请求的TCP连接池
        ssl_context (SSLContext): 与连接器共享的TLS上下文
        proxy (ProxyConfig, optional): 代理配置. Defaults to None.
        timeout (TimeoutConfig, optional): 超时配置. Defaults to None.
    """

    connector: aiohttp.TCPConnector
    ssl_context: SSLContext
    proxy: ProxyConfig
    timeout: TimeoutConfig

    def __init__(
        self,
        connector: aiohttp.TCPConnector,
        ssl_context: SSLContext,
        proxy: ProxyConfig | None = None,
        timeout: TimeoutConfig | None = None,
    ) -> None:
        self.connector = connector
        self.ssl_context = ssl_context

        if not isinstance(proxy, ProxyConfig):
            proxy = ProxyConfig()
        self.proxy = proxy

        if not isinstance(timeout, TimeoutConfig):
            timeout = TimeoutConfig()
        self.timeout = timeout

    async def open_connection(
        self, host: str, port: int, *, connect_timeout: float
    ) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """
        使用共享TLS上下文建立TCP连接

        Args:
            host (str): 目标主机名或IP地址
            port (int): 目标端口
            connect_timeout (float): 建立连接的超时时间，单位为秒

        Returns:
            tuple[asyncio.StreamReader, asyncio.StreamWriter]: 连接的读取器与写入器

        Raises:
            TimeoutError: 建立连接超时

        Note:
            直接连接目标服务器，不经过代理和HTTP连接池
            调用方负责关闭返回的连接
        """

        connection = await asyncio.wait_for(
            asyncio.open_connection(host, port, ssl=self.ssl_context, family=self.connector.family),
            timeout=connect_timeout,
        )
        return connection

    async def req2res(self, request: aiohttp.ClientRequest, read_until_eof: bool = True) -> aiohttp.ClientResponse:
        """
        发送http请求并返回ClientResponse

        Args:
            request (aiohttp.ClientRequest): 待发送的请求

            read_until_eof (bool, optional): 是否读取到EOF就中止. Defaults to True.

        Returns:
            ClientResponse: 响应
        """

        try:
            async with timeout(self.timeout.http_connect, self.connector._loop):
                conn = await self.connector.connect(request, [], self.timeout.http_timeout)
        except TimeoutError as exc:
            raise aiohttp.ServerTimeoutError(f"Connection timeout to host {request.url}") from exc

        conn.protocol.set_response_params(
            read_until_eof=read_until_eof,
            auto_decompress=True,
            read_timeout=self.timeout.http_read,
        )

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

    async def send(
        self,
        request: aiohttp.ClientRequest,
        headers_checker: TypeHeadersChecker = check_status_code,
    ) -> bytes:
        """
        简单发送http请求
        不包含重定向和身份验证功能

        Args:
            request (aiohttp.ClientRequest): 待发送的请求
            headers_checker (TypeHeadersChecker, optional): headers检查函数. Defaults to check_status_code.

        Returns:
            bytes: body
        """

        response = await self.req2res(request, True)

        try:
            headers_checker(response)
            body = await response.read()
        finally:
            response.release()

        return body
