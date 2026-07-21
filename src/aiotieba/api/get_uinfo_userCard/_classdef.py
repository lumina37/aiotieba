from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import TYPE_CHECKING, Self

from ...enums import Gender
from ...exception import TbErrorExt

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class UserInfo_uc(TbErrorExt):
    """
    用户信息

    Attributes:
        err (Exception | None): 捕获的异常

        portrait (str): portrait
        nick_name_new (str): 新版昵称
        tieba_uid (int): 用户个人主页uid

        gender (Gender): 性别
        age (float): 吧龄 以年为单位
        agree_num (int): 获赞数
        fan_num (int): 粉丝数
        follow_num (int): 关注数
        sign (str): 个性签名
        ip (str): ip归属地

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    portrait: str = ""
    nick_name_new: str = ""
    tieba_uid: int = 0

    gender: Gender = Gender.UNKNOWN
    age: float = 0.0
    agree_num: int = 0
    fan_num: int = 0
    follow_num: int = 0
    sign: str = ""
    ip: str = ""

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        nick_name_new = data_map["name_show"]
        tieba_uid = int(data_map["tieba_uid"])
        gender = Gender(data_map["sex"])
        age = float(data_map["tb_age"])
        agree_num = data_map["total_agree_num"]
        fan_num = data_map["fans_num"]
        follow_num = data_map["concern_num"]
        sign = data_map["intro"]
        ip = data_map["ip_address"]

        return UserInfo_uc(portrait, nick_name_new, tieba_uid, gender, age, agree_num, fan_num, follow_num, sign, ip)

    def __str__(self) -> str:
        return self.nick_name_new or self.portrait

    def __eq__(self, obj: UserInfo_uc) -> bool:
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
        return self.nick_name_new

    @cached_property
    def log_name(self) -> str:
        if self.nick_name_new:
            return self.nick_name_new
        else:
            return self.portrait
