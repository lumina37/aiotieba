from __future__ import annotations

import random
from typing import ClassVar, Self

from ..api._classdef import UserInfo
from ..helper.crypto import c3_aid, cuid_galaxy2


class Account:
    """
    贴吧的账号与用户信息容器

    Args:
        BDUSS (str, optional): BDUSS. Defaults to ''.
        STOKEN (str, optional): 网页STOKEN. Defaults to ''.

    Attributes:
        BDUSS (str): BDUSS
        STOKEN (str): 网页STOKEN
        user (UserInfo): 当前用户信息 不参与序列化
        tbs (str): 长度为26的小写16进制字符串 例:91be894d01799c4991be894d01
        android_id (str): 长度为16的小写16进制字符串 包含8字节信息 例:91be894d01799c49
        uuid (str): 包含16字节信息 例:e4200716-58a8-4170-af15-ea7edeb8e513
        client_id (str): 例:wappc_1653660000000_123
        sample_id (str): 例:104505_3-105324_2-...-107269_1
        cuid (str): 例:baidutiebaappe4200716-58a8-4170-af15-ea7edeb8e513
        cuid_galaxy2 (str): 例:A3ED2D7B9CFC28E8934A3FBD3A9579C7|VZ5FKB5XS
        c3_aid (str): 例:A00-ZNU3O3EP74D727LMQY745CZSGZQJQZGP-3JXCKC7X
        baidu_id (str): 例:1A2B3C4D5E6F708192A3B4C5D6E7F809:FG=1
        zid (str): zid
        ws_sec_key (bytes): 供贴吧websocket加密使用的随机密码 长度为31字节
        zid_sec_key (bytes): 供贴吧zid加密使用的随机密码 长度为16字节
    """

    __slots__ = [
        "_BDUSS",
        "_STOKEN",
        "user",
        "_tbs",
        "_android_id",
        "_uuid",
        "_client_id",
        "_sample_id",
        "_cuid",
        "_cuid_galaxy2",
        "_c3_aid",
        "_baidu_id",
        "_zid",
        "_ws_sec_key",
        "_zid_sec_key",
    ]

    __serialize__: ClassVar[list[str]] = [
        "_BDUSS",
        "_STOKEN",
        "_tbs",
        "_android_id",
        "_uuid",
        "_client_id",
        "_sample_id",
        "_cuid",
        "_cuid_galaxy2",
        "_c3_aid",
        "_baidu_id",
        "_zid",
        "_ws_sec_key",
        "_zid_sec_key",
    ]

    def __init__(self, BDUSS: str = "", STOKEN: str = "") -> None:
        self.BDUSS = BDUSS
        self.STOKEN = STOKEN

        self.user = UserInfo()
        self._tbs: str = None
        self._android_id: str = None
        self._uuid: str = None
        self._client_id: str = None
        self._sample_id: str = None
        self._cuid: str = None
        self._cuid_galaxy2: str = None
        self._c3_aid: str = None
        self._baidu_id: str = None
        self._zid: str = None
        self._ws_sec_key: bytes = None
        self._zid_sec_key: bytes = None

    def __repr__(self) -> str:
        return str(self.to_dict())

    def __hash__(self) -> int:
        return hash(self.BDUSS)

    def __eq__(self, obj: Account) -> bool:
        return self.BDUSS == obj.BDUSS

    def to_dict(self) -> dict[str, str | bytes]:
        """
        将Account转换为字典

        Returns:
            dict[str, str | bytes]: 包含用户参数的字典
        """

        dic = {}

        for key in self.__serialize__:
            value = getattr(self, key)
            if not value:
                continue
            key = key[1:]
            dic[key] = value

        return dic

    @classmethod
    def from_dict(cls, dic: dict[str, str | bytes]) -> Self:
        """
        将字典转换为Account

        Args:
            dic (Dict[str, str | bytes]): 包含用户参数的字典

        Returns:
            Account: 用户参数容器
        """

        account = cls()

        for key, value in dic.items():
            if not value:
                continue
            key = "_" + key
            setattr(account, key, value)

        return account

    @property
    def BDUSS(self) -> str:
        """
        当前账号的BDUSS

        Returns:
            str: 当前账号的BDUSS
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

        Returns:
            str: 当前账号的STOKEN
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
            self._android_id = random.randbytes(8).hex()
        return self._android_id

    @android_id.setter
    def android_id(self, new_android_id: str) -> None:
        self._android_id = new_android_id

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

    @uuid.setter
    def uuid(self, new_uuid: str) -> None:
        self._uuid = new_uuid

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

    @tbs.setter
    def tbs(self, new_tbs: str) -> None:
        self._tbs = new_tbs

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

    @client_id.setter
    def client_id(self, new_client_id: str) -> None:
        self._client_id = new_client_id

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

    @sample_id.setter
    def sample_id(self, new_sample_id: str) -> None:
        self._sample_id = new_sample_id

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

    @cuid.setter
    def cuid(self, new_cuid: str) -> None:
        self._cuid = new_cuid

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

    @cuid_galaxy2.setter
    def cuid_galaxy2(self, new_cuid_galaxy2: str) -> None:
        self._cuid_galaxy2 = new_cuid_galaxy2

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

    @c3_aid.setter
    def c3_aid(self, new_c3_aid: str) -> None:
        self._c3_aid = new_c3_aid

    @property
    def baidu_id(self) -> str:
        """
        返回一个可作为请求参数的baidu_id

        Returns:
            str

        Examples:
            1A2B3C4D5E6F708192A3B4C5D6E7F809:FG=1

        Note:
            在初始化后该属性便不会再发生变化
        """

        return self._baidu_id

    @baidu_id.setter
    def baidu_id(self, new_baidu_id: str) -> None:
        self._baidu_id = new_baidu_id

    @property
    def zid(self) -> str:
        """
        返回一个可作为请求参数的zid

        Returns:
            str

        Note:
            在初始化后该属性便不会再发生变化\n
            此实现与12.x版本及以前的官方实现一致
        """

        return self._zid

    @zid.setter
    def zid(self, new_zid: str) -> None:
        self._zid = new_zid

    @property
    def ws_sec_key(self) -> bytes:
        """
        返回一个供贴吧websocket加密使用的随机密码

        Returns:
            bytes: 长度为31字节的随机密码

        Note:
            在初始化后该属性便不会再发生变化
        """

        if self._ws_sec_key is None:
            self._ws_sec_key = random.randbytes(31)
        return self._ws_sec_key

    @ws_sec_key.setter
    def ws_sec_key(self, new_ws_sec_key: bytes) -> None:
        self._ws_sec_key = new_ws_sec_key

    @property
    def zid_sec_key(self) -> bytes:
        """
        返回一个供贴吧zid加密使用的随机密码

        Returns:
            bytes: 长度为16字节的随机密码

        Note:
            在初始化后该属性便不会再发生变化
        """

        if self._zid_sec_key is None:
            self._zid_sec_key = random.randbytes(16)
        return self._zid_sec_key

    @zid_sec_key.setter
    def zid_sec_key(self, new_zid_sec_key: bytes) -> None:
        self._zid_sec_key = new_zid_sec_key
