import bs4

from .._classdef import Containers


class BlacklistUser(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名

        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
    ]

    def _init(self, data_tag: bs4.element.Tag) -> "BlacklistUser":
        user_info_item = data_tag.previous_sibling.input
        self._user_name = user_info_item['data-user-name']
        self._user_id = int(user_info_item['data-user-id'])
        self._portrait = data_tag.a['href'][14:-17]
        return self

    def __str__(self) -> str:
        return self._user_name or self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'user_name': self._user_name,
                'portrait': self._portrait,
            }
        )

    def __eq__(self, obj: "BlacklistUser") -> bool:
        return self._user_id == obj._user_id

    def __hash__(self) -> int:
        return self._user_id

    def __int__(self) -> int:
        return self._user_id

    def __bool__(self) -> bool:
        return bool(self._user_id)

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
    def portrait(self) -> str:
        """
        用户portrait

        Note:
            唯一 不可变 不可为空
        """

        return self._portrait

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
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        return self.__str__()


class Page_blacklist(object):
    """
    页信息

    Attributes:
        current_page (int): 当前页码
        total_page (int): 总页码

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = [
        '_current_page',
        '_total_page',
        '_has_more',
        '_has_prev',
    ]

    def _init(self, data_tag: bs4.element.Tag) -> "Page_blacklist":
        self._current_page = int(data_tag.text)
        total_page_item = data_tag.parent.next_sibling
        self._total_page = int(total_page_item.text[1:-1])
        self._has_more = self._current_page < self._total_page
        self._has_prev = self._current_page > 1
        return self

    def _init_null(self) -> "Page_blacklist":
        self._current_page = 0
        self._total_page = 0
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


class BlacklistUsers(Containers[BlacklistUser]):
    """
    黑名单用户列表

    Attributes:
        _objs (list[BlacklistUser]): 黑名单用户列表

        page (Page_blacklist): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def _init(self, data_soup: bs4.BeautifulSoup) -> "BlacklistUsers":
        self._objs = [BlacklistUser()._init(_tag) for _tag in data_soup('td', class_='left_cell')]
        page_tag = data_soup.find('div', class_='tbui_pagination').find('li', class_='active')
        self._page = Page_blacklist()._init(page_tag)
        return self

    def _init_null(self) -> "BlacklistUsers":
        self._objs = []
        self._page = Page_blacklist()._init_null()
        return self

    @property
    def page(self) -> Page_blacklist:
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
