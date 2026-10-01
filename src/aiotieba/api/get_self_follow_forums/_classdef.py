from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class SelfFollowForum:
    """
    吧基本信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名
        level (int): 用户等级
        is_signed (bool): 是否已签到

        today_thread_num (int): 今日新帖数
        hot_num (int): 吧热度
        member_count (int): 关注数
        thread_num (int): 主题帖数
    """

    fid: int = 0
    fname: str = ""
    level: int = 0
    is_signed: bool = False

    today_thread_num: int = 0
    hot_num: int = 0
    member_count: int = 0
    thread_num: int = 0

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        fid = data_map["forum_id"]
        fname = data_map["forum_name"]
        level = data_map["level_id"]
        is_signed = bool(int(data_map["is_sign"]))

        today_thread_num = int(data_map.get("day_thread_num") or 0)
        hot_num = int(data_map.get("hot_num") or 0)
        member_count = int(data_map.get("member_count") or 0)
        thread_num = int(data_map.get("thread_num") or 0)

        return SelfFollowForum(fid, fname, level, is_signed, today_thread_num, hot_num, member_count, thread_num)


@dcs.dataclass
class SelfFollowForums(TbErrorExt, Containers[SelfFollowForum]):
    """
    本账号关注贴吧列表

    Attributes:
        objs (list[SelfFollowForum]): 本账号关注贴吧列表
        err (Exception | None): 捕获的异常

        has_more (bool): 是否还有下一页
    """

    has_more: bool = False

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        objs = [SelfFollowForum.from_json(m) for m in data_map["like_forum"]]
        has_more = data_map["like_forum_has_more"]
        return SelfFollowForums(objs, has_more)
