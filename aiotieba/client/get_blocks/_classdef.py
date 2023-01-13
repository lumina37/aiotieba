from typing import Mapping

import bs4

from .._classdef import Containers


class Block(object):
    """
    待解封用户信息

    Attributes:
        user_id (int): user_id
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称
        day (int): 封禁天数
    """

    __slots__ = [
        '_user_id',
        '_user_name',
        '_nick_name_old',
        '_day',
    ]

    def _init(self, data_tag: bs4.element.Tag) -> "Block":
        id_tag = data_tag.a
        self._user_id = int(id_tag['attr-uid'])
        self._user_name = id_tag['attr-un']
        self._nick_name_old = id_tag['attr-nn']
        self._day = int(id_tag['attr-blockday'])
        return self

    def _init_null(self) -> "Block":
        self._user_id = 0
        self._user_name = ''
        self._nick_name_old = ''
        self._day = 0
        return self

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'user_name': self._user_name,
                'nick_name_old': self._nick_name_old,
                'day': self._day,
            }
        )

    @property
    def user_id(self) -> int:
        """
        用户user_id

        Note:
            唯一 不可变 不可为空
            请注意与用户个人页的tieba_uid区分
        """

        return self._user_id

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
    def nick_name_old(self) -> str:
        """
        旧版昵称
        """

        return self._nick_name_old

    @property
    def day(self) -> int:
        """
        封禁天数
        """

        return self._day


class Page_block(object):
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
        '_page_size',
        '_current_page',
        '_total_page',
        '_total_count',
        '_has_more',
        '_has_prev',
    ]

    def _init(self, data_map: Mapping) -> "Page_block":
        self._page_size = data_map['size']
        self._current_page = data_map['pn']
        self._total_page = data_map['total_page']
        self._total_count = data_map['total_count']
        self._has_more = data_map['have_next']
        self._has_prev = self._current_page > 1
        return self

    def _init_null(self) -> "Page_block":
        self._page_size = 0
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
                'total_page': self._total_page,
                'has_more': self._has_more,
                'has_prev': self._has_prev,
            }
        )

    @property
    def page_size(self) -> int:
        """
        页大小
        """

        return self._page_size

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


class Blocks(Containers[Block]):
    """
    待恢复帖子列表

    Attributes:
        _objs (list[Block]): 待恢复帖子列表

        page (Page_block): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def _init(self, data_map: Mapping) -> "Blocks":
        data_soup = bs4.BeautifulSoup(data_map['data']['content'], 'lxml')
        self._objs = [Block()._init(t) for t in data_soup('li')]
        self._page = Page_block()._init(data_map['data']['page'])
        return self

    def _init_null(self) -> "Blocks":
        self._objs = []
        self._page = Page_block()._init_null()
        return self

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._page._has_more
