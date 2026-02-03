from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING

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

    @staticmethod
    def from_tbdata(data_map: Mapping) -> UserInfo_uf:
        show_name = data_map.get("name", "")
        user_id = int(data_map.get("id", 0) or 0)
        portrait = data_map.get("portrait", "")
        if "?" in portrait:
            portrait = portrait.split("?", 1)[0]
        is_like = bool(int(data_map.get("is_like", 0) or 0))
        return UserInfo_uf(user_id, portrait, show_name, is_like)

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
        member_rank (int): 吧内排名
        day_sign_rank (int): 今日签到排名
        level (int): 等级
        level_name (str): 本吧头衔名称
        exp (int): 当前经验
        levelup_exp (int): 升级经验
        role_name (str): 吧务名称
        identify (str): 身份标识
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
    member_rank: int = 0
    day_sign_rank: int = 0
    level: int = 0
    level_name: str = ""
    exp: int = 0
    levelup_exp: int = 0
    role_name: str = ""
    identify: str = ""
    high_light_sign_days: int = 0

    @staticmethod
    def from_tbdata(data_map: Mapping) -> UserForumInfo:
        user = UserInfo_uf.from_tbdata(data_map.get("user_info", {}))
        user_forum = data_map.get("user_forum_info", {})
        forum = data_map.get("forum_info", {})
        return UserForumInfo(
            user=user,
            is_follow=bool(int(user_forum.get("is_follow", 0) or 0)),
            follow_days=int(user_forum.get("follow_days", 0) or 0),
            sign_days=int(user_forum.get("sign_days", 0) or 0),
            thread_num=int(user_forum.get("thread_num", 0) or 0),
            day_post_num=int(user_forum.get("day_post_num", 0) or 0),
            member_rank=int(user_forum.get("member_no", 0) or 0),
            day_sign_rank=int(user_forum.get("day_sign_no", 0) or 0),
            level=int(user_forum.get("level_id", 0) or 0),
            level_name=user_forum.get("level_name", ""),
            exp=int(user_forum.get("cur_score", 0) or 0),
            levelup_exp=int(user_forum.get("levelup_score", 0) or 0),
            role_name=user_forum.get("role_name", ""),
            identify=user_forum.get("identify", ""),
            high_light_sign_days=int(user_forum.get("high_light_sign_days", 0) or 0),
            fname=forum.get("forum_name", ""),
            small_avatar=forum.get("forum_avatar", ""),
        )
