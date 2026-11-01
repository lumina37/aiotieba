from __future__ import annotations

import dataclasses as dcs
import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from ...helper import default_datetime
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping


_LEFT_TIME_PATTERN = re.compile(r"(\d+)(天|小时|分钟)")
_TIME_UNIT_SECONDS = {"天": 86400, "小时": 3600, "分钟": 60}


def _parse_left_time_tip(tip: str) -> datetime:
    match = _LEFT_TIME_PATTERN.match(tip)
    seconds = int(match[1]) * _TIME_UNIT_SECONDS[match[2]]

    return datetime.now() + timedelta(seconds=seconds)


@dcs.dataclass
class ChatroomBlock:
    """
    吧群禁言用户

    Attributes:
        user_name (str): 用户名
        nick_name_new (str): 新版昵称
        portrait (str): portrait

        approx_end_dt (datetime): 大致解除禁言时间
    """

    user_name: str = ""
    nick_name_new: str = ""
    portrait: str = ""

    approx_end_dt: datetime = dcs.field(default_factory=default_datetime)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user_name = data_map["name"]
        nick_name_new = data_map["show_nickname"]
        portrait = data_map["portrait_id"]
        if "?" in portrait:
            portrait = portrait[:-13]
        approx_end_dt = _parse_left_time_tip(data_map["left_time_tip"])

        return cls(user_name, nick_name_new, portrait, approx_end_dt)


@dcs.dataclass
class Page_crblock:
    """
    页信息

    Attributes:
        page_size (int): 页大小
        current_page (int): 当前页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    page_size: int = 0
    current_page: int = 0
    total_count: int = 0

    has_more: bool = False
    has_prev: bool = False

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        page_size = data_map["rn"]
        current_page = data_map["pn"]
        total_count = data_map["total"]
        has_more = current_page * page_size < total_count
        has_prev = current_page > 1

        return cls(page_size, current_page, total_count, has_more, has_prev)


@dcs.dataclass
class ChatroomBlocks(TbErrorExt, Containers[ChatroomBlock]):
    """
    吧群禁言用户列表

    Attributes:
        objs (list[ChatroomBlock]): 吧群禁言用户列表
        err (Exception | None): 捕获的异常

        page (Page_crblock): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_crblock = dcs.field(default_factory=Page_crblock)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        objs = [ChatroomBlock.from_json(m) for m in data_map["user_forbidden_list"]]
        page = Page_crblock.from_json(data_map)

        return cls(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
