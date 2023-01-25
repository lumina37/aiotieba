import asyncio
import hashlib
import logging
import random
import sys
import urllib.parse
import zlib
from types import FrameType
from typing import Callable, List, Optional, Tuple

import aiohttp
import async_timeout
import yarl
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from ..._logging import get_logger
from .._core import TbCore
from .._exception import HTTPStatusError, exc_handlers
from ._const import DEFAULT_TIMEOUT

try:
    import simdjson as jsonlib

    _JSON_PARSER = jsonlib.Parser()
    parse_json = _JSON_PARSER.parse

except ImportError:
    import json as jsonlib

    parse_json = jsonlib.loads


if sys.version_info >= (3, 9):

    def removeprefix(s: str, prefix: str) -> str:
        """
        移除字符串前缀

        Args:
            s (str): 待移除前缀的字符串
            prefix (str): 待移除的前缀

        Returns:
            str: 移除前缀后的字符串
        """

        return s.removeprefix(prefix)

    def removesuffix(s: str, suffix: str) -> str:
        """
        移除字符串前缀

        Args:
            s (str): 待移除前缀的字符串
            suffix (str): 待移除的前缀

        Returns:
            str: 移除前缀后的字符串
        """

        return s.removesuffix(suffix)

else:

    def removeprefix(s: str, prefix: str) -> str:
        """
        移除字符串前缀

        Args:
            s (str): 待移除前缀的字符串
            prefix (str): 待移除的前缀

        Returns:
            str: 移除前缀后的字符串

        Note:
            该函数不会拷贝字符串
        """

        if s.startswith(prefix):
            return s[len(prefix) :]
        else:
            return s

    def removesuffix(s: str, suffix: str) -> str:
        """
        移除字符串后缀
        该函数将不会拷贝字符串

        Args:
            s (str): 待移除前缀的字符串
            suffix (str): 待移除的前缀

        Returns:
            str: 移除前缀后的字符串

        Note:
            该函数不会拷贝字符串
        """

        if s.endswith(suffix):
            return s[: len(suffix)]
        else:
            return s


def is_portrait(portrait: str) -> bool:
    """
    简单判断输入是否符合portrait格式
    """

    return isinstance(portrait, str) and portrait.startswith('tb.')


def timeout(delay: Optional[float], loop: asyncio.AbstractEventLoop) -> async_timeout.Timeout:
    now = loop.time()
    when = int(now) + delay
    return async_timeout.timeout_at(when)


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

    sign = hashlib.md5(raw_str.encode('utf-8')).hexdigest()
    data.append(('sign', sign))

    return data


def pack_form_request(core: TbCore, url: yarl.URL, data: List[Tuple[str, str]]) -> aiohttp.ClientRequest:
    """
    自动签名参数元组列表
    并将其打包为移动端表单请求

    Args:
        core (TbCore): 贴吧客户端核心容器
        url (yarl.URL): 链接
        data (list[tuple[str, str]]): 参数元组列表

    Returns:
        aiohttp.ClientRequest
    """

    payload = aiohttp.payload.BytesPayload(
        urllib.parse.urlencode(sign(data), doseq=True).encode('utf-8'),
        content_type="application/x-www-form-urlencoded",
    )

    request = aiohttp.ClientRequest(
        aiohttp.hdrs.METH_POST,
        url,
        headers=core._app_core.headers,
        data=payload,
        loop=core._loop,
        proxy=core._proxy,
        proxy_auth=core._proxy_auth,
        ssl=False,
    )

    return request


def pack_proto_request(core: TbCore, url: yarl.URL, data: bytes) -> aiohttp.ClientRequest:
    """
    打包移动端protobuf请求

    Args:
        core (TbCore): 贴吧客户端核心容器
        url (yarl.URL): 链接
        data (bytes): protobuf序列化后的二进制数据

    Returns:
        aiohttp.ClientRequest
    """

    writer = aiohttp.MultipartWriter('form-data', boundary=f"*-672328094--{random.randint(0,9)}")
    payload_headers = {
        aiohttp.hdrs.CONTENT_DISPOSITION: aiohttp.helpers.content_disposition_header(
            'form-data', name='data', filename='file'
        )
    }
    payload = aiohttp.BytesPayload(data, content_type='', headers=payload_headers)
    payload.headers.popone(aiohttp.hdrs.CONTENT_TYPE)
    writer._parts.append((payload, None, None))

    request = aiohttp.ClientRequest(
        aiohttp.hdrs.METH_POST,
        url,
        headers=core._app_proto_core.headers,
        data=writer,
        loop=core._loop,
        proxy=core._proxy,
        proxy_auth=core._proxy_auth,
        ssl=False,
    )

    return request


