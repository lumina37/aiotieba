from __future__ import annotations

import dataclasses as dcs
from datetime import datetime
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from ...helper import default_datetime
from ...helper.parse import text_of
from .._classdef import Containers

if TYPE_CHECKING:
    from lxml import etree


@dcs.dataclass
class BawuUserLog:
    """
    吧务用户管理日志

    Attributes:
        op_type (str): 操作类型
        op_duration (int): 操作作用时长
        user_portrait (str): 被操作用户的portrait
        op_user_name (str): 操作人用户名
        op_time (datetime.datetime): 操作时间
    """

    op_type: str = ""
    op_duration: int = 0
    user_portrait: str = ""
    op_user_name: str = ""
    op_time: datetime = dcs.field(default_factory=default_datetime)

    @classmethod
    def from_xml(cls, data_tag: etree._Element) -> Self:
        tds = data_tag.xpath("./td")

        user_item = tds[0].xpath("./a")[0]
        user_portrait = user_item.get("href")[14:-17]

        op_type = text_of(tds[2]).strip()

        op_duration = text_of(tds[3]).strip().replace(" ", "")
        op_duration = 0 if "天" not in op_duration else int(op_duration[:-1])

        op_user_name = text_of(tds[4]).strip()

        op_time = datetime.strptime(text_of(tds[5]).strip(), "%Y-%m-%d %H:%M")

        return cls(op_type, op_duration, user_portrait, op_user_name, op_time)


@dcs.dataclass
class Page_userlog:
    """
    页信息

    Attributes:
        current_page (int): 当前页码
        total_page (int): 总页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    current_page: int = 0
    total_page: int = 0
    total_count: int = 0

    has_more: bool = False
    has_prev: bool = False

    @classmethod
    def from_xml(cls, data_soup: etree._Element) -> Self:
        total_count_tag = data_soup.xpath(
            '//div[contains(concat(" ", normalize-space(@class), " "), " breadcrumbs ")]'
        )[0]
        total_count = int(text_of(total_count_tag.xpath(".//em")[0]))

        page_tag_list = data_soup.xpath(
            '//div[contains(concat(" ", normalize-space(@class), " "), " tbui_pagination ")]'
            '//li[contains(concat(" ", normalize-space(@class), " "), " active ")]'
        )
        if not page_tag_list:
            if total_count != 0:
                current_page = 1
                total_page = 1
            else:
                current_page = 0
                total_page = 0
        else:
            page_tag = page_tag_list[0]
            current_page = int(text_of(page_tag))
            total_page_item = page_tag.getparent().getnext()
            total_page = int(text_of(total_page_item)[1:-1])

        has_more = current_page < total_page
        has_prev = current_page > 1

        return cls(current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class BawuUserLogs(TbErrorExt, Containers[BawuUserLog]):
    """
    吧务用户管理日志表

    Attributes:
        objs (list[BawuUserLog]): 吧务用户管理日志表
        err (Exception | None): 捕获的异常

        page (Page_userlog): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_userlog = dcs.field(default_factory=Page_userlog)

    @classmethod
    def from_xml(cls, data_soup: etree._Element) -> Self:
        tbody = data_soup.xpath("//tbody")[0]
        objs = [BawuUserLog.from_xml(t) for t in tbody.xpath(".//tr")]
        page = Page_userlog.from_xml(data_soup)
        return cls(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
