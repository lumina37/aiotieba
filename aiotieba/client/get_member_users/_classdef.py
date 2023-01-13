import bs4

from .._classdef import Containers


class MemberUser(object):
    """
    最新关注用户信息

    Attributes:
        user_name (str): 用户名
        portrait (str): portrait
        level (int): 等级
    """

    __slots__ = [
        '_user_name',
        '_portrait',
        '_level',
    ]

    def _init(self, data_tag: bs4.element.Tag) -> "MemberUser":
        user_item = data_tag.a
        self._user_name = user_item['title']
        self._portrait = user_item['href'][14:]
        level_item = data_tag.span
        self._level = int(level_item['class'][1][12:])
        return self

    def __repr__(self) -> str:
        return str(
            {
                'user_name': self._user_name,
                'portrait': self._portrait,
                'level': self._level,
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
    def portrait(self) -> str:
        """
        用户portrait

        Note:
            唯一 不可变 不可为空
        """

        return self._portrait

    @property
    def level(self) -> int:
        """
        等级
        """

        return self._level


class Page_member(object):
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

    def _init(self, data_tag: bs4.element.Tag) -> "Page_member":
        self._current_page = int(data_tag.text)
        total_page_item = data_tag.parent.next_sibling
        self._total_page = int(total_page_item.text[1:-1])
        self._has_more = self._current_page < self._total_page
        self._has_prev = self._current_page > 1
        return self

    def _init_null(self) -> "Page_member":
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


class MemberUsers(Containers[MemberUser]):
    """
    最新关注用户列表

    Attributes:
        _objs (list[MemberUser]): 最新关注用户列表

        page (Page_member): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def _init(self, data_soup: bs4.BeautifulSoup) -> "MemberUsers":
        self._objs = [MemberUser()._init(t) for t in data_soup('div', class_='name_wrap')]
        self._page = Page_member()._init(data_soup.find('div', class_='tbui_pagination').find('li', class_='active'))
        return self

    def _init_null(self) -> "MemberUsers":
        self._objs = []
        self._page = Page_member()._init_null()
        return self

    @property
    def page(self) -> Page_member:
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
