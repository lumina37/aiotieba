import asyncio
import dataclasses as dcs
import random
import urllib.parse
from typing import Dict, List, Optional, Tuple

import aiohttp
import yarl

from ..__version__ import __version__
from ..const import APP_BASE_HOST
from ..helper.crypto import sign
from .account import Account
from .net import NetCore


@dcs.dataclass
class HttpContainer:
    """
    用于保存会话headers与cookies的容器
    """

    headers: Dict[str, str]
    cookie_jar: aiohttp.CookieJar

    def __init__(self, headers: Dict[str, str], cookie_jar: aiohttp.CookieJar) -> None:
        self.headers: Dict[str, str] = headers
        self.cookie_jar: aiohttp.CookieJar = cookie_jar


@dcs.dataclass
class HttpCore:
    """
    保存http接口相关状态的核心容器
    """

    account: Account
    net_core: NetCore
    app: HttpContainer
    app_proto: HttpContainer
    web: HttpContainer
    loop: asyncio.AbstractEventLoop

    def __init__(self, account: Account, net_core: NetCore, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self.account = account
        self.net_core = net_core
        self.loop = loop

        from aiohttp import hdrs

        app_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            hdrs.ACCEPT_ENCODING: "gzip",
            hdrs.CONNECTION: "keep-alive",
            hdrs.HOST: APP_BASE_HOST,
        }
        self.app = HttpContainer(app_headers, aiohttp.DummyCookieJar(loop=loop))

        app_proto_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            "x_bd_data_type": "protobuf",
            hdrs.ACCEPT_ENCODING: "gzip",
            hdrs.CONNECTION: "keep-alive",
            hdrs.HOST: APP_BASE_HOST,
        }
        self.app_proto = HttpContainer(app_proto_headers, aiohttp.DummyCookieJar(loop=loop))

        web_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            hdrs.ACCEPT_ENCODING: "gzip, deflate",
            hdrs.CACHE_CONTROL: "no-cache",
            hdrs.CONNECTION: "keep-alive",
        }
        self.web = HttpContainer(web_headers, aiohttp.CookieJar(loop=loop))
        BDUSS_morsel = aiohttp.cookiejar.Morsel()
        BDUSS_morsel.set('BDUSS', account.BDUSS, account.BDUSS)
        BDUSS_morsel['domain'] = "baidu.com"
        self.web.cookie_jar._cookies[("baidu.com", "/")]['BDUSS'] = BDUSS_morsel
        STOKEN_morsel = aiohttp.cookiejar.Morsel()
        STOKEN_morsel.set('STOKEN', account.STOKEN, account.STOKEN)
        STOKEN_morsel['domain'] = "tieba.baidu.com"
        self.web.cookie_jar._cookies[("tieba.baidu.com", "/")]['STOKEN'] = STOKEN_morsel

    def pack_form_request(self, url: yarl.URL, data: List[Tuple[str, str]]) -> aiohttp.ClientRequest:
        """
        自动签名参数元组列表
        并将其打包为移动端表单请求

        Args:
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
            headers=self.app.headers,
            data=payload,
            loop=self.loop,
            proxy=self.net_core.proxy.url,
            proxy_auth=self.net_core.proxy.auth,
            ssl=False,
        )

        return request

    def pack_proto_request(self, url: yarl.URL, data: bytes) -> aiohttp.ClientRequest:
        """
        打包移动端protobuf请求

        Args:
            url (yarl.URL): 链接
            data (bytes): protobuf序列化后的二进制数据

        Returns:
            aiohttp.ClientRequest
        """

        writer = aiohttp.MultipartWriter('form-data', boundary=f"*-reverse1999-{random.randint(0,9)}")
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
            headers=self.app_proto.headers,
            data=writer,
            loop=self.loop,
            proxy=self.net_core.proxy.url,
            proxy_auth=self.net_core.proxy.auth,
            ssl=False,
        )

        return request

    def pack_web_get_request(self, url: yarl.URL, params: List[Tuple[str, str]]) -> aiohttp.ClientRequest:
        """
        打包网页端参数请求

        Args:
            url (yarl.URL): 链接
            params (list[tuple[str, str]]): 参数元组列表

        Returns:
            aiohttp.ClientRequest
        """

        url = url.update_query(params)
        request = aiohttp.ClientRequest(
            aiohttp.hdrs.METH_GET,
            url,
            headers=self.web.headers,
            cookies=self.web.cookie_jar.filter_cookies(url),
            loop=self.loop,
            proxy=self.net_core.proxy.url,
            proxy_auth=self.net_core.proxy.auth,
            ssl=False,
        )

        return request

    def pack_web_form_request(self, url: yarl.URL, data: List[Tuple[str, str]]) -> aiohttp.ClientRequest:
        """
        打包网页端表单请求

        Args:
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
            headers=self.web.headers,
            data=payload,
            cookies=self.web.cookie_jar.filter_cookies(url),
            loop=self.loop,
            proxy=self.net_core.proxy.url,
            proxy_auth=self.net_core.proxy.auth,
            ssl=False,
        )

        return request
