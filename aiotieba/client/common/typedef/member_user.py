__all__ = [
    'MemberUser',
    'MemberUsers',
]

from typing import List, Optional

import bs4

from ..protobuf import Page_pb2
from .common import Page
from .container import Containers


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

    def __init__(self, _raw_data: Optional[bs4.element.Tag] = None) -> None:

        if _raw_data:
            user_item = _raw_data.a
            self._user_name = user_item['title']
            self._portrait = user_item['href'][14:]
            level_item = _raw_data.span
            self._level = int(level_item['class'][1][12:])

        else:
            self._user_name = ''
            self._portrait = ''
            self._level = 0

    def __repr__(self) -> str:
        return str(
            {
                'user_name': self.user_name,
                'portrait': self.portrait,
                'level': self.level,
            }
        )

    @property
    def user_name(self) -> str:
        """
        用户名

        Note:
            具有唯一性
            请注意与用户昵称区分
        """

        return self._user_name

    @property
    def portrait(self) -> str:
        """
        用户portrait

        Note:
            具有唯一性
            可以用于获取用户头像
        """

        return self._portrait

    @property
    def level(self) -> int:
        """
        等级
        """

        return self._level


class MemberUsers(Containers[MemberUser]):
    """
    最新关注用户列表

    Attributes:
        objs (list[MemberUser]): 最新关注用户列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[bs4.BeautifulSoup] = None) -> None:
        super(MemberUsers, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data('div', class_='name_wrap')
            self._page = _raw_data.find('div', class_='tbui_pagination').find('li', class_='active')

        else:
            self._raw_objs = None
            self._page = None

        self._page = None

    @property
    def objs(self) -> List[MemberUser]:
        """
        最新关注用户列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [MemberUser(_raw_data=_tag) for _tag in self._raw_objs]
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                page_proto = Page_pb2.Page()
                page_proto.current_page = int(self._page.text)
                total_page_item = self._page.parent.next_sibling
                page_proto.total_page = int(total_page_item.text[1:-1])
                self._page = Page(page_proto)

            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more
