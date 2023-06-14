import datetime
from typing import Optional

import bs4

from .._classdef import Containers


class Userlog(object):
    """
    吧务用户管理日志

    Attributes:
        op_type (str): 操作类型
        op_duration (int): 操作作用时长
        user_portrait (str): 被操作用户的portrait
        op_user_name (str): 操作人用户名
        op_time (datetime.datetime): 操作时间
    """

    __slots__ = [
        '_op_type',
        '_op_duration',
        '_user_portrait',
        '_op_user_name',
        '_op_time',
    ]

    def __init__(self, data_tag: bs4.element.Tag) -> None:
        left_cell_item = data_tag.td

        post_user_item = left_cell_item.a
        self._user_portrait = post_user_item['href'][14:-17]

        op_type_item = left_cell_item.next_sibling.next_sibling
        self._op_type = op_type_item.string

        op_duration_item = op_type_item.next_sibling
        op_duration = op_duration_item.string.replace(' ', '')
        self._op_duration = 0 if '天' not in op_duration else int(op_duration[:-1])

        op_user_name_item = op_duration_item.next_sibling
        self._op_user_name = op_user_name_item.string

        op_time_item = op_user_name_item.next_sibling
        self._op_time = datetime.datetime.strptime(op_time_item.text, '%Y-%m-%d %H:%M')

    def __repr__(self) -> str:
        return str(
            {
                'op_type': self._op_type,
                'op_duration': self._op_duration,
                'user': self._user_portrait,
            }
        )

    @property
    def op_type(self) -> str:
        """
        操作类型
        """

        return self._op_type

    @property
    def op_duration(self) -> int:
        """
        操作持续时间

        Note:
            单位为天
        """

        return self._op_duration

    @property
    def user_portrait(self) -> str:
        """
        被操作用户的portrait
        """

        return self._user_portrait

    @property
    def op_user_name(self) -> str:
        """
        操作人用户名
        """

        return self._op_user_name

    @property
    def op_time(self) -> datetime.datetime:
        """
        操作时间
        """

        return self._op_time


class Page_postlog(object):
    """
    页信息

    Attributes:
        current_page (int): 当前页码
        total_page (int): 总页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = [
        '_current_page',
        '_total_page',
        '_total_count',
        '_has_more',
        '_has_prev',
    ]

    def _init(self, data_soup: bs4.BeautifulSoup) -> "Page_postlog":
        page_tag = data_soup.find('div', class_='tbui_pagination').find('li', class_='active')
        self._current_page = int(page_tag.text)
        total_page_item = page_tag.parent.next_sibling
        self._total_page = int(total_page_item.text[1:-1])
        self._has_more = self._current_page < self._total_page
        self._has_prev = self._current_page > 1

        total_count_tag = data_soup.find('div', class_='breadcrumbs')
        self._total_count = int(total_count_tag.em.text)

        return self

    def _init_null(self) -> "Page_postlog":
        self._current_page = 0
        self._total_page = 0
        self._total_count = 0
        self._has_more = False
        self._has_prev = False
        return self

    def __repr__(self) -> str:
        return str(
            {
                'current_page': self._current_page,
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
    def total_count(self) -> int:
        """
        总计数
        """

        return self._total_count

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


class Userlogs(Containers[Userlog]):
    """
    吧务用户管理日志表

    Attributes:
        _objs (list[Postlog]): 吧务用户管理日志表

        page (Page_postlog): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, data_soup: Optional[bs4.BeautifulSoup] = None) -> None:
        if data_soup:
            self._objs = [Userlog(_tag) for _tag in data_soup.find('tbody').find_all('tr')]
            self._page = Page_postlog()._init(data_soup)
        else:
            self._objs = []
            self._page = Page_postlog()._init_null()

    @property
    def page(self) -> Page_postlog:
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
