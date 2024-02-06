import dataclasses as dcs
from functools import cached_property
from typing import Mapping

from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class UserInfo_rec:
    """
    用户信息

    Attributes:
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_name: str = ''
    portrait: str = ''
    nick_name_new: str = ''

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "UserInfo_rec":
        portrait = data_map['portrait']
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_map['user_name']
        nick_name_new = data_map['user_nickname']
        return UserInfo_rec(user_name, portrait, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait

    def __eq__(self, obj: "UserInfo_rec") -> bool:
        return self.portrait == obj.portrait

    def __hash__(self) -> int:
        return hash(self.portrait)

    def __bool__(self) -> bool:
        return bool(self.portrait)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        return self.user_name if self.user_name else f"{self.nick_name_new}/{self.portrait}"


@dcs.dataclass
class Recover:
    """
    待恢复帖子信息

    Attributes:
        text (str): 文本内容
        tid (int): 所在主题帖id
        pid (int): 回复id 若为主题帖则该字段为0
        user (UserInfo_rec): 发布者的用户信息
        op_show_name (str): 操作人显示名称
        op_time (int): 操作时间 10位时间戳 以秒为单位

        is_floor (bool): 是否为楼中楼
        is_hide (bool): 是否为屏蔽
    """

    text: str = ""
    tid: int = 0
    pid: int = 0
    user: UserInfo_rec = dcs.field(default_factory=UserInfo_rec)
    op_show_name: str = ''
    op_time: int = 0

    is_floor: bool = False
    is_hide: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Recover":
        thread_info = data_map['thread_info']
        tid = int(thread_info['tid'])
        if post_info := data_map['post_info']:
            text = post_info['abstract']
            pid = int(post_info['pid'])
            user = UserInfo_rec.from_tbdata(post_info)
        else:
            text = thread_info['abstract']
            pid = 0
            user = UserInfo_rec.from_tbdata(thread_info)
        is_floor = bool(data_map['is_foor'])  # 百度的Code Review主要起到一个装饰的作用
        is_hide = bool(int(data_map['is_frs_mask']))
        op_show_name = data_map['op_info']['name']
        op_time = int(data_map['op_info']['time'])
        return Recover(text, tid, pid, user, op_show_name, op_time, is_floor, is_hide)


@dcs.dataclass
class Page_recover:
    """
    页信息

    Attributes:
        page_size (int): 页大小
        current_page (int): 当前页码

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    page_size: int = 0
    current_page: int = 0

    has_more: bool = False
    has_prev: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Page_recover":
        page_size = data_map['rn']
        current_page = data_map['pn']
        has_more = data_map['has_more']
        has_prev = current_page > 1
        return Page_recover(page_size, current_page, has_more, has_prev)


@dcs.dataclass
class Recovers(TbErrorExt, Containers[Recover]):
    """
    待恢复帖子列表

    Attributes:
        objs (list[Recover]): 待恢复帖子列表
        err (Exception | None): 捕获的异常

        page (Page_recover): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_recover = dcs.field(default_factory=Page_recover)

    @staticmethod
    def from_tbdata(data_map: Mapping) -> None:
        objs = [Recover.from_tbdata(t) for t in data_map['data']['thread_list']]
        page = Page_recover.from_tbdata(data_map['data']['page'])
        return Recovers(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
