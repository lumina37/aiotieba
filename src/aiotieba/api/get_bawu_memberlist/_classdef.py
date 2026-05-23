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
        tds = data_tag.find_all("td")

        left_cell = tds[0]
        user_name = left_cell.a.text.strip()

        exp = int(tds[2].text.strip())

        level_item = tds[3].div
        level = int(level_item.span.text.strip())

        thread_num = int(tds[4].text.strip())

        good_num_text = tds[5].text.strip()
        good_num = int(good_num_text) if good_num_text else 0

        in_time_str = tds[6].text.strip()
        join_time = datetime.strptime(in_time_str, "%Y-%m-%d %H:%M")

        btn_group = tds[7]
        user_id = int(btn_group["id"])
        portrait = btn_group["portrait"]

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
