from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

import bs4

from ...exception import TbErrorExt
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class BawuBlacklistUser:
    """
    吧务黑名单用户

    Attributes:
        user_id (int): user_id
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称
        op_user_name (str): 操作人用户名

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    user_name: str = ""
    nick_name_old: str = ""
    op_user_name: str = ""

    @classmethod
    def from_xml(cls, data_tag: bs4.element.Tag) -> Self:
        user_item = data_tag.a
        user_id = int(user_item["attr-uid"])
        user_name = user_item["attr-un"]
        nick_name_old = user_item["attr-nn"]
        op_user_name_item = data_tag.find("span", class_="black_list_item_operate_name")
        op_user_name = op_user_name_item.get_text(strip=True).removeprefix("操作人：").rsplit("】", 1)[-1]
        return cls(user_id, user_name, nick_name_old, op_user_name)

    def __str__(self) -> str:
        return self.user_name or str(self.user_id)

    def __eq__(self, obj: BawuBlacklistUser) -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_old

    @property
    def show_name(self) -> str:
        return self.nick_name_old or self.user_name

    @property
    def log_name(self) -> str:
        return str(self)


@dcs.dataclass
class Page_bwblacklist:
    """
    页信息

    Attributes:
        page_size (int): 页大小
        current_page (int): 当前页码
        total_page (int): 总页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    page_size: int = 0
    current_page: int = 0
    total_page: int = 0
    total_count: int = 0

    has_more: bool = False
    has_prev: bool = False

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        page_size = data_map["size"]
        current_page = data_map["pn"]
        total_page = data_map["total_page"]
        total_count = data_map["total_count"]
        has_more = data_map["have_next"]
        has_prev = current_page > 1
        return cls(page_size, current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class BawuBlacklistUsers(TbErrorExt, Containers[BawuBlacklistUser]):
    """
    吧务黑名单列表

    Attributes:
        objs (list[BawuBlacklistUser]): 吧务黑名单列表
        err (Exception | None): 捕获的异常

        page (Page_bwblacklist): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_bwblacklist = dcs.field(default_factory=Page_bwblacklist)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        data_soup = bs4.BeautifulSoup(data_map["data"]["content"], "lxml")
        objs = [BawuBlacklistUser.from_xml(t) for t in data_soup("li")]
        page = Page_bwblacklist.from_json(data_map["data"]["page"])
        return cls(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
