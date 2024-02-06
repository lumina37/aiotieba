import dataclasses as dcs

from ...exception import TbErrorExt
from .._classdef import Containers, TypeMessage


@dcs.dataclass
class Page_dislikef:
    """
    页信息

    Attributes:
        current_page (int): 当前页码

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    current_page: int = 0

    has_more: bool = False
    has_prev: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Page_dislikef":
        current_page = data_proto.cur_page
        has_more = bool(data_proto.has_more)
        has_prev = current_page > 1
        return Page_dislikef(current_page, has_more, has_prev)


@dcs.dataclass
class DislikeForum:
    """
    吧广场贴吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        member_num (int): 吧会员数
        post_num (int): 发帖量
        thread_num (int): 主题帖数

        is_followed (bool): 是否已关注
    """

    fid: int = 0
    fname: str = ''

    member_num: int = 0
    post_num: int = 0
    thread_num: int = 0

    is_followed: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "DislikeForum":
        fid = data_proto.forum_id
        fname = data_proto.forum_name
        member_num = data_proto.member_count
        post_num = data_proto.post_num
        thread_num = data_proto.thread_num
        return DislikeForum(fid, fname, member_num, post_num, thread_num)

    def __eq__(self, obj: "DislikeForum") -> bool:
        return self.fid == obj.fid

    def __hash__(self) -> int:
        return self.fid


@dcs.dataclass
class DislikeForums(TbErrorExt, Containers[DislikeForum]):
    """
    首页推荐屏蔽的贴吧列表

    Attributes:
        objs (list[DislikeForum]): 首页推荐屏蔽的贴吧列表
        err (Exception | None): 捕获的异常

        page (Page_dislikef): 页信息
    """

    page: Page_dislikef = dcs.field(default_factory=Page_dislikef)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "DislikeForums":
        objs = [DislikeForum.from_tbdata(p) for p in data_proto.forum_list]
        page = Page_dislikef.from_tbdata(data_proto)
        return DislikeForums(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
