import dataclasses as dcs
from typing import Mapping

from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class SelfFollowForum:
    """
    吧基本信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名
        level (int): 用户等级
    """

    fid: int = 0
    fname: str = ''
    level: int = 0

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "SelfFollowForum":
        fid = data_map['forum_id']
        fname = data_map['forum_name']
        level = data_map['level_id']
        return SelfFollowForum(fid, fname, level)


@dcs.dataclass
class Page_sforum:
    """
    页信息

    Attributes:
        current_page (int): 当前页码
        total_page (int): 总页码

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    current_page: int = 0
    total_page: int = 0

    has_more: bool = False
    has_prev: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Page_sforum":
        current_page = data_map['cur_page']
        total_page = data_map['total_page']
        has_more = current_page < total_page
        has_prev = current_page > 1
        return Page_sforum(current_page, total_page, has_more, has_prev)


@dcs.dataclass
class SelfFollowForums(TbErrorExt, Containers[SelfFollowForum]):
    """
    本账号关注贴吧列表

    Attributes:
        objs (list[SelfFollowForum]): 本账号关注贴吧列表
        err (Exception | None): 捕获的异常

        page (Page_sforum): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_sforum = dcs.field(default_factory=Page_sforum)

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "SelfFollowForums":
        objs = [SelfFollowForum.from_tbdata(m) for m in data_map['list']]
        page = Page_sforum.from_tbdata(data_map['page'])
        return SelfFollowForums(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
