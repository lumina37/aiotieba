from __future__ import annotations

import dataclasses as dcs
import json
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from ...helper.parse import class_tokens, text_of
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping

    from lxml import etree


@dcs.dataclass
class RankUser:
    """
    等级排行榜用户信息

    Attributes:
        user_name (str): 用户名
        level (int): 等级
        exp (int): 经验值
        is_vip (bool): 是否会员
    """

    user_name: str = ""
    level: int = 0
    exp: int = 0
    is_vip: bool = False

    @classmethod
    def from_xml(cls, data_tag: etree._Element) -> Self:
        tds = data_tag.xpath("./td")
        user_name = text_of(tds[1])
        is_vip = "drl_item_vip" in class_tokens(tds[1].xpath("./div")[0])
        level_item = tds[2].xpath("./div")[0]
        # e.g. get level 16 from "bg_lv16" by slicing [5:]
        level = int(class_tokens(level_item)[0][5:])
        exp = int(text_of(tds[3]))
        return cls(user_name, level, exp, is_vip)


@dcs.dataclass
class Page_rank:
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

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        current_page = data_map["cur_page"]
        total_page = data_map["total_page"]
        has_more = current_page < total_page
        has_prev = current_page > 1
        return cls(current_page, total_page, has_more, has_prev)


@dcs.dataclass
class RankUsers(TbErrorExt, Containers[RankUser]):
    """
    等级排行榜用户列表

    Attributes:
        objs (list[RankUser]): 等级排行榜用户列表
        err (Exception | None): 捕获的异常

        page (Page_rank): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_rank = dcs.field(default_factory=Page_rank)

    @classmethod
    def from_xml(cls, data_soup: etree._Element) -> Self:
        objs = [RankUser.from_xml(t) for t in data_soup.xpath('//tr[contains(@class, "drl_list_item")]')]
        page_item = data_soup.xpath('//ul[contains(concat(" ", normalize-space(@class), " "), " p_rank_pager ")]')[0]
        page_dict = json.loads(page_item.get("data-field"))
        page = Page_rank.from_json(page_dict)
        return cls(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
