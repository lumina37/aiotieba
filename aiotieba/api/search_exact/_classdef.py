from __future__ import annotations

import dataclasses as dcs
from typing import Mapping

from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class ExactSearch:
    """
    搜索结果

    Attributes:
        text (str): 文本内容
        title (str): 标题

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        show_name (str): 发布者的显示名称

        is_comment (bool): 是否楼中楼
        create_time (int): 创建时间
    """

    text: str = ""
    title: str = ""

    fname: str = ''
    tid: int = 0
    pid: int = 0
    show_name: str = ''

    is_comment: bool = False
    create_time: int = 0

    @staticmethod
    def from_tbdata(data_map: Mapping) -> ExactSearch:
        text = data_map['content']
        title = data_map['title']
        fname = data_map['fname']
        tid = int(data_map['tid'])
        pid = int(data_map['pid'])
        show_name = data_map['author']["name_show"]
        is_comment = bool(int(data_map['is_floor']))
        create_time = int(data_map['time'])
        return ExactSearch(text, title, fname, tid, pid, show_name, is_comment, create_time)

    def __eq__(self, obj: ExactSearch) -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid


@dcs.dataclass
class Page_exsch:
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

    @staticmethod
    def from_tbdata(data_map: Mapping) -> Page_exsch:
        page_size = int(data_map["page_size"])
        current_page = int(data_map["current_page"])
        total_page = int(data_map["total_page"])
        total_count = int(data_map["total_count"])
        has_more = bool(int(data_map["has_more"]))
        has_prev = bool(int(data_map["has_prev"]))
        return Page_exsch(page_size, current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class ExactSearches(TbErrorExt, Containers[ExactSearch]):
    """
    搜索结果列表

    Attributes:
        objs (list[ExactSearch]): 搜索结果列表
        err (Exception | None): 捕获的异常

        page (Page_exsch): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_exsch = dcs.field(default_factory=Page_exsch)

    @staticmethod
    def from_tbdata(data_map: Mapping) -> ExactSearches:
        objs = [ExactSearch.from_tbdata(m) for m in data_map.get('post_list', [])]
        page = Page_exsch.from_tbdata(data_map['page'])
        return ExactSearches(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
