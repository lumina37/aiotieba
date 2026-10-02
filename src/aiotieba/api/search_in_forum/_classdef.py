from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from ...enums import ObjType
from ...exception import TbErrorExt
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class SearchInForum:
    """
    搜索结果

    Attributes:
        text (str): 文本内容
        title (str): 标题内容

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        ppid (int): 所在楼层id
        pid (int): 该条结果的回复id
        show_name (str): 发布者的显示名称

        obj_type (ObjType): 帖子对象类型
        create_time (int): 创建时间
    """

    text: str = ""
    title: str = ""

    fname: str = ""
    tid: int = 0
    ppid: int = 0
    pid: int = 0
    show_name: str = ""

    obj_type: ObjType = ObjType.UNKNOWN
    create_time: int = 0

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        text = data_map["content"]
        title = data_map["title"]
        fname = data_map["fname"]
        tid = int(data_map["tid"])
        is_comment = bool(int(data_map["is_floor"]))
        obj_type = ObjType.COMMENT if is_comment else ObjType.POST
        ppid = int(data_map["pid"])
        pid = int(data_map["cid"]) if is_comment else ppid
        show_name = data_map["author"]["name_show"]
        create_time = int(data_map["time"])
        return cls(text, title, fname, tid, ppid, pid, show_name, obj_type, create_time)

    def __eq__(self, obj: SearchInForum) -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid


@dcs.dataclass
class Page_fsch:
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
        page_size = int(data_map["page_size"])
        current_page = int(data_map["current_page"])
        total_page = int(data_map["total_page"])
        total_count = int(data_map["total_count"])
        has_more = bool(int(data_map["has_more"]))
        has_prev = bool(int(data_map["has_prev"]))
        return cls(page_size, current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class SearchInForums(TbErrorExt, Containers[SearchInForum]):
    """
    搜索结果列表

    Attributes:
        objs (list[SearchInForum]): 搜索结果列表
        err (Exception | None): 捕获的异常

        page (Page_fsch): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_fsch = dcs.field(default_factory=Page_fsch)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        objs = [SearchInForum.from_json(m) for m in data_map["post_list"]]
        page = Page_fsch.from_json(data_map["page"])
        return cls(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
