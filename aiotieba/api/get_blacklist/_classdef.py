import dataclasses as dcs
from functools import cached_property
from typing import Dict, Mapping

from ...enums import BlacklistType
from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class BlacklistUser:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        btype (BlacklistType): 黑名单类型 FOLLOW禁止关注 INTERACT禁止互动 CHAT禁止私信

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name_new: str = ''

    btype: BlacklistType = BlacklistType.NULL

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "BlacklistUser":
        user_id = int(data_map['uid'])
        portrait = data_map['portrait']
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_map['user_name']
        nick_name_new = data_map['name_show']

        perm: Dict[str, str] = data_map['perm_list']
        btype = BlacklistType.NULL
        i = 1
        for flag in perm.values():
            if flag != '0':
                btype |= i
            i <<= 1
        btype = BlacklistType(btype)

        return BlacklistUser(user_id, portrait, user_name, nick_name_new, btype)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "BlacklistUser") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_new}/{self.portrait}"
        else:
            return str(self.user_id)


@dcs.dataclass
class BlacklistUsers(TbErrorExt, Containers[BlacklistUser]):
    """
    新版用户黑名单列表

    Attributes:
        objs (list[BlacklistUser]): 新版用户黑名单列表
        err (Exception | None): 捕获的异常
    """

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "BlacklistUsers":
        objs = [BlacklistUser.from_tbdata(m) for m in data_map.get('user_perm_list', [])]
        return BlacklistUsers(objs)
