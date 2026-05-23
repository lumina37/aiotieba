from __future__ import annotations

import dataclasses as dcs
from datetime import datetime
from typing import TYPE_CHECKING

from ...exception import TbErrorExt
from ...helper import default_datetime
from .._classdef import Containers

if TYPE_CHECKING:
    import bs4


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

    @staticmethod
    def from_xml(data_tag: bs4.element.Tag) -> BawuListMemberUser:
        left_cell_item = data_tag.td

        post_user_item = left_cell_item.a
        user_name = post_user_item.text.lstrip()

        exp_item = left_cell_item.next_sibling.next_sibling
        exp = int(exp_item.string)

        level_item = exp_item.next_sibling
        level = int(level_item.string)

        thread_num_item = level_item.next_sibling
        thread_num = int(thread_num_item.string)

        good_num_item = thread_num_item.next_sibling
        good_num_text = good_num_item.string
        good_num = int(good_num_text) if good_num_text else 0

        join_time_item = good_num_item.next_sibling
        join_time = datetime.strptime(join_time_item.string, "%Y-%m-%d %H:%M")

        btn_group_item = join_time_item.next_sibling
        user_id = int(btn_group_item["id"])
        portrait = btn_group_item["portrait"]

        return BawuListMemberUser(user_id, portrait, user_name, exp, level, thread_num, good_num, join_time)


@dcs.dataclass
class BawuListMemberUsers(TbErrorExt, Containers[BawuListMemberUser]):
    """
    吧会员列表

    Attributes:
        objs (list[BawuListMemberUser]): 吧会员列表
        err (Exception | None): 捕获的异常
    """

    @staticmethod
    def from_xml(data_soup: bs4.BeautifulSoup) -> BawuListMemberUsers:
        objs = [BawuListMemberUser.from_xml(t) for t in data_soup.find("tbody").find_all("tr")]
        return BawuListMemberUsers(objs)
