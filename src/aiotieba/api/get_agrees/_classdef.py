from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import TYPE_CHECKING, Self

from ...enums import ContentType
from ...exception import TbErrorExt
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping


_CONTENT_TYPES = {1: ContentType.POST, 2: ContentType.COMMENT, 3: ContentType.THREAD}


@dcs.dataclass
class UserInfo_agree:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ""
    user_name: str = ""
    nick_name_new: str = ""

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user_id = int(data_map["id"])
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_map["name"]
        nick_name_new = data_map["name_show"]

        return cls(user_id, portrait, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_new}/{self.portrait}"
        else:
            return str(self.user_id)


@dcs.dataclass
class Post_agree:
    """
    被点赞的回复信息

    Attributes:
        pid (int): 回复id
        text (str): 文本内容
    """

    pid: int = 0
    text: str = ""

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        post_map = data_map.get("post_info")
        if not post_map:
            return cls()

        pid = int(post_map["id"])
        text = "".join(frag["text"] for frag in post_map["content"])

        return cls(pid, text)

    def __bool__(self) -> bool:
        return bool(self.pid)


@dcs.dataclass
class Agree:
    """
    点赞信息

    Attributes:
        user (UserInfo_agree): 点赞者的用户信息

        agree_id (int): 点赞记录id 用于翻页
        fname (str): 所在贴吧名
        fid (int): 所在贴吧id
        tid (int): 所在主题帖id
        title (str): 所在主题帖标题
        post (Post_agree): 被点赞的回复信息 点赞对象为主题帖时该字段为空

        content_type (ContentType): 被点赞的帖子对象类型
        create_time (int): 点赞时间 10位时间戳 以秒为单位
    """

    user: UserInfo_agree = dcs.field(default_factory=UserInfo_agree)

    agree_id: int = 0
    fname: str = ""
    fid: int = 0
    tid: int = 0
    title: str = ""
    post: Post_agree = dcs.field(default_factory=Post_agree)

    content_type: ContentType = ContentType.UNKNOWN
    create_time: int = 0

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user = UserInfo_agree.from_json(data_map["agreeer"])

        agree_id = int(data_map["id"])
        thread_map = data_map["thread_info"]
        fname = thread_map["fname"]
        fid = int(thread_map["fid"])
        tid = int(thread_map["id"])
        title = thread_map["title"]
        post = Post_agree.from_json(data_map)

        content_type = _CONTENT_TYPES.get(int(data_map["type"]), ContentType.UNKNOWN)
        create_time = int(data_map["time"])

        return cls(user, agree_id, fname, fid, tid, title, post, content_type, create_time)


@dcs.dataclass
class Agrees(TbErrorExt, Containers[Agree]):
    """
    点赞信息列表

    Attributes:
        objs (list[Agree]): 点赞信息列表
        err (Exception | None): 捕获的异常

        has_more (bool): 是否还有下一页
    """

    has_more: bool = False

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        objs = [Agree.from_json(m) for m in data_map.get("agree_list", [])]
        has_more = bool(int(data_map["has_more"]))

        return cls(objs, has_more)
