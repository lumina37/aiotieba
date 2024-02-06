import dataclasses as dcs
from functools import cached_property

from ...enums import Gender
from ...exception import TbErrorExt
from .._classdef import TypeMessage


@dcs.dataclass
class UserInfo_guinfo_app(TbErrorExt):
    """
    用户信息

    Attributes:
        err (Exception | None): 捕获的异常

        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称

        gender (Gender): 性别

        is_vip (bool): 是否超级会员
        is_god (bool): 是否大神

        nick_name (str): 用户昵称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name_old: str = ''

    gender: Gender = Gender.UNKNOWN

    is_vip: bool = False
    is_god: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_guinfo_app":
        user_id = data_proto.id
        portrait = data_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.name
        nick_name_old = data_proto.name_show
        gender = Gender(data_proto.sex)
        is_vip = bool(data_proto.vipInfo.v_status)
        is_god = bool(data_proto.new_god_data.status)
        return UserInfo_guinfo_app(user_id, portrait, user_name, nick_name_old, gender, is_vip, is_god)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_guinfo_app") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_old

    @cached_property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_old}/{self.portrait}"
        else:
            return str(self.user_id)
