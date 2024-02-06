import dataclasses as dcs
from functools import cached_property
from typing import Mapping


@dcs.dataclass
class UserInfo_selfinit:
    """
    用户信息

    Attributes:
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称
        tieba_uid (int): 用户个人主页uid

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_name: str = ''
    nick_name_old: str = ''
    tieba_uid: int = 0

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "UserInfo_selfinit":
        user_name = data_map['user_name']
        nick_name_old = data_map['name_show']
        tieba_uid = data_map['tieba_uid']
        return UserInfo_selfinit(user_name, nick_name_old, tieba_uid)

    def __str__(self) -> str:
        return self.user_name

    def __eq__(self, obj: "UserInfo_selfinit") -> bool:
        return self.tieba_uid == obj.tieba_uid

    def __hash__(self) -> int:
        return self.tieba_uid

    def __bool__(self) -> bool:
        return bool(self.tieba_uid)

    @property
    def nick_name(self) -> str:
        return self.nick_name_old

    @cached_property
    def log_name(self) -> str:
        self.user_name if self.user_name else f"{self.nick_name_old}/{self.tieba_uid}"
