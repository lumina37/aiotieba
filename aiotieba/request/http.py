import random
import urllib.parse
from typing import List, Tuple

import aiohttp
import yarl

from ..core import HttpCore
from ..helper.crypto import sign


def pack_form_request(http_core: HttpCore, url: yarl.URL, data: List[Tuple[str, str]]) -> aiohttp.ClientRequest:
    """
    自动签名参数元组列表
    并将其打包为移动端表单请求

    Args:
        http_core (HttpCore): 保存http接口相关状态的核心容器
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
        headers=http_core.app.headers,
        data=payload,
        loop=http_core.loop,
        proxy=http_core.network.proxy,
        proxy_auth=http_core.network.proxy_auth,
        ssl=False,
    )

    return request


def pack_proto_request(http_core: HttpCore, url: yarl.URL, data: bytes) -> aiohttp.ClientRequest:
    """
    打包移动端protobuf请求

    Args:
        http_core (HttpCore): 保存http接口相关状态的核心容器
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
        headers=http_core.app_proto.headers,
        data=writer,
        loop=http_core.loop,
        proxy=http_core.network.proxy,
        proxy_auth=http_core.network.proxy_auth,
        ssl=False,
    )

    return request


def pack_web_get_request(http_core: HttpCore, url: yarl.URL, params: List[Tuple[str, str]]) -> aiohttp.ClientRequest:
    """
    打包网页端参数请求

    Args:
        http_core (HttpCore): 保存http接口相关状态的核心容器
        url (yarl.URL): 链接
        params (list[tuple[str, str]]): 参数元组列表

    Returns:
        aiohttp.ClientRequest
    """

    url = url.update_query(params)
    request = aiohttp.ClientRequest(
        aiohttp.hdrs.METH_GET,
        url,
        headers=http_core.web.headers,
        cookies=http_core.web.cookie_jar.filter_cookies(url),
        loop=http_core.loop,
        proxy=http_core.network.proxy,
        proxy_auth=http_core.network.proxy_auth,
        ssl=False,
    )

    return request


def pack_web_form_request(http_core: HttpCore, url: yarl.URL, data: List[Tuple[str, str]]) -> aiohttp.ClientRequest:
    """
    打包网页端表单请求

    Args:
        http_core (HttpCore): 保存http接口相关状态的核心容器
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
        headers=http_core.web.headers,
        data=payload,
        cookies=http_core.web.cookie_jar.filter_cookies(url),
        loop=http_core.loop,
        proxy=http_core.network.proxy,
        proxy_auth=http_core.network.proxy_auth,
        ssl=False,
    )

    return request
