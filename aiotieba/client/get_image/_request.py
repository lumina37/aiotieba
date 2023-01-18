import asyncio

import aiohttp

from .._exception import ContentTypeError, HTTPStatusError
from .._helper import DEFAULT_TIMEOUT, timeout


async def img_send_request(request: aiohttp.ClientRequest, connector: aiohttp.TCPConnector) -> bytes:

    # 获取TCP连接
    try:
        async with timeout(DEFAULT_TIMEOUT.connect, connector._loop):
            conn = await connector.connect(request, [], DEFAULT_TIMEOUT)
    except asyncio.TimeoutError as exc:
        raise aiohttp.ServerTimeoutError(f"Connection timeout to host {request.url}") from exc

    # 设置响应解析流程
    conn.protocol.set_response_params(
        read_until_eof=True,
        auto_decompress=True,
        read_timeout=DEFAULT_TIMEOUT.sock_read,
        read_bufsize=512 * 1024,
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

    # 检查状态码
    if response.status != 200:
        raise HTTPStatusError(response.status, response.reason)

    if not response.content_type.endswith(('jpeg', 'png', 'bmp'), 6):
        raise ContentTypeError(f"Expect jpeg, png or bmp, got {response.content_type}")

    # 读取响应
    response._body = await response.content.read()
    body = response._body

    # 释放连接
    response.release()

    return body
