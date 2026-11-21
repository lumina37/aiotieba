from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from ...helper.parse import class_tokens, text_of
from .._classdef import Containers

if TYPE_CHECKING:
    from lxml import etree


@dcs.dataclass
class RankForum:
    """
    吧签到排名

    Attributes:
        fname (str): 吧名

        sign_num (int): 签到用户数
        member_num (int): 总用户数

        has_bawu (bool): 是否有吧务
    """

    fname: str = ""

    sign_num: int = 0
    member_num: int = 0

    has_bawu: bool = False

    @classmethod
    def from_xml(cls, data_tag: etree._Element) -> Self:
        tds = data_tag.xpath("./td")
        fname = text_of(tds[1])
        sign_num = int(text_of(tds[2]))
        member_num = int(text_of(tds[3]))
        manager_item = data_tag.xpath('./td[contains(concat(" ", normalize-space(@class), " "), " clearfix ")]')[0]
        manager_status_item = manager_item.xpath("./div")[0]
        has_bawu = class_tokens(manager_status_item)[0] != "no_bawu"
        return cls(fname, sign_num, member_num, has_bawu)


@dcs.dataclass
class Page_rankforum:
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
    def from_xml(cls, data_soup: etree._Element) -> Self:
        pages_item = data_soup.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " pagination ")]')[0]
        current_page = int(text_of(pages_item.xpath("./span")[0]))
        total_page_item = pages_item.xpath("./a")[-1]
        total_page_url: str = total_page_item.get("href")
        total_page_str = total_page_url[total_page_url.rfind("pn=") + 3 :]
        total_page = int(total_page_str)
        has_more = current_page < total_page
        has_prev = current_page > 1

        return cls(current_page, total_page, has_more, has_prev)


@dcs.dataclass
class RankForums(TbErrorExt, Containers[RankForum]):
    """
    吧签到排名表

    Attributes:
        objs (list[RankForum]): 吧签到排名表
        err (Exception | None): 捕获的异常

        page (Page_rankforum): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_rankforum = dcs.field(default_factory=Page_rankforum)

    @classmethod
    def from_xml(cls, data_soup: etree._Element) -> Self:
        rank_table = data_soup.xpath("//table")[0]
        objs = [
            RankForum.from_xml(t)
            for t in rank_table.xpath('.//tr[contains(concat(" ", normalize-space(@class), " "), " j_rank_row ")]')
        ]
        page = Page_rankforum.from_xml(data_soup)
        return cls(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
