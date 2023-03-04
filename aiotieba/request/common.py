import asyncio
from typing import Callable

import aiohttp

from ..core import Network
from ..exception import HTTPStatusError
from ..helper import timeout


def check_status_code(response: aiohttp.ClientResponse) -> None:
    if response.status != 200:
        raise HTTPStatusError(response.status, response.reason)


TypeHeadersChecker = Callable[[aiohttp.ClientResponse], None]


async def req2res(
    request: aiohttp.ClientRequest,
    network: Network,
    read_until_eof: bool = True,
    read_bufsize: int = 64 * 1024,
) -> aiohttp.ClientResponse:
    """
    发送http请求并返回ClientResponse

    Args:
        request (aiohttp.ClientRequest): 待发送的请求
        network (Network): 网络请求相关容器
        read_until_eof (bool, optional): 是否读取到EOF就中止. Defaults to True.
        read_bufsize (int, optional): 读缓冲区大小 以字节为单位. Defaults to 64KiB.

    Returns:
        ClientResponse: 响应
    """

    # 获取TCP连接
    try:
        async with timeout(network.time.http_connect, network.connector._loop):
            conn = await network.connector.connect(request, [], network.time.http)
    except asyncio.TimeoutError as exc:
        raise aiohttp.ServerTimeoutError(f"Connection timeout to host {request.url}") from exc

    # 设置响应解析流程
    conn.protocol.set_response_params(
        read_until_eof=read_until_eof,
        auto_decompress=True,
        read_timeout=network.time.http_read,
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
    request: aiohttp.ClientRequest,
    network: Network,
    read_bufsize: int = 64 * 1024,
    headers_checker: TypeHeadersChecker = check_status_code,
) -> bytes:
    """
    简单发送http请求
    不包含重定向和身份验证功能

    Args:
        request (aiohttp.ClientRequest): 待发送的请求
        network (Network): 网络请求相关容器
        read_bufsize (int, optional): 读缓冲区大小 以字节为单位. Defaults to 64KiB.
        headers_checker (TypeHeadersChecker, optional): headers检查函数. Defaults to check_status_code.

    Returns:
        bytes: body
    """

    response = await req2res(request, network, True, read_bufsize)

    # 检查headers
    headers_checker(response)

    # 读取响应
    response._body = await response.content.read()
    body = response._body

    # 释放连接
    response.release()

    return body
