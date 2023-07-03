from typing import Dict, Mapping, Optional

from ...enums import BlacklistType
from .._classdef import Containers


class BlacklistUser(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        btype (BlacklistType): 黑名单类型

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
        '_nick_name_new',
        '_btype',
    ]

    def __init__(self, data_map: Mapping) -> None:
        self._user_id = int(data_map['uid'])
        if '?' in (portrait := data_map['portrait']):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_map['user_name']
        self._nick_name_new = data_map['name_show']

        perm: Dict[str, str] = data_map['perm_list']
        btype = BlacklistType.NULL
        i = 1
        for flag in perm.values():
            if flag != '0':
                btype |= i
            i <<= 1
        self._btype = BlacklistType(btype)

    def __str__(self) -> str:
        return self._user_name or self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'user_name': self._user_name,
                'portrait': self._portrait,
                'show_name': self.show_name,
                'btype': self._btype,
            }
        )

    def __eq__(self, obj: "BlacklistUser") -> bool:
        return self._user_id == obj._user_id

    def __hash__(self) -> int:
        return self._user_id

    def __int__(self) -> int:
        return self._user_id

    def __bool__(self) -> bool:
        return bool(self._user_id)

    @property
    def user_id(self) -> int:
        """
        用户user_id

        Note:
            唯一 不可变 不可为空\n
            请注意与用户个人页的tieba_uid区分
        """

        return self._user_id

    @property
    def portrait(self) -> str:
        """
        用户portrait

        Note:
            唯一 不可变 不可为空
        """

        return self._portrait

    @property
    def user_name(self) -> str:
        """
        用户名

        Note:
            唯一 可变 可为空\n
            请注意与用户昵称区分
        """

        return self._user_name

    @property
    def nick_name_new(self) -> str:
        """
        新版昵称
        """

        return self._nick_name_new

    @property
    def btype(self) -> BlacklistType:
        """
        黑名单类型

        Note:
            FOLLOW禁止关注 INTERACT禁止互动 CHAT禁止私信
        """

        return self._btype

    @property
    def nick_name(self) -> str:
        """
        用户昵称
        """

        return self._nick_name_new

    @property
    def show_name(self) -> str:
        """
        显示名称
        """

        return self._nick_name_new or self._user_name

    @property
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        if self._user_name:
            return self._user_name
        elif self._portrait:
            return f"{self._nick_name_new}/{self._portrait}"
        else:
            return str(self._user_id)


class BlacklistUsers(Containers[BlacklistUser]):
    """
    新版用户黑名单列表

    Attributes:
        _objs (list[BlacklistUser]): 新版用户黑名单列表
    """

    __slots__ = []

    def __init__(self, data_map: Optional[Mapping] = None) -> None:
        if data_map:
            self._objs = [BlacklistUser(m) for m in data_map.get('user_perm_list', [])]
        else:
            self._objs = []
