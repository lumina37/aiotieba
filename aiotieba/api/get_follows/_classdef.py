import dataclasses as dcs
from functools import cached_property
from typing import Mapping

from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class Follow:
    """
    用户信息

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
    portrait: str = ''
    user_name: str = ''
    nick_name_new: str = ''

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Follow":
        user_id = int(data_map['id'])
        portrait = data_map['portrait']
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_map['name']
        nick_name_new = data_map['name_show']
        return Follow(user_id, portrait, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "Follow") -> bool:
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
class Page_follow:
    """
    页信息

    Attributes:
        current_page (int): 当前页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    current_page: int = 0
    total_count: int = 0

    has_more: bool = False
    has_prev: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Page_follow":
        current_page = int(data_map['pn'])
        total_count = int(data_map['total_follow_num'])
        has_more = bool(int(data_map['has_more']))
        has_prev = current_page > 1
        return Page_follow(current_page, total_count, has_more, has_prev)


@dcs.dataclass
class Follows(TbErrorExt, Containers[Follow]):
    """
    粉丝列表

    Attributes:
        objs (list[Follow]): 粉丝列表
        err (Exception | None): 捕获的异常

        page (Page_follow): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_follow = dcs.field(default_factory=Page_follow)

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Follows":
        objs = [Follow.from_tbdata(m) for m in data_map['follow_list']]
        page = Page_follow.from_tbdata(data_map)
        return Follows(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
