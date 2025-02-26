from __future__ import annotations

import dataclasses as dcs
from functools import cached_property

from ...exception import TbErrorExt
from .._classdef import Containers, TypeMessage


@dcs.dataclass
class Page_lp:
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
    def from_tbdata(data_proto: TypeMessage) -> Page_lp:
        page_size = data_proto.page_size
        current_page = data_proto.current_page
        total_page = data_proto.total_page
        total_count = data_proto.total_count
        has_more = bool(data_proto.has_more)
        has_prev = bool(data_proto.has_prev)
        return Page_lp(page_size, current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class UserInfo_lp:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ""
    user_name: str = ""
    nick_name_old: str = ""

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> UserInfo_lp:
        user_id = data_proto.id
        portrait = data_proto.portrait
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.name
        nick_name_old = data_proto.name_show
        return UserInfo_lp(user_id, portrait, user_name, nick_name_old)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: UserInfo_lp) -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_old

    @property
    def show_name(self) -> str:
        return self.nick_name_old or self.user_name

    @cached_property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_old}/{self.portrait}"
        else:
            return str(self.user_id)


@dcs.dataclass
class LastReplyer:
    """
    最后回复者的用户信息

    Attributes:
        user_id (int): user_id
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    user_name: str = ""
    nick_name_old: str = ""

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> LastReplyer:
        user_id = data_proto.id
        user_name = data_proto.name
        nick_name_old = data_proto.name_show
        return LastReplyer(user_id, user_name, nick_name_old)

    def __str__(self) -> str:
        return self.user_name or str(self.user_id)

    def __eq__(self, obj: LastReplyer) -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_old

    @property
    def show_name(self) -> str:
        return self.nick_name_old or self.user_name

    @cached_property
    def log_name(self) -> str:
        return self.user_name or str(self.user_id)


@dcs.dataclass
class Thread_lp:
    """
    主题帖信息

    Attributes:
        text (str): 文本内容
        title (str): 标题内容

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼回复pid
        user (UserInfo_lp): 发布者的用户信息
        author_id (int): 发布者的user_id
        last_replyer (LastReplyer): 最后回复者的用户信息

        create_time (int): 创建时间 10位时间戳 以秒为单位
        last_time (int): 最后回复时间 10位时间戳 以秒为单位
    """

    title: str = ""

    fid: int = 0
    fname: str = ""
    tid: int = 0
    pid: int = 0
    user: UserInfo_lp = dcs.field(default_factory=UserInfo_lp)
    last_replyer: LastReplyer = dcs.field(default_factory=LastReplyer)

    create_time: int = 0
    last_time: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> None:
        title = data_proto.title
        tid = data_proto.id
        pid = data_proto.first_post_id
        user = UserInfo_lp.from_tbdata(data_proto.author)
        last_replyer = LastReplyer.from_tbdata(data_proto.last_replyer)
        create_time = data_proto.create_time
        last_time = data_proto.last_time_int
        return Thread_lp(title, 0, "", tid, pid, user, last_replyer, create_time, last_time)

    def __eq__(self, obj: Thread_lp) -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @property
    def text(self) -> str:
        return self.title

    @property
    def author_id(self) -> int:
        return self.user.user_id


@dcs.dataclass
class Forum_lp:
    """
    吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名
    """

    fid: int = 0
    fname: str = ""

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> Forum_lp:
        forum_proto = data_proto.forum
        fid = forum_proto.id
        fname = forum_proto.name
        return Forum_lp(fid, fname)


@dcs.dataclass
class Threads_lp(TbErrorExt, Containers[Thread_lp]):
    """
    主题帖列表

    Attributes:
        objs (list[Thread_lp]): 主题帖列表
        err (Exception | None): 捕获的异常

        page (Page_lp): 页信息
        has_more (bool): 是否还有下一页

        forum (Forum_lp): 所在吧信息
    """

    page: Page_lp = dcs.field(default_factory=Page_lp)
    forum: Forum_lp = dcs.field(default_factory=Forum_lp)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> Threads_lp:
        page = Page_lp.from_tbdata(data_proto.page)
        forum = Forum_lp.from_tbdata(data_proto)

        objs = [Thread_lp.from_tbdata(p) for p in data_proto.thread_list]
        for thread in objs:
            thread.fname = forum.fname
            thread.fid = forum.fid

        return Threads_lp(objs, page, forum)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
