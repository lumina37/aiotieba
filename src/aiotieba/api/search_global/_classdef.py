from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class GlobalSearchPost:
    """
    全吧搜索结果

    Attributes:
        tid (int): 所在主题帖id
        pid (int): 回复id
        title (str): 标题
        content (str): 正文
        create_time (int): 创建时间

        forum_id (int): 所在贴吧fid
        forum_name (str): 所在贴吧名
        post_num (int): 回复数
        pb_url (str): 帖子页相对路径

        author_id (int): 作者user_id
        author_name (str): 作者用户名
        author_show_name (str): 作者显示昵称
    """

    tid: int = 0
    pid: int = 0
    title: str = ""
    content: str = ""
    create_time: int = 0

    forum_id: int = 0
    forum_name: str = ""
    post_num: int = 0
    pb_url: str = ""

    author_id: int = 0
    author_name: str = ""
    author_show_name: str = ""

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        user_map = data_map.get("user") or {}
        return GlobalSearchPost(
            tid=int(data_map["tid"]),
            pid=int(data_map["pid"]),
            title=data_map.get("title", ""),
            content=data_map.get("content", ""),
            create_time=int(data_map.get("create_time") or data_map.get("time") or 0),
            forum_id=int(data_map.get("forum_id") or 0),
            forum_name=data_map.get("forum_name", ""),
            post_num=int(data_map.get("post_num") or 0),
            pb_url=data_map.get("pb_url", ""),
            author_id=int(user_map.get("user_id") or 0),
            author_name=user_map.get("user_name", ""),
            author_show_name=user_map.get("show_nickname") or user_map.get("user_name", ""),
        )

    def __eq__(self, obj: GlobalSearchPost) -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid


@dcs.dataclass
class GlobalSearches(TbErrorExt, Containers[GlobalSearchPost]):
    """
    全吧搜索结果列表

    Attributes:
        objs (list[GlobalSearchPost]): 搜索结果列表
        err (Exception | None): 捕获的异常

        has_more (bool): 是否还有下一页
        current_page (int): 当前页码
    """

    has_more: bool = False
    current_page: int = 0

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        objs = [GlobalSearchPost.from_json(m) for m in data_map.get("post_list", [])]
        has_more = bool(int(data_map.get("has_more") or 0))
        current_page = int(data_map.get("current_page") or 0)
        return GlobalSearches(objs, has_more, current_page)
