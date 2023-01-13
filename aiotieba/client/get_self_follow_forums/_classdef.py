from typing import Mapping

from .._classdef import Containers


class SelfFollowForum(object):
    """
    吧基本信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名
        level (int): 用户等级
    """

    __slots__ = [
        '_fid',
        '_fname',
        '_level',
    ]

    def _init(self, data_map: Mapping) -> "SelfFollowForum":
        self._fid = data_map['forum_id']
        self._fname = data_map['forum_name']
        self._level = data_map['level_id']
        return self

    def _init_null(self) -> "SelfFollowForum":
        self._fid = 0
        self._fname = ''
        self._level = 0
        return self

    def __repr__(self) -> str:
        return str(
            {
                'fid': self._fid,
                'fname': self._fname,
                'level': self._level,
            }
        )

    @property
    def fid(self) -> int:
        """
        贴吧id
        """

        return self._fid

    @property
    def fname(self) -> str:
        """
        贴吧名
        """

        return self._fname


class Page_sforum(object):
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

    def _init(self, data_map: Mapping) -> "Page_sforum":
        self._current_page = data_map['cur_page']
        self._total_page = data_map['total_page']
        self._has_more = self._current_page < self._total_page
        self._has_prev = self._current_page > 1
        return self

    def _init_null(self) -> "Page_sforum":
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


class SelfFollowForums(Containers[SelfFollowForum]):
    """
    本账号关注贴吧列表

    Attributes:
        _objs (list[SelfFollowForum]): 本账号关注贴吧列表

        page (Page_sforum): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def _init(self, data_map: Mapping) -> "SelfFollowForums":
        self._objs = [SelfFollowForum()._init(m) for m in data_map['list']]
        self._page = Page_sforum()._init(data_map['page'])
        return self

    def _init_null(self) -> "SelfFollowForums":
        self._objs = []
        self._page = Page_sforum()._init_null()
        return self

    @property
    def page(self) -> Page_sforum:
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
