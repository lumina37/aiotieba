import asyncio
import hashlib
import random
import time
import uuid
from typing import Dict, Optional, Tuple, Union

import aiohttp
import yarl
from Crypto.Cipher import AES

from ..__version__ import __version__
from .._config import CONFIG
from .._logging import get_logger as LOG

APP_BASE_HOST = "tiebac.baidu.com"
WEB_BASE_HOST = "tieba.baidu.com"


class SessionCore(object):
    """
    用于保存客户端的headers与cookies的容器
    """

    __slots__ = [
        'headers',
        'cookie_jar',
    ]

    def __init__(self, headers: Dict[str, str], cookie_jar: aiohttp.CookieJar) -> None:
        self.headers = headers
        self.cookie_jar = cookie_jar


def _is_valid_BDUSS(BDUSS: str) -> bool:
    if not BDUSS:
        return False

    legal_length = 192
    if (len_new_BDUSS := len(BDUSS)) != legal_length:
        LOG().warning(f"BDUSS的长度应为{legal_length}个字符 而输入的{BDUSS}有{len_new_BDUSS}个字符")
        return False

    return True


def _is_valid_STOKEN(STOKEN: str) -> bool:
    if not STOKEN:
        return False

    legal_length = 64
    if (len_new_STOKEN := len(STOKEN)) != legal_length:
        LOG().warning(f"STOKEN的长度应为{legal_length}个字符 而输入的{STOKEN}有{len_new_STOKEN}个字符")
        return False

    return True


