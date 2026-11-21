from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from ...helper.parse import class_tokens, text_of
from .._classdef import Containers

if TYPE_CHECKING:
    from lxml import etree


@dcs.dataclass
class MemberUser:
    """
    最新关注用户信息

    Attributes:
        user_name (str): 用户名
        portrait (str): portrait
        level (int): 等级
    """

    user_name: str = ""
    portrait: str = ""
    level: int = 0

    @classmethod
    def from_xml(cls, data_tag: etree._Element) -> Self:
        user_item = data_tag.xpath("./a")[0]
        user_name = user_item.get("title")
        portrait = user_item.get("href")[14:]
        level_item = data_tag.xpath("./span")[0]
        level = int(class_tokens(level_item)[1][12:])
        return cls(user_name, portrait, level)


@dcs.dataclass
class Page_member:
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
    def from_xml(cls, data_tag: etree._Element) -> Self:
        current_page = int(text_of(data_tag))
        total_page_item = data_tag.getparent().getnext()
        total_page = int(text_of(total_page_item)[1:-1])
        has_more = current_page < total_page
        has_prev = current_page > 1
        return cls(current_page, total_page, has_more, has_prev)


@dcs.dataclass
class MemberUsers(TbErrorExt, Containers[MemberUser]):
    """
    最新关注用户列表

    Attributes:
        objs (list[MemberUser]): 最新关注用户列表
        err (Exception | None): 捕获的异常

        page (Page_member): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_member = dcs.field(default_factory=Page_member)

    @classmethod
    def from_xml(cls, data_soup: etree._Element) -> Self:
        objs = [
            MemberUser.from_xml(t)
            for t in data_soup.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " name_wrap ")]')
        ]
        page_tag = data_soup.xpath(
            '//div[contains(concat(" ", normalize-space(@class), " "), " tbui_pagination ")]'
            '//li[contains(concat(" ", normalize-space(@class), " "), " active ")]'
        )[0]
        page = Page_member.from_xml(page_tag)
        return cls(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
