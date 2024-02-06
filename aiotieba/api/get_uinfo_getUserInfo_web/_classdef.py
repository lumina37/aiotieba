import dataclasses as dcs
from functools import cached_property
from typing import Mapping

from ...exception import TbErrorExt


@dcs.dataclass
class UserInfo_guinfo_web(TbErrorExt):
    """
    用户信息

    Attributes:
        err (Exception | None): 捕获的异常

        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name_new: str = ''

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "UserInfo_guinfo_web":
        user_id = data_map['uid']
        portrait = data_map['portrait']
        user_name = user_name if (user_name := data_map['uname']) != user_id else ''
        nick_name_new = data_map['show_nickname']
        return UserInfo_guinfo_web(user_id, portrait, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_guinfo_web") -> bool:
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
