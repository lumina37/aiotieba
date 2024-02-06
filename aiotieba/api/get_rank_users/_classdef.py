import dataclasses as dcs
from typing import Mapping

import bs4

from ...exception import TbErrorExt
from ...helper import parse_json
from .._classdef import Containers


@dcs.dataclass
class RankUser:
    """
    等级排行榜用户信息

    Attributes:
        user_name (str): 用户名
        level (int): 等级
        exp (int): 经验值
        is_vip (bool): 是否超级会员
    """

    user_name: str = ''
    level: int = 0
    exp: int = 0
    is_vip: bool = False

    @staticmethod
    def from_tbdata(data_tag: bs4.element.Tag) -> "RankUser":
        user_name_item = data_tag.td.next_sibling
        user_name = user_name_item.text
        is_vip = 'drl_item_vip' in user_name_item.div['class']
        level_item = user_name_item.next_sibling
        # e.g. get level 16 from "bg_lv16" by slicing [5:]
        level = int(level_item.div['class'][0][5:])
        exp_item = level_item.next_sibling
        exp = int(exp_item.text)
        return RankUser(user_name, level, exp, is_vip)


@dcs.dataclass
class Page_rank:
    """
    页信息

    Attributes:
        current_page (int): 当前页码
        total_page (int): 总页码

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    current_page: int = 0
    total_page: int = 0

    has_more: bool = False
    has_prev: int = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Page_rank":
        current_page = data_map['cur_page']
        total_page = data_map['total_num']
        has_more = current_page < total_page
        has_prev = current_page > 1
        return Page_rank(current_page, total_page, has_more, has_prev)


@dcs.dataclass
class RankUsers(TbErrorExt, Containers[RankUser]):
    """
    等级排行榜用户列表

    Attributes:
        objs (list[RankUser]): 等级排行榜用户列表
        err (Exception | None): 捕获的异常

        page (Page_rank): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_rank = dcs.field(default_factory=Page_rank)

    @staticmethod
    def from_tbdata(data_soup: bs4.BeautifulSoup) -> "RankUsers":
        objs = [RankUser.from_tbdata(t) for t in data_soup('tr', class_=['drl_list_item', 'drl_list_item_self'])]
        page_item = data_soup.find('ul', class_='p_rank_pager')
        page_dict = parse_json(page_item['data-field'])
        page = Page_rank.from_tbdata(page_dict)
        return RankUsers(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
