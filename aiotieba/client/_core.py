import asyncio
import binascii
import hashlib
import random
from typing import Dict, Optional, Tuple, Union

import aiohttp
import yarl
from Crypto.Cipher import AES

from ..__version__ import __version__
from .._config import CONFIG
from .._logging import get_logger as LOG
from ._hash import c3_aid, cuid_galaxy2

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
        '_tbs',
        '_android_id',
        '_uuid',
        '_client_id',
        '_cuid',
        '_cuid_galaxy2',
        '_c3_aid',
        '_z_id',
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
        BDUSS_key: Optional[str] = None,
        proxy: Union[Tuple[yarl.URL, aiohttp.BasicAuth], bool] = False,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._BDUSS_key = BDUSS_key

        self._tbs = None
        self._android_id = None
        self._uuid = None
        self._client_id = None
        self._cuid = None
        self._cuid_galaxy2 = None
        self._c3_aid = None
        self._z_id = None
        self._ws_password = None
        self._ws_aes_chiper = None

        if loop is None:
            self._loop = asyncio.get_running_loop()

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
    def android_id(self) -> str:
        """
        返回一个随机的android_id

        Returns:
            str: 长度为16的16进制字符串 包含8字节信息 字母为小写

        Examples:
            91be894d01799c49

        Note:
            在初始化后该属性便不会再发生变化
        """

        if self._android_id is None:
            self._android_id = random.randbytes(8).hex()
        return self._android_id

    @property
    def uuid(self) -> str:
        """
        使用uuid.uuid4生成并返回一个随机的uuid

        Returns:
            str: 包含16字节信息

        Examples:
            e4200716-58a8-4170-af15-ea7edeb8e513

        Note:
            在初始化后该属性便不会再发生变化
        """

        if self._uuid is None:
            import uuid

            self._uuid = str(uuid.uuid4())

        return self._uuid

    @property
    def tbs(self) -> str:
        """
        返回一个可作为请求参数的反csrf校验码tbs

        Returns:
            str: 长度为26的16进制字符串 字母为小写

        Examples:
            17634e03cbe25e6e1674526199

        Note:
            在初始化后该属性便不会再发生变化
        """

        return self._tbs

    @property
    def client_id(self) -> str:
        """
        返回一个可作为请求参数的client_id

        Returns:
            str

        Examples:
            wappc_1653660000000_123

        Note:
            在初始化后该属性便不会再发生变化
        """

        return self._client_id

    @property
    def cuid(self) -> str:
        """
        返回一个可作为请求参数的cuid

        Returns:
            str

        Examples:
            baidutiebaappe4200716-58a8-4170-af15-ea7edeb8e513

        Note:
            在初次生成后该属性便不会再发生变化
            此实现仅用于9.x等旧版本 11.x后请使用cuid_galaxy2填充对应字段
        """

        if self._cuid is None:
            self._cuid = f"baidutiebaapp{self.uuid}"
        return self._cuid

    @property
    def cuid_galaxy2(self) -> str:
        """
        返回一个可作为请求参数的cuid_galaxy2

        Returns:
            str

        Examples:
            A3ED2D7B9CFC28E8934A3FBD3A9579C7|VZ5FKB5XS

        Note:
            在初始化后该属性便不会再发生变化
            此实现与12.x版本及以前的官方实现一致
        """

        if self._cuid_galaxy2 is None:
            self._cuid_galaxy2 = cuid_galaxy2(self.android_id)
        return self._cuid_galaxy2

    @property
    def c3_aid(self) -> str:
        """
        返回一个可作为请求参数的c3_aid

        Returns:
            str

        Examples:
            A00-ZNU3O3EP74D727LMQY745CZSGZQJQZGP-3JXCKC7X

        Note:
            在初次生成后该属性便不会再发生变化
            此实现与12.x版本及以前的官方实现一致
        """

        if self._c3_aid is None:
            self._c3_aid = c3_aid(self.android_id, self.uuid)
        return self._c3_aid

    @property
    def z_id(self) -> str:
        """
        返回一个伪z_id

        Returns:
            str

        Note:
            在初次生成后该属性便不会再发生变化
            z_id是`/data/<pkgname>/shared_prefs/leroadcfg.xml`中键`xytk`对应的值
            这不是一个官方实现 因为我们尚不清楚该文件是如何生成的
        """

        if self._z_id is None:
            z_id = binascii.b2a_base64(random.randbytes(65))
            z_id = z_id.translate(bytes.maketrans(b'+/', b'-_')).rstrip(b'=\n')
            self._z_id = z_id.decode('utf-8')

        return self._z_id

    @property
    def ws_password(self) -> bytes:
        """
        返回一个供贴吧websocket使用的随机密码

        Returns:
            bytes: 长度为36字节的随机密码

        Note:
            在初次生成后该属性便不会再发生变化
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
