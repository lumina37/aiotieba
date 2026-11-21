from __future__ import annotations

import dataclasses as dcs
from datetime import datetime
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from ...helper import default_datetime
from ...helper.parse import text_of
from .._classdef import Containers
from .._classdef.contents import _IMAGEHASH_EXP

if TYPE_CHECKING:
    from lxml import etree


@dcs.dataclass
class Media_postlog:
    """
    媒体信息

    Attributes:
        src (str): 小图链接
        origin_src (str): 原图链接
        hash (str): 百度图床hash
    """

    src: str = dcs.field(default="", repr=False)
    origin_src: str = dcs.field(default="", repr=False)
    hash: str = ""

    @classmethod
    def from_xml(cls, data_tag: etree._Element) -> Self:
        img_items = data_tag.xpath(".//img")
        if img_items:
            src = img_items[0].get("original")
            hash_ = _IMAGEHASH_EXP.search(src).group(1)
        else:
            src = ""
            hash_ = ""
        origin_src = data_tag.get("href")
        return cls(src, origin_src, hash_)


@dcs.dataclass
class BawuPostLog:
    """
    吧务帖子管理日志

    Attributes:
        text (str): 文本内容
        title (str): 所在主题帖标题
        medias (list[Media_postlog]): 媒体列表

        tid (int): 所在主题帖id
        pid (int): 回复id

        op_type (str): 操作类型
        post_portrait (str): 发帖用户的portrait
        post_time (datetime): 发帖时间 不含年份
        op_user_name (str): 操作人用户名
        op_time (datetime): 操作时间
    """

    text: str = ""
    title: str = ""
    medias: list[Media_postlog] = dcs.field(default_factory=list)

    tid: int = 0
    pid: int = 0

    op_type: str = ""
    post_portrait: str = ""
    post_time: datetime = dcs.field(default_factory=default_datetime)
    op_user_name: str = ""
    op_time: datetime = dcs.field(default_factory=default_datetime)

    @classmethod
    def from_xml(cls, data_tag: etree._Element) -> Self:
        tds = data_tag.xpath("./td")
        left_cell_item = tds[0]

        post_meta_item = left_cell_item.xpath(
            './/div[contains(concat(" ", normalize-space(@class), " "), " post_meta ")]'
        )[0]
        post_user_item = post_meta_item.xpath("./div")[0]
        post_portrait = post_user_item.xpath("./a")[0].get("href")[14:-17]
        post_time_item = post_meta_item.xpath("./time")[0]
        post_time_str = text_of(post_time_item)
        post_time_month = int(post_time_str[:2])
        post_time_day = int(post_time_str[3:5])
        post_time_hour = int(post_time_str[7:9])
        post_time_minute = int(post_time_str[10:])
        post_time = datetime(1904, post_time_month, post_time_day, post_time_hour, post_time_minute)

        post_content_item = post_meta_item.getnext()
        title_item = post_content_item.xpath("./h1/a")[0]
        url: str = title_item.get("href")
        tid = int(url[3 : url.find("?")])
        pid = int(url[url.rfind("#") + 1 :])
        title: str = title_item.get("title")

        text_item = post_content_item.xpath("./div")[0]
        text = text_of(text_item)[12:]

        if pid == tid or not title.startswith("回复："):
            # is thread
            pid = 0
            text = f"{title}\n{text}"
        else:
            title = title.removeprefix("回复：")

        media_list_item = text_item.getnext()
        if media_list_item is not None:
            medias = [Media_postlog.from_xml(tag) for tag in media_list_item.xpath(".//a")]
        else:
            medias = []

        op_type_item = tds[1]
        op_type = text_of(op_type_item).strip()

        op_user_name_item = tds[2]
        op_user_name = text_of(op_user_name_item).strip()

        op_time_item = tds[3]
        op_time = datetime.strptime(text_of(op_time_item).strip(), "%Y-%m-%d%H:%M")

        return cls(text, title, medias, tid, pid, op_type, post_portrait, post_time, op_user_name, op_time)


@dcs.dataclass
class Page_postlog:
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
class BawuPostLogs(TbErrorExt, Containers[BawuPostLog]):
    """
    吧务帖子管理日志表

    Attributes:
        objs (list[BawuPostLog]): 吧务帖子管理日志表
        err (Exception | None): 捕获的异常

        page (Page_postlog): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_postlog = dcs.field(default_factory=Page_postlog)

    @classmethod
    def from_xml(cls, data_soup: etree._Element) -> Self:
        tbody = data_soup.xpath("//tbody")[0]
        objs = [BawuPostLog.from_xml(t) for t in tbody.xpath(".//tr")]
        page = Page_postlog.from_xml(data_soup)
        return cls(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
