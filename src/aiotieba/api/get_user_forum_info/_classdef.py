from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class UserInfo_uf:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        show_name (str): 显示名称
        is_like (bool): 是否已关注该用户
    """

    user_id: int = 0
    portrait: str = ""
    show_name: str = ""
    is_like: bool = False

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        show_name = data_map["name"]
        user_id = data_map["id"]
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        is_like = bool(data_map["is_like"])
        return cls(user_id, portrait, show_name, is_like)

    def __str__(self) -> str:
        return self.show_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, UserInfo_uf) and self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)


@dcs.dataclass
class UserForumInfo(TbErrorExt):
    """
    用户在吧内的信息

    Attributes:
        err (Exception | None): 捕获的异常

        user (UserInfo_uf): 用户信息

        fname (str): 贴吧名
        small_avatar (str): 吧头像(小)

        is_follow (bool): 是否已关注该吧
        follow_days (int): 关注天数
        sign_days (int): 签到天数
        thread_num (int): 本吧发帖数
        day_post_num (int): 今日发帖数
        day_sign_rank (int): 今日签到排名
        level (int): 等级
        level_name (str): 本吧头衔名称
        exp (int): 当前经验
        levelup_exp (int): 升级经验
        role_name (str): 吧务名称
        high_light_sign_days (int): 连续签到天数
    """

    user: UserInfo_uf = dcs.field(default_factory=UserInfo_uf)

    fname: str = ""
    small_avatar: str = ""

    is_follow: bool = False
    follow_days: int = 0
    sign_days: int = 0
    thread_num: int = 0
    day_post_num: int = 0
    day_sign_rank: int = 0
    level: int = 0
    level_name: str = ""
    exp: int = 0
    levelup_exp: int = 0
    role_name: str = ""
    high_light_sign_days: int = 0

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        # 本接口强制要求BDUSS可用 服务端必定下发user_info
        user = UserInfo_uf.from_json(data_map["user_info"])
        user_forum = data_map["user_forum_info"]
        forum = data_map["forum_info"]

        fname = forum["forum_name"]
        small_avatar = forum["forum_avatar"]

        is_follow = bool(user_forum["is_follow"])
        follow_days = user_forum["follow_days"]
        sign_days = user_forum["sign_days"]
        thread_num = user_forum["thread_num"]
        day_post_num = user_forum["day_post_num"]
        day_sign_rank = user_forum["day_sign_no"]
        level = user_forum["level_id"]
        level_name = user_forum["level_name"]
        exp = user_forum["cur_score"]
        levelup_exp = user_forum["levelup_score"]
        role_name = user_forum["role_name"]
        high_light_sign_days = user_forum["high_light_sign_days"]

        return cls(
            user,
            fname,
            small_avatar,
            is_follow,
            follow_days,
            sign_days,
            thread_num,
            day_post_num,
            day_sign_rank,
            level,
            level_name,
            exp,
            levelup_exp,
            role_name,
            high_light_sign_days,
        )
