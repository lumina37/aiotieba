from typing import Mapping

import bs4

from .._classdef import Containers


class Recover(object):
    """
    待恢复帖子信息

    Attributes:
        text (str): 文本内容
        tid (int): 所在主题帖id
        pid (int): 回复id
        is_hide (bool): 是否为屏蔽
        oper (bool): 操作人名称
    """

    __slots__ = [
        '_text',
        '_tid',
        '_pid',
        '_is_hide',
        '_oper',
    ]

    def _init(self, data_tag: bs4.element.Tag) -> "Recover":
        id_tag = data_tag.a
        self._tid = int(id_tag['attr-tid'])
        self._pid = int(id_tag['attr-pid'])
        self._is_hide = bool(int(id_tag['attr-isfrsmask']))
        text_tag = id_tag.next_sibling.span
        self._text = text_tag.string
        oper_tag = id_tag.next_sibling.find('span', class_="recover_list_item_operator")
        self._oper = oper_tag.string[4:]
        return self

    def _init_null(self) -> "Recover":
        self._text = ""
        self._tid = 0
        self._pid = 0
        self._is_hide = False
        self._oper = ''
        return self

    def __repr__(self) -> str:
        return str(
            {
                'text': self._text,
                'tid': self.tid,
                'pid': self.pid,
                'is_hide': self.is_hide,
                'oper': self._oper,
            }
        )

    @property
    def text(self) -> str:
        """
        文本内容
        """

        return self._text

    @property
    def tid(self) -> int:
        """
        所在主题帖id
        """

        return self._tid

    @property
    def pid(self) -> int:
        """
        回复id
        """

        return self._pid

    @property
    def is_hide(self) -> bool:
        """
        是否为屏蔽
        """

        return self._is_hide

    @property
    def oper(self) -> str:
        """
        操作人名称
        """

        return self._oper


class Page_recover(object):
    """
    页信息

    Attributes:
        page_size (int): 页大小
        current_page (int): 当前页码

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = [
        '_page_size',
        '_current_page',
        '_has_more',
        '_has_prev',
    ]

    def _init(self, data_map: Mapping) -> "Page_recover":
        self._page_size = data_map['size']
        self._current_page = data_map['pn']
        self._has_more = data_map['have_next']
        self._has_prev = self._current_page > 1
        return self

    def _init_null(self) -> "Page_recover":
        self._page_size = 0
        self._current_page = 0
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


class Recovers(Containers[Recover]):
    """
    待恢复帖子列表

    Attributes:
        _objs (list[Recover]): 待恢复帖子列表

        page (Page_recover): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def _init(self, data_map: Mapping) -> "Recovers":
        data_soup = bs4.BeautifulSoup(data_map['data']['content'], 'lxml')
        self._objs = [Recover()._init(t) for t in data_soup('li')]
        self._page = Page_recover()._init(data_map['data']['page'])
        return self

    def _init_null(self) -> "Recovers":
        self._objs = []
        self._page = Page_recover()._init_null()
        return self

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._page._has_more
