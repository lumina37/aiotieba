__all__ = [
    'BlacklistUsers',
    'Fans',
    'Follows',
]

from typing import List, Optional

import bs4
from google.protobuf.json_format import ParseDict

from ..protobuf import Page_pb2, User_pb2
from .common import Page, UserInfo
from .container import Containers


class BlacklistUsers(Containers[UserInfo]):
    """
    黑名单用户列表

    Attributes:
        objs (list[UserInfo]): 黑名单用户列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[bs4.BeautifulSoup] = None) -> None:
        super(BlacklistUsers, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data('td', class_='left_cell')
            self._page = _raw_data.find('div', class_='tbui_pagination').find('li', class_='active')

        else:
            self._raw_objs = None
            self._page = None

    @property
    def objs(self) -> List[UserInfo]:
        """
        黑名单用户列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:

                def parse_tag(tag):
                    user_info_item = tag.previous_sibling.input
                    user = UserInfo()
                    user.user_name = user_info_item['data-user-name']
                    user.user_id = int(user_info_item['data-user-id'])
                    user.portrait = tag.a['href'][14:]
                    return user

                self._objs = [parse_tag(_tag) for _tag in self._raw_objs]

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


class Fans(Containers[UserInfo]):
    """
    粉丝列表

    Attributes:
        objs (list[UserInfo]): 粉丝列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Fans, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data['user_list']
            self._page = _raw_data['page']

        else:
            self._raw_objs = None
            self._page = None

    @property
    def objs(self) -> List[UserInfo]:
        """
        粉丝列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [
                    UserInfo(_raw_data=ParseDict(_dict, User_pb2.User(), ignore_unknown_fields=True))
                    for _dict in self._raw_objs
                ]
                self._raw_objs = None
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
                self._page = Page(ParseDict(self._page, Page_pb2.Page(), ignore_unknown_fields=True))
            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more


class Follows(Containers[UserInfo]):
    """
    关注列表

    Attributes:
        objs (list[UserInfo]): 关注列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_has_more',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Follows, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data['follow_list']
            self._has_more = bool(int(_raw_data['has_more']))

        else:
            self._raw_objs = None
            self._has_more = False

    @property
    def objs(self) -> List[UserInfo]:
        """
        关注列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [
                    UserInfo(_raw_data=ParseDict(_dict, User_pb2.User(), ignore_unknown_fields=True))
                    for _dict in self._raw_objs
                ]
                self._raw_objs = None
            else:
                self._objs = []

        return self._objs

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more
