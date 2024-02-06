import dataclasses as dcs
from typing import Optional

from ...exception import TbErrorExt
from .._classdef import Containers, TypeMessage


@dcs.dataclass
class SquareForum:
    """
    吧广场贴吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        member_num (int): 吧会员数
        post_num (int): 发帖量

        is_followed (bool): 是否已关注
    """

    fid: int = 0
    fname: str = ''

    member_num: int = 0
    post_num: int = 0

    is_followed: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "SquareForum":
        fid = data_proto.forum_id
        fname = data_proto.forum_name
        member_num = data_proto.member_count
        post_num = data_proto.thread_count
        is_followed = bool(data_proto.is_like)
        return SquareForum(fid, fname, member_num, post_num, is_followed)

    def __eq__(self, obj: "SquareForum") -> bool:
        return self.fid == obj.fid

    def __hash__(self) -> int:
        return self.fid


@dcs.dataclass
class Page_square:
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
    def from_tbdata(data_proto: TypeMessage) -> "Page_square":
        page_size = data_proto.page_size
        current_page = data_proto.current_page
        total_page = data_proto.total_page
        total_count = data_proto.total_count
        has_more = bool(data_proto.has_more)
        has_prev = bool(data_proto.has_prev)
        return Page_square(page_size, current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class SquareForums(TbErrorExt, Containers[SquareForum]):
    """
    吧广场列表

    Attributes:
        objs (list[SquareForum]): 吧广场列表
        err (Exception | None): 捕获的异常

        page (Page_square): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_square = dcs.field(default_factory=Page_square)

    @staticmethod
    def from_tbdata(data_proto: Optional[TypeMessage] = None) -> None:
        objs = [SquareForum.from_tbdata(p) for p in data_proto.forum_info]
        page = Page_square.from_tbdata(data_proto.page)
        return SquareForums(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
