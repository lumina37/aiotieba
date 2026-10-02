from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import TYPE_CHECKING, Self

from ...enums import ContentType
from ...exception import TbErrorExt
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping


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

    user_name: str = ""
    portrait: str = ""
    nick_name_new: str = ""

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_map["user_name"]
        nick_name_new = data_map["user_nickname"]
        return cls(user_name, portrait, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait

    def __eq__(self, obj: UserInfo_rec) -> bool:
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
        return self.user_name or f"{self.nick_name_new}/{self.portrait}"


@dcs.dataclass
class Post_rec:
    """
    父级回复信息

    Attributes:
        pid (int): 父级回复id
        text (str): 文本内容
        user (UserInfo_rec): 发布者的用户信息
    """

    pid: int = 0
    text: str = ""
    user: UserInfo_rec = dcs.field(default_factory=UserInfo_rec)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        pid = int(data_map["pid"])
        text = data_map["abstract"]
        user = UserInfo_rec.from_json(data_map)
        return cls(pid, text, user)

    def __bool__(self) -> bool:
        return bool(self.pid)


@dcs.dataclass
class Thread_rec:
    """
    所在主题帖信息

    Attributes:
        tid (int): 主题帖id
        title (str): 标题
        text (str): 文本内容
        user (UserInfo_rec): 发布者的用户信息
    """

    tid: int = 0
    title: str = ""
    text: str = ""
    user: UserInfo_rec = dcs.field(default_factory=UserInfo_rec)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        tid = int(data_map["tid"])
        title = data_map["title"]
        text = data_map["abstract"]
        user = UserInfo_rec.from_json(data_map)
        return cls(tid, title, text, user)

    def __bool__(self) -> bool:
        return bool(self.tid)


@dcs.dataclass
class Recover:
    """
    待恢复帖子信息

    Attributes:
        text (str): 文本内容
        tid (int): 所在主题帖id
        pid (int): 待恢复对象的id 若`content_type`为`THREAD`则该字段为0
        user (UserInfo_rec): 待恢复对象的发布者用户信息
        post (Post_rec): 父级回复信息 仅`content_type`为`COMMENT`时有值
        thread (Thread_rec): 所在主题帖信息 当`content_type`为`THREAD`时即待恢复对象本身

        op_show_name (str): 操作人显示名称
        op_time (int): 操作时间 10位时间戳 以秒为单位

        content_type (ContentType): 待恢复对象的类型
        is_hide (bool): 是否为屏蔽
    """

    text: str = ""
    tid: int = 0
    pid: int = 0
    user: UserInfo_rec = dcs.field(default_factory=UserInfo_rec)
    post: Post_rec = dcs.field(default_factory=Post_rec)
    thread: Thread_rec = dcs.field(default_factory=Thread_rec)

    op_show_name: str = ""
    op_time: int = 0

    content_type: ContentType = ContentType.UNKNOWN
    is_hide: bool = False

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        thread_info = data_map["thread_info"]
        post_info = data_map["post_info"]
        sub_post_info = data_map["sub_post_info"]

        thread = Thread_rec.from_json(thread_info)

        if sub_post_info:
            content_type = ContentType.COMMENT
            post = Post_rec.from_json(post_info)
            text = sub_post_info["abstract"]
            pid = int(sub_post_info["pid"])
            user = UserInfo_rec.from_json(sub_post_info)
        elif post_info:
            content_type = ContentType.POST
            post = Post_rec()
            text = post_info["abstract"]
            pid = int(post_info["pid"])
            user = UserInfo_rec.from_json(post_info)
        else:
            content_type = ContentType.THREAD
            post = Post_rec()
            text = thread.text
            pid = 0
            user = thread.user

        op_show_name = data_map["op_info"]["name"]
        op_time = int(data_map["op_info"]["time"])
        is_hide = bool(int(data_map["is_frs_mask"]))

        return cls(text, thread.tid, pid, user, post, thread, op_show_name, op_time, content_type, is_hide)


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

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        page_size = data_map["rn"]
        current_page = data_map["pn"]
        has_more = bool(data_map["has_more"])
        has_prev = current_page > 1
        return cls(page_size, current_page, has_more, has_prev)


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

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        objs = [Recover.from_json(t) for t in data_map["data"]["thread_list"]]
        page = Page_recover.from_json(data_map["data"]["page"])
        return cls(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
