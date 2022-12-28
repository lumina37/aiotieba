import hashlib
import random
from typing import List, Tuple

import httpx


async def send_request(client: httpx.AsyncClient, request: httpx.Request) -> httpx.Response:
    response = await client._send_single_request(request)
    try:
        await response.aread()
    except BaseException as err:
        await response.aclose()
        raise err
    return response


def pack_form(forms: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    打包form参数元组列表 为其添加贴吧客户端签名

    Args:
        payload (list[tuple[str, str]]): form参数元组列表

    Returns:
        list[tuple[str, str]]: 签名后的form参数元组列表
    """

    raw_list = [f"{k}={v}" for k, v in forms]
    raw_list.append("tiebaclient!!!")
    raw_str = "".join(raw_list)

    md5 = hashlib.md5()
    md5.update(raw_str.encode('utf-8'))
    forms.append(('sign', md5.hexdigest()))

    return forms


def pack_proto_request(client: httpx.AsyncClient, url: str, data: bytes) -> httpx.Request:
    """
    打包protobuf请求

    Args:
        client (httpx.AsyncClient): 客户端
        url (str): 链接
        data (bytes): protobuf序列化后的二进制数据

    Returns:
        httpx.Request
    """

    files = [('data', ('file', data, ''))]
    boundary = b"*-672328094--" + str(random.randint(0, 9)).encode('utf-8')

    stream = httpx._content.MultipartStream({}, files, boundary)
    request = httpx.Request("POST", url, stream=stream)
    request.headers = httpx.Headers(
        [
            ("Content-Length", str(stream.get_content_length())),
            ("Content-Type", stream.content_type),
        ]
    )
    request.headers._list += client.headers._list
    if client.cookies:
        client.cookies.set_cookie_header(request)

    return request
