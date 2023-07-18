import hashlib
import secrets
from typing import Optional

from Crypto.Cipher import AES

from ..config import CONFIG
from ..helper.crypto import c3_aid, cuid_galaxy2


class Account(object):
    """
    贴吧的用户信息容器

    Args:
        BDUSS_key (str, optional): 用于快捷调用BDUSS. Defaults to None.
    """

    __slots__ = [
        '_BDUSS_key',
        '_BDUSS',
        '_STOKEN',
        '_tbs',
        '_android_id',
        '_uuid',
        '_client_id',
        '_sample_id',
        '_cuid',
        '_cuid_galaxy2',
        '_c3_aid',
        '_z_id',
        '_aes_ecb_sec_key',
        '_aes_ecb_chiper',
        '_aes_cbc_sec_key',
        '_aes_cbc_chiper',
    ]

    def __init__(
        self,
        BDUSS_key: Optional[str] = None,
    ) -> None:
        self._BDUSS_key = BDUSS_key
        users_cfg = CONFIG.setdefault('User', {})
        user_cfg = users_cfg.get(BDUSS_key, {})
        self.BDUSS = user_cfg.get('BDUSS', '')
        self.STOKEN = user_cfg.get('STOKEN', '')

        self._tbs: str = None
        self._android_id: str = None
        self._uuid: str = None
        self._client_id: str = None
        self._sample_id: str = None
        self._cuid: str = None
        self._cuid_galaxy2: str = None
        self._c3_aid: str = None
        self._z_id: str = None
        self._aes_ecb_sec_key: bytes = None
        self._aes_ecb_chiper = None
        self._aes_cbc_sec_key: bytes = None
        self._aes_cbc_chiper = None

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
        if new_BDUSS and len(new_BDUSS) != 192:
            raise ValueError(f"BDUSS的长度应为192个字符 而输入的{new_BDUSS}有{len(new_BDUSS)}个字符")
        self._BDUSS = new_BDUSS

    @property
    def STOKEN(self) -> str:
        """
        当前账号的STOKEN
        """

        return self._STOKEN

    @STOKEN.setter
    def STOKEN(self, new_STOKEN: str) -> None:
        if new_STOKEN and len(new_STOKEN) != 64:
            raise ValueError(f"STOKEN的长度应为64个字符 而输入的{new_STOKEN}有{len(new_STOKEN)}个字符")
        self._STOKEN = new_STOKEN

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
            self._android_id = secrets.token_hex(8)
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
    def sample_id(self) -> str:
        """
        返回一个可作为请求参数的sample_id

        Returns:
            str

        Examples:
            104505_3-105324_2-...-107269_1

        Note:
            在初始化后该属性便不会再发生变化
        """

        return self._sample_id

    @property
    def cuid(self) -> str:
        """
        返回一个可作为请求参数的cuid

        Returns:
            str

        Examples:
            baidutiebaappe4200716-58a8-4170-af15-ea7edeb8e513

        Note:
            在初始化后该属性便不会再发生变化\n
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
            在初始化后该属性便不会再发生变化\n
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
            在初始化后该属性便不会再发生变化\n
            此实现与12.x版本及以前的官方实现一致
        """

        if self._c3_aid is None:
            self._c3_aid = c3_aid(self.android_id, self.uuid)
        return self._c3_aid

    @property
    def z_id(self) -> str:
        """
        返回一个可作为请求参数的z_id

        Returns:
            str

        Note:
            在初始化后该属性便不会再发生变化\n
            此实现与12.x版本及以前的官方实现一致
        """

        return self._z_id

    @property
    def aes_ecb_sec_key(self) -> bytes:
        """
        返回一个供贴吧AES-ECB加密使用的随机密码

        Returns:
            bytes: 长度为31字节的随机密码

        Note:
            在初始化后该属性便不会再发生变化
        """

        if self._aes_ecb_sec_key is None:
            self._aes_ecb_sec_key = secrets.token_bytes(31)
        return self._aes_ecb_sec_key

    @property
    def aes_ecb_chiper(self):
        """
        获取供贴吧websocket使用的AES-ECB加密器

        Returns:
            Any: AES chiper
        """

        if self._aes_ecb_chiper is None:
            salt = b'\xa4\x0b\xc8\x34\xd6\x95\xf3\x13'
            ws_secret_key = hashlib.pbkdf2_hmac('sha1', self.aes_ecb_sec_key, salt, 5, 32)
            self._aes_ecb_chiper = AES.new(ws_secret_key, AES.MODE_ECB)

        return self._aes_ecb_chiper

    @property
    def aes_cbc_sec_key(self) -> bytes:
        """
        返回一个供贴吧AES-CBC加密使用的随机密码

        Returns:
            bytes: 长度为16字节的随机密码

        Note:
            在初始化后该属性便不会再发生变化
        """

        if self._aes_cbc_sec_key is None:
            self._aes_cbc_sec_key = secrets.token_bytes(16)
        return self._aes_cbc_sec_key

    @property
    def aes_cbc_chiper(self):
        """
        获取供贴吧客户端使用的AES-CBC加密器

        Returns:
            Any: AES chiper
        """

        if self._aes_cbc_chiper is None:
            self._aes_cbc_chiper = AES.new(self.aes_cbc_sec_key, AES.MODE_CBC, iv=b'\x00' * 16)
        return self._aes_cbc_chiper
