__all__ = [
    'RankUser',
    'RankUsers',
]


from typing import List, Optional

import bs4
from google.protobuf.json_format import ParseDict

from ...common.helper import jsonlib
from ..protobuf import Page_pb2
from .common import Page
from .container import Containers


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

    def __init__(self, _raw_data: Optional[bs4.element.Tag] = None) -> None:

        if _raw_data:
            user_name_item = _raw_data.td.next_sibling
            self._user_name = user_name_item.text
            self._is_vip = 'drl_item_vip' in user_name_item.div['class']
            level_item = user_name_item.next_sibling
            # e.g. get level 16 from "bg_lv16" by slicing [5:]
            self._level = int(level_item.div['class'][0][5:])
            exp_item = level_item.next_sibling
            self._exp = int(exp_item.text)

        else:
            self._user_name = ''
            self._level = 0
            self._exp = 0
            self._is_vip = False

    def __repr__(self) -> str:
        return str(
            {
                'user_name': self.user_name,
                'level': self.level,
                'exp': self.exp,
                'is_vip': self.is_vip,
            }
        )

    @property
    def user_name(self) -> str:
        """
        用户名
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


class RankUsers(Containers[RankUser]):
    """
    等级排行榜用户列表

    Attributes:
        objs (list[RankUser]): 等级排行榜用户列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[bs4.BeautifulSoup] = None) -> None:
        super(RankUsers, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data('tr', class_=['drl_list_item', 'drl_list_item_self'])

            page_item = _raw_data.find('ul', class_='p_rank_pager')
            self._page = jsonlib.loads(page_item['data-field'])

        else:
            self._raw_objs = None
            self._page = None

    @property
    def objs(self) -> List[RankUser]:
        """
        等级排行榜用户列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [RankUser(_tag) for _tag in self._raw_objs]
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
                self._page['current_page'] = self._page.pop('cur_page')
                self._page['total_count'] = self._page.pop('total_num')
                page_proto = ParseDict(self._page, Page_pb2.Page(), ignore_unknown_fields=True)
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
