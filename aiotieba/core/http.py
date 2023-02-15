import asyncio
from typing import Dict, Optional

import aiohttp

from ..__version__ import __version__
from ..const import APP_BASE_HOST
from .account import Account
from .network import Network


class HttpContainer(object):
    """
    用于保存会话headers与cookies的容器
    """

    __slots__ = [
        'headers',
        'cookie_jar',
    ]

    def __init__(self, headers: Dict[str, str], cookie_jar: aiohttp.CookieJar) -> None:
        self.headers: Dict[str, str] = headers
        self.cookie_jar: aiohttp.CookieJar = cookie_jar


class HttpCore(object):
    """
    保存http接口相关状态的核心容器
    """

    __slots__ = [
        'account',
        'network',
        'app',
        'app_proto',
        'web',
        'loop',
    ]

    def __init__(
        self,
        account: Account,
        network: Network,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self.account = account
        self.network = network
        self.loop: asyncio.AbstractEventLoop = loop

        from aiohttp import hdrs

        app_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            hdrs.ACCEPT_ENCODING: "gzip",
            hdrs.CONNECTION: "keep-alive",
            hdrs.HOST: APP_BASE_HOST,
        }
        self.app: HttpContainer = HttpContainer(app_headers, aiohttp.DummyCookieJar(loop=loop))

        app_proto_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            "x_bd_data_type": "protobuf",
            hdrs.ACCEPT_ENCODING: "gzip",
            hdrs.CONNECTION: "keep-alive",
            hdrs.HOST: APP_BASE_HOST,
        }
        self.app_proto: HttpContainer = HttpContainer(app_proto_headers, aiohttp.DummyCookieJar(loop=loop))

        web_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            hdrs.ACCEPT_ENCODING: "gzip, deflate",
            hdrs.CACHE_CONTROL: "no-cache",
            hdrs.CONNECTION: "keep-alive",
        }
        self.web: HttpContainer = HttpContainer(web_headers, aiohttp.CookieJar(loop=loop))
        BDUSS_morsel = aiohttp.cookiejar.Morsel()
        BDUSS_morsel.set('BDUSS', account._BDUSS, account._BDUSS)
        BDUSS_morsel['domain'] = "baidu.com"
        self.web.cookie_jar._cookies[("baidu.com", "/")]['BDUSS'] = BDUSS_morsel
        STOKEN_morsel = aiohttp.cookiejar.Morsel()
        STOKEN_morsel.set('STOKEN', account._STOKEN, account._STOKEN)
        STOKEN_morsel['domain'] = "tieba.baidu.com"
        self.web.cookie_jar._cookies[("tieba.baidu.com", "/")]['STOKEN'] = STOKEN_morsel