class TbCore(object):
    """
    贴吧客户端核心容器

    Args:
        loop (asyncio.AbstractEventLoop): 事件循环
        BDUSS_key (str, optional): 用于快捷调用BDUSS. Defaults to None.
        proxy (tuple[yarl.URL, aiohttp.BasicAuth] | bool, optional): True则使用环境变量代理 False则禁用代理
            输入一个 (http代理地址, 代理验证) 的元组以手动设置代理. Defaults to False.
    """

    __slots__ = [
        '_BDUSS_key',
        '_BDUSS',
        '_STOKEN',
        '_client_id',
        '_cuid',
        '_cuid_galaxy2',
        '_ws_password',
        '_ws_aes_chiper',
        '_app_core',
        '_app_proto_core',
        '_web_core',
        '_ws_core',
        '_proxy',
        '_proxy_auth',
        '_loop',
    ]

    main_version: str = "12.35.1.0"  # 最新版本
    # no_fold_version: str = "12.12.1.0"  # 最后一个回复列表不发生折叠的版本
    post_version: str = "9.1.0.0"  # 极速版

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        BDUSS_key: Optional[str] = None,
        proxy: Union[Tuple[yarl.URL, aiohttp.BasicAuth], bool] = False,
    ) -> None:
        self._loop = loop
        self._BDUSS_key = BDUSS_key

        self._client_id = None
        self._cuid = None
        self._cuid_galaxy2 = None
        self._ws_password = None
        self._ws_aes_chiper = None

        hdrs = aiohttp.hdrs

        app_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            hdrs.ACCEPT_ENCODING: "gzip",
            hdrs.CONNECTION: "keep-alive",
            hdrs.HOST: APP_BASE_HOST,
        }
        self._app_core = SessionCore(app_headers, aiohttp.DummyCookieJar(loop=loop))

        app_proto_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            "x_bd_data_type": "protobuf",
            hdrs.ACCEPT_ENCODING: "gzip",
            hdrs.CONNECTION: "keep-alive",
            hdrs.HOST: APP_BASE_HOST,
        }
        self._app_proto_core = SessionCore(app_proto_headers, aiohttp.DummyCookieJar(loop=loop))

        web_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            hdrs.ACCEPT_ENCODING: "gzip, deflate",
            hdrs.CACHE_CONTROL: "no-cache",
            hdrs.CONNECTION: "keep-alive",
        }
        self._web_core = SessionCore(web_headers, aiohttp.CookieJar(loop=loop))

        ws_headers = {
            hdrs.HOST: "im.tieba.baidu.com:8000",
            hdrs.SEC_WEBSOCKET_EXTENSIONS: "im_version=2.3",
        }
        self._ws_core = SessionCore(ws_headers, aiohttp.DummyCookieJar(loop=loop))

        user_cfg = CONFIG['User'].get(BDUSS_key, {})
        self.BDUSS = user_cfg.get('BDUSS', '')
        self.STOKEN = user_cfg.get('STOKEN', '')

        if proxy is False:
            self._proxy = None
            self._proxy_auth = None
        elif proxy is True:
            proxy_info = aiohttp.helpers.proxies_from_env().get('http', None)
            if proxy_info is None:
                self._proxy = None
                self._proxy_auth = None
            else:
                self._proxy = proxy_info.proxy
                self._proxy_auth = proxy_info.proxy_auth
        else:
            self._proxy, self._proxy_auth = proxy

    @property
    def BDUSS_key(self) -> str:
        """
        当前账号的BDUSS_key
        """

        return self._BDUSS_key

    @property
    def BDUSS(self) -> str:
        """
        当前账号的BDUSS
        """

        return self._BDUSS

    @BDUSS.setter
    def BDUSS(self, new_BDUSS: str) -> None:

        if not _is_valid_BDUSS(new_BDUSS):
            self._BDUSS = ''

        self._BDUSS = new_BDUSS

        BDUSS_morsel = aiohttp.cookiejar.Morsel()
        BDUSS_morsel.set('BDUSS', self._BDUSS, self._BDUSS)
        BDUSS_morsel['domain'] = "baidu.com"
        self._web_core.cookie_jar._cookies["baidu.com"]['BDUSS'] = BDUSS_morsel

    @property
    def STOKEN(self) -> str:
        """
        当前账号的STOKEN
        """

        return self._STOKEN

    @STOKEN.setter
    def STOKEN(self, new_STOKEN: str) -> None:

        if not _is_valid_STOKEN(new_STOKEN):
            self._STOKEN = ''

        self._STOKEN = new_STOKEN

        STOKEN_morsel = aiohttp.cookiejar.Morsel()
        STOKEN_morsel.set('STOKEN', self._STOKEN, self._STOKEN)
        STOKEN_morsel['domain'] = "tieba.baidu.com"
        self._web_core.cookie_jar._cookies["tieba.baidu.com"]['STOKEN'] = STOKEN_morsel

    @property
    def client_id(self) -> str:
        """
        返回一个可作为请求参数的client_id
        在初次生成后该属性便不会再发生变化

        Returns:
            str: 举例 wappc_1653660000000_123
        """

        if self._client_id is None:
            self._client_id = f"wappc_{int(time.time() * 1000)}_{random.randint(0,999):03d}"
        return self._client_id

    @property
    def cuid(self) -> str:
        """
        返回一个可作为请求参数的cuid
        在初次生成后该属性便不会再发生变化

        Returns:
            str: 举例 baidutiebaappe4200716-58a8-4170-af15-ea7edeb8e513
        """

        if self._cuid is None:
            self._cuid = f"baidutiebaapp{uuid.uuid4()}"
        return self._cuid

    @property
    def cuid_galaxy2(self) -> str:
        """
        返回一个可作为请求参数的cuid_galaxy2
        在初次生成后该属性便不会再发生变化

        Returns:
            str: 举例 159AB36E0E5C55E4AAE340CA046F1303|0
        """

        if self._cuid_galaxy2 is None:
            rand_str = random.randbytes(16).hex().upper()
            self._cuid_galaxy2 = rand_str + "|0"

        return self._cuid_galaxy2

    @property
    def ws_password(self) -> bytes:
        """
        返回一个供贴吧websocket使用的随机密码
        在初次生成后该属性便不会再发生变化

        Returns:
            bytes: 长度为36字节的随机密码
        """

        if self._ws_password is None:
            self._ws_password = random.randbytes(36)
        return self._ws_password

    @property
    def ws_aes_chiper(self):
        """
        获取供贴吧websocket使用的AES加密器

        Returns:
            Any: AES chiper
        """

        if self._ws_aes_chiper is None:
            salt = b'\xa4\x0b\xc8\x34\xd6\x95\xf3\x13'
            ws_secret_key = hashlib.pbkdf2_hmac('sha1', self.ws_password, salt, 5, 32)
            self._ws_aes_chiper = AES.new(ws_secret_key, AES.MODE_ECB)

        return self._ws_aes_chiper
