import dataclasses as dcs
from typing import Mapping

from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class FollowForum:
    """
    关注吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        level (int): 用户等级
        exp (int): 经验值
    """

    fid: int = 0
    fname: str = ''
    level: int = 0
    exp: int = 0

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "FollowForum":
        fid = int(data_map['id'])
        fname = data_map['name']
        level = int(data_map['level_id'])
        exp = int(data_map['cur_score'])
        return FollowForum(fid, fname, level, exp)

    def __eq__(self, obj: "FollowForum") -> bool:
        return self.fid == obj.fid

    def __hash__(self) -> int:
        return self.fid


@dcs.dataclass
class FollowForums(TbErrorExt, Containers[FollowForum]):
    """
    用户关注贴吧列表

    Attributes:
        objs (list[Forum]): 用户关注贴吧列表
        err (Exception | None): 捕获的异常

        has_more (bool): 是否还有下一页
    """

    has_more: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "FollowForums":
        if forum_list := data_map.get('forum_list', {}):
            forum_dicts = forum_list.get('non-gconforum', [])
            objs = [FollowForum.from_tbdata(m) for m in forum_dicts]
            forum_dicts = forum_list.get('gconforum', [])
            objs += [FollowForum.from_tbdata(m) for m in forum_dicts]
            has_more = bool(int(data_map['has_more']))
        else:
            objs = []
            has_more = False

        return FollowForums(objs, has_more)
