from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from ...helper import tbnum2int
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class UserInfo_sg:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    user_name: str = ""
    nick_name_new: str = ""

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user_id = int(data_map["user_id"])
        user_name = data_map["user_name"] or ""
        nick_name_new = data_map["show_nickname"] or ""
        return cls(user_id, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or str(self.user_id)

    def __eq__(self, obj: UserInfo_sg) -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        return self.user_name or str(self.user_id)


@dcs.dataclass
class SearchGlobal:
    """
    全吧搜索结果

    Attributes:
        title (str): 标题
        content (str): 正文

        user (UserInfo_sg)
        forum_id (int): 所在贴吧fid
        forum_name (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id

        post_num (int): 回复数
        create_time (int): 创建时间
    """

    title: str = ""
    content: str = ""

    user: UserInfo_sg = dcs.field(default_factory=UserInfo_sg)
    forum_id: int = 0
    forum_name: str = ""
    tid: int = 0
    pid: int = 0

    post_num: int = 0
    create_time: int = 0

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user_map = data_map["user"]

        title = data_map["title"]
        content = data_map["content"]

        user = UserInfo_sg.from_json(user_map)
        forum_id = data_map["forum_id"]
        forum_name = data_map["forum_name"]
        tid = int(data_map["tid"])
        pid = int(data_map["pid"])

        post_num = tbnum2int(data_map["post_num"], "W")
        create_time = data_map["create_time"]

        return cls(title, content, user, forum_id, forum_name, tid, pid, post_num, create_time)

    def __eq__(self, obj: SearchGlobal) -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid


@dcs.dataclass
class SearchGlobals(TbErrorExt, Containers[SearchGlobal]):
    """
    全吧搜索结果列表

    Attributes:
        objs (list[SearchGlobal]): 搜索结果列表
        err (Exception | None): 捕获的异常

        has_more (bool): 是否还有下一页
        current_page (int): 当前页码
    """

    has_more: bool = False
    current_page: int = 0

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        objs = [SearchGlobal.from_json(m) for m in data_map["post_list"]]
        has_more = bool(data_map["has_more"])
        current_page = data_map["current_page"]
        return cls(objs, has_more, current_page)