def pack_web_get_request(core: TbCore, url: yarl.URL, params: List[Tuple[str, str]]) -> aiohttp.ClientRequest:
    """
    打包网页端参数请求

    Args:
        core (TbCore): 贴吧客户端核心容器
        url (yarl.URL): 链接
        params (list[tuple[str, str]]): 参数元组列表

    Returns:
        aiohttp.ClientRequest
    """

    url = url.update_query(params)
    request = aiohttp.ClientRequest(
        aiohttp.hdrs.METH_GET,
        url,
        headers=core._web_core.headers,
        cookies=core._web_core.cookie_jar.filter_cookies(url),
        loop=core._loop,
        proxy=core._proxy,
        proxy_auth=core._proxy_auth,
        ssl=False,
    )

    return request


def pack_web_form_request(core: TbCore, url: yarl.URL, data: List[Tuple[str, str]]) -> aiohttp.ClientRequest:
    """
    打包网页端表单请求

    Args:
        core (TbCore): 贴吧客户端核心容器
        url (yarl.URL): 链接
        data (list[tuple[str, str]]): 参数元组列表

    Returns:
        aiohttp.ClientRequest
    """

    payload = aiohttp.payload.BytesPayload(
        urllib.parse.urlencode(data, doseq=True).encode('utf-8'),
        content_type="application/x-www-form-urlencoded",
    )

    request = aiohttp.ClientRequest(
        aiohttp.hdrs.METH_POST,
        url,
        headers=core._web_core.headers,
        data=payload,
        cookies=core._web_core.cookie_jar.filter_cookies(url),
        loop=core._loop,
        proxy=core._proxy,
        proxy_auth=core._proxy_auth,
        ssl=False,
    )

    return request


def pack_ws_bytes(
    core: TbCore, ws_bytes: bytes, /, cmd: int, req_id: int, *, need_gzip: bool = True, need_encrypt: bool = True
) -> bytes:
    """
    对ws_bytes进行打包 压缩加密并添加9字节头部

    Args:
        core (TiebaCore): 贴吧核心参数容器
        ws_bytes (bytes): 待发送的websocket数据
        cmd (int): 请求的cmd类型
        req_id (int): 请求的id
        need_gzip (bool, optional): 是否需要gzip压缩. Defaults to False.
        need_encrypt (bool, optional): 是否需要aes加密. Defaults to False.

    Returns:
        bytes: 打包后的websocket数据
    """

    if need_gzip:
        ws_bytes = zlib.compress(ws_bytes, 5)

    if need_encrypt:
        ws_bytes = pad(ws_bytes, AES.block_size)
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


def parse_ws_bytes(core: TbCore, ws_bytes: bytes) -> Tuple[bytes, int, int]:
    """
    对ws_bytes进行解包

    Args:
        core (TiebaCore): 贴吧核心参数容器
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
        ws_bytes = unpad(ws_bytes, AES.block_size)
    if flag & 0b01000000:
        ws_bytes = zlib.decompress(ws_bytes)

    return ws_bytes, cmd, req_id


def check_status_code(response: aiohttp.ClientResponse) -> None:
    if response.status != 200:
        raise HTTPStatusError(response.status, response.reason)


TypeHeadersChecker = Callable[[aiohttp.ClientResponse], None]


async def send_request(
    request: aiohttp.ClientRequest,
    connector: aiohttp.TCPConnector,
    read_bufsize: int = 64 * 1024,
    headers_checker: TypeHeadersChecker = check_status_code,
) -> bytes:
    """
    简单发送http请求
    不包含重定向和身份验证功能

    Args:
        request (aiohttp.ClientRequest): 待发送的请求
        connector (aiohttp.TCPConnector): 用于生成TCP连接的连接器
        read_bufsize (int, optional): 读缓冲区大小 以字节为单位. Defaults to 64KiB.
        headers_checker (TypeHeadersChecker, optional): headers检查函数. Defaults to check_status_code.

    Returns:
        bytes: body
    """

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

    # 合并cookies
    # cookie_jar.update_cookies(response.cookies, response._url)

    # 检查headers
    headers_checker(response)

    # 读取响应
    response._body = await response.content.read()
    body = response._body

    # 释放连接
    response.release()

    return body


def log_exception(frame: FrameType, err: Exception, log_str: str = '', log_level: int = logging.WARNING):
    """
    异常日志

    Args:
        frame (FrameType): 帧对象
        err (Exception): 异常对象
        log_str (str): 附加日志
        log_level (int): 日志等级
    """

    meth_name = frame.f_code.co_name
    log_str = f"{err}. {log_str}"
    logger = get_logger()
    if logger.isEnabledFor(log_level):
        record = logger.makeRecord(logger.name, log_level, None, frame.f_lineno, log_str, None, None, meth_name)
        logger.handle(record)

    exc_handlers._handle(meth_name, err)


def log_success(frame: FrameType, log_str: str = '', log_level: int = logging.INFO):
    """
    成功日志

    Args:
        frame (FrameType): 帧对象
        log_str (str): 附加日志
        log_level (int): 日志等级
    """

    meth_name = frame.f_code.co_name
    log_str = "Suceeded. " + log_str
    logger = get_logger()
    if logger.isEnabledFor(log_level):
        record = logger.makeRecord(logger.name, log_level, None, frame.f_lineno, log_str, None, None, meth_name)
        logger.handle(record)
