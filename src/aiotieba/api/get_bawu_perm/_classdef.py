from __future__ import annotations

import dataclasses as dcs
from datetime import datetime
from typing import TYPE_CHECKING, Self

from ...enums import BawuPermType, BawuType
from ...exception import TbErrorExt
from ...helper import default_datetime

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class UserInfo_perm:
    """
    吧务权限查询的目标用户

    Attributes:
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称
        level (int): 吧内等级

        bawu_type (BawuType): 吧务类型
        begin_time (datetime): 上任时间
    """

    user_name: str = ""
    nick_name_old: str = ""
    level: int = 0

    bawu_type: BawuType = BawuType.UNKNOWN
    begin_time: datetime = dcs.field(default_factory=default_datetime)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user_name = data_map["user_name"]
        nick_name_old = data_map["user_nickname"]
        level = data_map["level_id"]

        bawu_type = BawuType(data_map["role_type"])

        if create_time := data_map["create_time"]:
            begin_time = datetime.fromtimestamp(create_time)
        else:
            begin_time = default_datetime()

        return cls(user_name, nick_name_old, level, bawu_type, begin_time)


@dcs.dataclass
class BawuPerm(TbErrorExt):
    """
    吧务已分配的权限

    Attributes:
        err (Exception | None): 捕获的异常
        user (UserInfo_perm): 目标用户
        perms (BawuPermType): 吧务已分配的权限
    """

    user: UserInfo_perm = dcs.field(default_factory=UserInfo_perm)
    perms: BawuPermType = BawuPermType.NULL

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user = UserInfo_perm.from_json(data_map["user"])

        perms = BawuPermType.NULL

        for cate in ["category_user", "category_thread"]:
            perm_setting = data_map["perm_setting"]
            for perm_setting_item in perm_setting[cate]:
                if not perm_setting_item["switch"]:
                    continue

                perm_idx: int = perm_setting_item["perm"] - 2
                perm = [
                    BawuPermType.RECOVER_APPEAL,
                    BawuPermType.RECOVER,
                    BawuPermType.UNBLOCK,
                    BawuPermType.UNBLOCK_APPEAL,
                ][perm_idx]

                perms |= perm

        return cls(user, perms)
