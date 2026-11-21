from __future__ import annotations

import dataclasses as dcs
from datetime import datetime
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from ...helper import default_datetime
from ...helper.parse import text_of
from .._classdef import Containers

if TYPE_CHECKING:
    from lxml import etree


@dcs.dataclass
class BawuListMemberUser:
    """
    吧会员信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名

        exp (int): 经验值
        level (int): 等级
        thread_num (int): 主题帖数
        good_num (int): 精品帖数

        join_time (datetime): 关注时间
    """

    user_id: int = 0
    portrait: str = ""
    user_name: str = ""

    exp: int = 0
    level: int = 0
    thread_num: int = 0
    good_num: int = 0

    join_time: datetime = dcs.field(default_factory=default_datetime)

    @classmethod
    def from_xml(cls, data_tag: etree._Element) -> Self:
        tds = data_tag.xpath("./td")
        left_cell_item = tds[0]

        user_item = left_cell_item.xpath("./a")[0]
        user_name = text_of(user_item).lstrip()

        exp = int(text_of(tds[2]).strip())

        level = int(text_of(tds[3]).strip())

        thread_num = int(text_of(tds[4]).strip())

        good_num_text = text_of(tds[5]).strip()
        good_num = int(good_num_text) if good_num_text else 0

        join_time = datetime.strptime(text_of(tds[6]).strip(), "%Y-%m-%d %H:%M")

        btn_group_item = tds[7]
        user_id = int(btn_group_item.get("id"))
        portrait = btn_group_item.get("portrait")

        return cls(user_id, portrait, user_name, exp, level, thread_num, good_num, join_time)


@dcs.dataclass
class BawuListMemberUsers(TbErrorExt, Containers[BawuListMemberUser]):
    """
    吧会员列表

    Attributes:
        objs (list[BawuListMemberUser]): 吧会员列表
        err (Exception | None): 捕获的异常
    """

    @classmethod
    def from_xml(cls, data_soup: etree._Element) -> Self:
        tbody = data_soup.xpath("//tbody")[0]
        objs = [BawuListMemberUser.from_xml(t) for t in tbody.xpath(".//tr")]
        return cls(objs)
