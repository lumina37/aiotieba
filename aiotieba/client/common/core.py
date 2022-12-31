import hashlib
import random
import time
import uuid
from typing import ClassVar, Optional

from Crypto.Cipher import AES

from ..._config import CONFIG
from ..._logger import LOG


class TiebaCore(object):
    """
    贴吧核心参数集

    Args:
        BDUSS_key (str, optional): 用于快捷调用BDUSS. Defaults to None.
    """

    __slots__ = [
        '_BDUSS_key',
        '_BDUSS',
        '_STOKEN',
        '_client_id',
        '_cuid',
        '_cuid_galaxy2',
        '_ws_password',
    ]

    main_version: ClassVar[str] = "12.34.3.0"  # 最新版本
    # no_fold_version: ClassVar[str] = "12.12.1.0"  # 最后一个回复列表不发生折叠的版本
    post_version: ClassVar[str] = "9.1.0.0"  # 极速版

    def __init__(self, BDUSS_key: Optional[str] = None) -> None:
        self._BDUSS_key = BDUSS_key

        user_cfg = CONFIG['User'].get(BDUSS_key, {})
        self.BDUSS = user_cfg.get('BDUSS', '')
        self.STOKEN = user_cfg.get('STOKEN', '')

        self._client_id: str = None
        self._cuid: str = None
        self._cuid_galaxy2: str = None
        self._ws_password: bytes = None

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

        if hasattr(self, "_BDUSS"):
            LOG.warning("BDUSS已初始化 无法修改")
            return

        if not new_BDUSS:
            self._BDUSS = ""
            return

        legal_length = 192
        if (len_new_BDUSS := len(new_BDUSS)) != legal_length:
            LOG.warning(f"BDUSS的长度应为{legal_length}个字符 而输入的{new_BDUSS}有{len_new_BDUSS}个字符")
            self._BDUSS = ""
            return

        self._BDUSS = new_BDUSS

    @property
    def STOKEN(self) -> str:
        """
        当前账号的STOKEN
        """

        return self._STOKEN

    @STOKEN.setter
    def STOKEN(self, new_STOKEN: str) -> None:

        if hasattr(self, "_STOKEN"):
            LOG.warning("STOKEN已初始化 无法修改")
            return

        if not new_STOKEN:
            self._STOKEN = ""
            return

        legal_length = 64
        if (len_new_STOKEN := len(new_STOKEN)) != legal_length:
            LOG.warning(f"STOKEN的长度应为{legal_length}个字符 而输入的{new_STOKEN}有{len_new_STOKEN}个字符")
            self._STOKEN = ""
            return

        self._STOKEN = new_STOKEN

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
            ws_secret_key = hashlib.pbkdf2_hmac('sha1', self.core.ws_password, salt, 5, 32)
            self._ws_aes_chiper = AES.new(ws_secret_key, AES.MODE_ECB)

        return self._ws_aes_chiper
