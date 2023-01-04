import gzip
import hashlib
import random
import urllib.parse
from typing import List, Optional, Tuple

import httpx
import simdjson as jsonlib
from Crypto.Cipher import AES

from ..._exception import HTTPStatusError
from .core import TiebaCore

APP_BASE_HOST = "tiebac.baidu.com"
WEB_BASE_HOST = "tieba.baidu.com"


def url(scheme: str, netloc: str, path: Optional[str] = None, query: Optional[str] = None) -> httpx.URL:
    """
    简单打包URL

    Returns:
        httpx.URL
    """

    url = httpx.URL()
    url._uri_reference = url._uri_reference.copy_with(scheme=scheme, authority=netloc, path=path, query=query)

    return url


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

    body = urllib.parse.urlencode(data, doseq=True).encode('utf-8')
    stream = httpx.ByteStream(body)

    request = httpx.Request("POST", url, stream=stream)
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


def pack_ws_bytes(
    core: TiebaCore, ws_bytes: bytes, /, cmd: int, req_id: int, *, need_gzip: bool = True, need_encrypt: bool = True
) -> bytes:
    """
    对ws_bytes进行打包 压缩加密并添加9字节头部

    Args:
        core (TiebaCore): 贴吧核心参数集
        ws_bytes (bytes): 待发送的websocket数据
        cmd (int): 请求的cmd类型
        req_id (int): 请求的id
        need_gzip (bool, optional): 是否需要gzip压缩. Defaults to False.
        need_encrypt (bool, optional): 是否需要aes加密. Defaults to False.

    Returns:
        bytes: 打包后的websocket数据
    """

    if need_gzip:
        ws_bytes = gzip.compress(ws_bytes, 5)

    if need_encrypt:
        pad_num = AES.block_size - (len(ws_bytes) % AES.block_size)
        ws_bytes += pad_num.to_bytes(1, 'big') * pad_num
        ws_bytes = core.ws_aes_chiper.encrypt(ws_bytes)

    flag = 0x08 | (need_gzip << 7) | (need_encrypt << 6)
    ws_bytes = b''.join(
        [
            flag.to_bytes(1, 'big'),
            cmd.to_bytes(4, 'big'),
            req_id.to_bytes(4, 'big'),
            ws_bytes,
        ]
    )

    return ws_bytes


def unpack_ws_bytes(core: TiebaCore, ws_bytes: bytes) -> Tuple[bytes, int, int]:
    """
    对ws_bytes进行解包

    Args:
        core (TiebaCore): 贴吧核心参数集
        ws_bytes (bytes): 接收到的websocket数据

    Returns:
        bytes: 解包后的websocket数据
        int: 对应请求的cmd类型
        int: 对应请求的id
    """

    if len(ws_bytes) < 9:
        return ws_bytes, 0, 0

    ws_view = memoryview(ws_bytes)
    flag = ws_view[0]
    cmd = int.from_bytes(ws_view[1:5], 'big')
    req_id = int.from_bytes(ws_view[5:9], 'big')

    ws_bytes = ws_view[9:].tobytes()
    if flag & 0b10000000:
        ws_bytes = core.ws_aes_chiper.decrypt(ws_bytes)
        ws_bytes = ws_bytes.rstrip(ws_bytes[-2:-1])
    if flag & 0b01000000:
        ws_bytes = gzip.decompress(ws_bytes)

    return ws_bytes, cmd, req_id


def raise_for_status(response: httpx.Response):
    """
    为非200状态码抛出异常

    Args:
        response (httpx.Response): 响应

    Raises:
        HTTPStatusError
    """

    if (status_code := response.status_code) != 200:
        code = httpx.codes(status_code)
        raise HTTPStatusError(f"{status_code} {code.phrase}")
