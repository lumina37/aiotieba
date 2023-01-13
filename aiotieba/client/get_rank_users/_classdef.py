from typing import Mapping

import bs4

from .._classdef import Containers
from .._helper import parse_json


class RankUser(object):
    """
    等级排行榜用户信息

    Attributes:
        user_name (str): 用户名
        level (int): 等级
        exp (int): 经验值
        is_vip (bool): 是否超级会员
    """

    __slots__ = [
        '_user_name',
        '_level',
        '_exp',
        '_is_vip',
    ]

    def _init(self, data_tag: bs4.element.Tag) -> "RankUser":
        user_name_item = data_tag.td.next_sibling
        self._user_name = user_name_item.text
        self._is_vip = 'drl_item_vip' in user_name_item.div['class']
        level_item = user_name_item.next_sibling
        # e.g. get level 16 from "bg_lv16" by slicing [5:]
        self._level = int(level_item.div['class'][0][5:])
        exp_item = level_item.next_sibling
        self._exp = int(exp_item.text)
        return self

    def __repr__(self) -> str:
        return str(
            {
                'user_name': self._user_name,
                'level': self._level,
                'exp': self._exp,
                'is_vip': self._is_vip,
            }
        )

    @property
    def user_name(self) -> str:
        """
        用户名

        Note:
            唯一 可变 可为空
            请注意与用户昵称区分
        """

        return self._user_name

    @property
    def level(self) -> int:
        """
        等级
        """

        return self._level

    @property
    def exp(self) -> int:
        """
        经验值
        """

        return self._exp

    @property
    def is_vip(self) -> bool:
        """
        是否超级会员
        """

        return self._is_vip


class Page_rank(object):
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

    __slots__ = [
        '_current_page',
        '_total_page',
        '_has_more',
        '_has_prev',
    ]

    def _init(self, data_map: Mapping) -> "Page_rank":
        self._current_page = data_map['cur_page']
        self._total_page = data_map['total_num']
        self._has_more = self._current_page < self._total_page
        self._has_prev = self._current_page > 1
        return self

    def _init_null(self) -> "Page_rank":
        self._current_page = 0
        self._total_page = 0
        self._has_more = False
        self._has_prev = False
        return self

    def __repr__(self) -> str:
        return str(
            {
                'current_page': self._current_page,
                'total_page': self._total_page,
                'has_more': self._has_more,
                'has_prev': self._has_prev,
            }
        )

    @property
    def current_page(self) -> int:
        """
        当前页码
        """

        return self._current_page

    @property
    def total_page(self) -> int:
        """
        总页码
        """

        return self._total_page

    @property
    def has_more(self) -> bool:
        """
        是否有后继页
        """

        return self._has_more

    @property
    def has_prev(self) -> bool:
        """
        是否有前驱页
        """

        return self._has_prev


class RankUsers(Containers[RankUser]):
    """
    等级排行榜用户列表

    Attributes:
        _objs (list[RankUser]): 等级排行榜用户列表

        page (Page_rank): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def _init(self, data_soup: bs4.BeautifulSoup) -> "RankUsers":
        self._objs = [RankUser()._init(t) for t in data_soup('tr', class_=['drl_list_item', 'drl_list_item_self'])]
        page_item = data_soup.find('ul', class_='p_rank_pager')
        page_dict = parse_json(page_item['data-field'])
        self._page = Page_rank()._init(page_dict)
        return self

    def _init_null(self) -> "RankUsers":
        self._objs = []
        self._page = Page_rank()._init_null()

    @property
    def page(self) -> Page_rank:
        """
        页信息
        """

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._page._has_more
