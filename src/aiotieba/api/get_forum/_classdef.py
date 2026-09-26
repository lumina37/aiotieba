from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class BawuInfo_f:
    """
    吧务信息

    该接口仅返回大吧主

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ""
    user_name: str = ""
    nick_name_new: str = ""

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        user_id = int(data_map.get("id", 0) or 0)
        portrait = data_map.get("portrait") or ""
        user_name = data_map.get("name") or ""
        nick_name_new = data_map.get("show_name") or ""
        return BawuInfo_f(user_id, portrait, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: BawuInfo_f) -> bool:
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
class Forum(TbErrorExt):
    """
    贴吧信息

    Attributes:
        err (Exception | None): 捕获的异常

        fid (int): 贴吧id
        fname (str): 贴吧名

        category (str): 一级分类
        subcategory (str): 二级分类

        small_avatar (str): 吧头像(小)
        slogan (str): 吧标语
        member_num (int): 吧会员数
        post_num (int): 发帖数
        thread_num (int): 主题帖数

        admins (list[BawuInfo_f]): 大吧主列表

        has_bawu (bool): 是否有吧务
    """

    fid: int = 0
    fname: str = ""

    category: str = ""
    subcategory: str = ""

    small_avatar: str = ""
    slogan: str = ""
    member_num: int = 0
    post_num: int = 0
    thread_num: int = 0

    admins: list[BawuInfo_f] = dcs.field(default_factory=list)

    has_bawu: bool = False

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        fid = data_map["id"]
        fname = data_map["name"]
        category = data_map["first_class"]
        subcategory = data_map["second_class"]
        small_avatar = data_map["avatar"]
        slogan = data_map["slogan"]
        member_num = data_map["member_num"]
        post_num = data_map["post_num"]
        thread_num = data_map["thread_num"]
        admins = [BawuInfo_f.from_json(m) for m in data_map.get("managers") or ()]
        has_bawu = "managers" in data_map
        return Forum(
            fid,
            fname,
            category,
            subcategory,
            small_avatar,
            slogan,
            member_num,
            post_num,
            thread_num,
            admins,
            has_bawu,
        )
