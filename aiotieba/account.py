__all__ = ['Account']

import binascii
import random
import time
import uuid
from typing import Dict, Optional

from ._config import CONFIG
from ._logger import LOG
from .typedefs import BasicUserInfo


class Account(object):
    """
    贴吧账号容器

    Args:
        BDUSS_key (str, optional): 用于从CONFIG中提取BDUSS. Defaults to None.
    """

    __slots__ = [
        'BDUSS_key',
        '_BDUSS',
        '_STOKEN',
        '_user',
        '_tbs',
        '_client_id',
        '_cuid',
        '_cuid_galaxy2',
    ]

    def __init__(self, BDUSS_key: Optional[str] = None) -> None:
        self.BDUSS_key = BDUSS_key
        user_dict: Dict[str, str] = CONFIG['User'].get(BDUSS_key, {})
        self.BDUSS = user_dict.get('BDUSS', '')
        self.STOKEN = user_dict.get('STOKEN', '')

        self._user: BasicUserInfo = None
        self._tbs: str = None
        self._client_id: str = None
        self._cuid: str = None
        self._cuid_galaxy2: str = None

    @property
    def BDUSS(self) -> str:
        """
        当前账号的BDUSS
        """

        return self._BDUSS

    @BDUSS.setter
    def BDUSS(self, new_BDUSS: str) -> None:

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
    def timestamp_ms(self) -> int:
        """
        返回13位毫秒级整数时间戳

        Returns:
            int: 毫秒级整数时间戳
        """

        return int(time.time() * 1000)

    @property
    def client_id(self) -> str:
        """
        返回一个供贴吧客户端使用的client_id
        在初次生成后该属性便不会再发生变化

        Returns:
            str: 举例 wappc_1653660000000_123
        """

        if self._client_id is None:
            self._client_id = f"wappc_{self.timestamp_ms}_{random.randint(0,999):03d}"
        return self._client_id

    @property
    def cuid(self) -> str:
        """
        返回一个供贴吧客户端使用的cuid
        在初次生成后该属性便不会再发生变化

        Returns:
            str: 举例 baidutiebaappe4200716-58a8-4170-af15-ea7edeb8e513
        """

        if self._cuid is None:
            self._cuid = "baidutiebaapp" + str(uuid.uuid4())
        return self._cuid

    @property
    def cuid_galaxy2(self) -> str:
        """
        返回一个供贴吧客户端使用的cuid_galaxy2
        在初次生成后该属性便不会再发生变化

        Returns:
            str: 举例 159AB36E0E5C55E4AAE340CA046F1303|0
        """

        if self._cuid_galaxy2 is None:
            rand_str = binascii.hexlify(random.randbytes(16)).decode('ascii').upper()
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
