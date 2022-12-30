import hashlib
import random
import time
import urllib.parse
from typing import List, Tuple

import httpx
import simdjson as jsonlib


def timestamp_ms(self) -> int:
    """
    毫秒级本机时间戳 (13位整数)

    Returns:
        int: 毫秒级整数时间戳
    """

    return int(time.time() * 1000)


async def send_request(client: httpx.AsyncClient, request: httpx.Request) -> httpx.Response:
    """
    简单发送http请求
    不包含重定向和身份验证功能

    Args:
        client (httpx.AsyncClient): 客户端
        request (httpx.Request): 待发送的请求

    Returns:
        httpx.Response
    """

    response = await client._send_single_request(request)
    try:
        await response.aread()
    except BaseException as err:
        await response.aclose()
        raise err
    return response


def sign(data: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    为参数元组列表添加贴吧客户端签名

    Args:
        data (list[tuple[str, str]]): 参数元组列表

    Returns:
        list[tuple[str, str]]: 签名后的form参数元组列表
    """

    raw_list = [f"{k}={v}" for k, v in data]
    raw_list.append("tiebaclient!!!")
    raw_str = "".join(raw_list)

    md5 = hashlib.md5()
    md5.update(raw_str.encode('utf-8'))
    data.append(('sign', md5.hexdigest()))

    return data


def pack_form_request(client: httpx.AsyncClient, url: str, data: List[Tuple[str, str]]) -> httpx.Request:
    """
    将参数元组列表打包为Request

    Args:
        client (httpx.AsyncClient): 客户端
        url (str): 链接
        data (list[tuple[str, str]]): 参数元组列表

    Returns:
        httpx.Request
    """

    body = urllib.parse.urlencode(data, doseq=True).encode("utf-8")

    request = httpx.Request("POST", url, stream=httpx.ByteStream(body))
    request.headers = httpx.Headers(
        [
            ("Content-Length", str(len(body))),
            ("Content-Type", "application/x-www-form-urlencoded"),
        ]
    )
    request.headers._list += client.headers._list
    if client.cookies:
        client.cookies.set_cookie_header(request)

    return request


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
