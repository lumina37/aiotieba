from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING

from ...exception import TbErrorExt
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class PcFollowForum:
    """
    关注吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        level (int): 用户等级
    """

    fid: int = 0
    fname: str = ""
    level: int = 0

    @staticmethod
    def from_json(data_map: Mapping) -> PcFollowForum:
        fid = data_map["forum_id"]
        fname = data_map["forum_name"]
        level = data_map["level_id"]
        return PcFollowForum(fid, fname, level)

    def __eq__(self, obj: PcFollowForum) -> bool:
        return self.fid == obj.fid

    def __hash__(self) -> int:
        return self.fid


@dcs.dataclass
class PcFollowForums(TbErrorExt, Containers[PcFollowForum]):
    """
    用户关注贴吧列表

    Attributes:
        objs (list[PcFollowForum]): 用户关注贴吧列表
        err (Exception | None): 捕获的异常

        has_more (bool): 是否还有下一页
    """

    has_more: bool = False

    @staticmethod
    def from_json(data_map: Mapping) -> PcFollowForums:
        objs = [PcFollowForum.from_json(m) for m in data_map["like"]]
        has_more = bool(data_map["has_more"])
        return PcFollowForums(objs, has_more)
