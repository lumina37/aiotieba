from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import TYPE_CHECKING, Self

from ...enums import Gender
from ...exception import TbErrorExt
from ...helper import tbnum2int, vipinfo2bool

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class UserInfo_panel(TbErrorExt):
    """
    用户信息

    Attributes:
        err (Exception | None): 捕获的异常

        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称
        nick_name_old (str): 旧版昵称

        gender (Gender): 性别
        age (float): 吧龄
        post_num (int): 发帖数
        fan_num (int): 粉丝数

        is_vip (bool): 是否会员

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    portrait: str = ""
    user_name: str = ""
    nick_name_new: str = ""
    nick_name_old: str = ""

    gender: Gender = Gender.UNKNOWN
    age: float = 0.0
    post_num: int = 0
    fan_num: int = 0

    is_vip: bool = False

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_map["name"]
        nick_name_new = data_map["show_nickname"]
        nick_name_old = data_map["name_show"]

        sex = data_map["sex"]
        if sex == "male":
            gender = Gender.MALE
        elif sex == "female":
            gender = Gender.FEMALE
        else:
            gender = Gender.UNKNOWN

        if (tb_age := data_map["tb_age"]) != "-":
            age = float(tb_age)
        else:
            age = 0.0

        post_num = tbnum2int(data_map["post_num"], "万")
        fan_num = tbnum2int(data_map["followed_count"], "万")

        is_vip = vipinfo2bool(data_map.get("vipInfo"))

        return cls(portrait, user_name, nick_name_new, nick_name_old, gender, age, post_num, fan_num, is_vip)

    def __str__(self) -> str:
        return self.user_name or self.portrait

    def __eq__(self, obj: UserInfo_panel) -> bool:
        return self.portrait == obj.portrait

    def __hash__(self) -> int:
        return hash(self.portrait)

    def __bool__(self) -> bool:
        return bool(self.portrait)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        return self.user_name or f"{self.nick_name_new}/{self.portrait}"
