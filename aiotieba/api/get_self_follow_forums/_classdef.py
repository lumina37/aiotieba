from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING

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
    """

    fid: int = 0
    fname: str = ""
    level: int = 0
    is_signed: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> SelfFollowForum:
        fid = data_map["forum_id"]
        fname = data_map["forum_name"]
        level = data_map["level_id"]
        is_signed = data_map["is_sign"]
        return SelfFollowForum(fid, fname, level, is_signed)


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
    def from_tbdata(data_map: Mapping) -> SelfFollowForums:
        objs = [SelfFollowForum.from_tbdata(m) for m in data_map["like_forum"]]
        has_more = data_map["like_forum_has_more"]
        return SelfFollowForums(objs, has_more)
