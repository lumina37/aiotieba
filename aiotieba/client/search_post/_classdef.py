from typing import List, Mapping

from .._classdef import Containers


class Search(object):
    """
    搜索结果

    Attributes:
        text (str): 文本内容
        title (str): 标题

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        show_name (str): 发布者的显示名称

        is_floor (bool): 是否楼中楼
        create_time (int): 创建时间
    """

    __slots__ = [
        '_text',
        '_title',
        '_fname',
        '_tid',
        '_pid',
        '_show_name',
        '_is_floor',
        '_create_time',
    ]

    def _init(self, data_map: Mapping) -> "Search":
        self._text = data_map['content']
        self._title = data_map['title']
        self._fname = data_map['fname']
        self._tid = int(data_map['tid'])
        self._pid = int(data_map['pid'])
        self._show_name = data_map['author']["name_show"]
        self._is_floor = bool(int(data_map['is_floor']))
        self._create_time = int(data_map['time'])
        return self

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'pid': self._pid,
                'show_name': self._show_name,
                'text': self._text,
                'is_floor': self._is_floor,
            }
        )

    def __eq__(self, obj: "Search") -> bool:
        return self._pid == obj._pid

    def __hash__(self) -> int:
        return self._pid

    @property
    def text(self) -> str:
        """
        文本内容
        """

        return self._text

    @property
    def title(self) -> str:
        """
        帖子标题
        """

        return self._title

    @property
    def fid(self) -> int:
        """
        所在吧id
        """

        return self._fid

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
    def is_floor(self) -> bool:
        """
        是否楼中楼
        """

        return self._is_floor

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._create_time


class Page_search(object):
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

    def _init(self, data_map: Mapping) -> "Page_search":
        self._page_size = int(data_map["page_size"])
        self._current_page = int(data_map["current_page"])
        self._total_page = int(data_map["total_page"])
        self._total_count = int(data_map["total_count"])
        self._has_more = bool(int(data_map["has_more"]))
        self._has_prev = bool(int(data_map["has_prev"]))
        return self

    def _init_null(self) -> "Page_search":
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


class Searches(Containers[Search]):
    """
    搜索结果列表

    Attributes:
        _objs (list[Search]): 搜索结果列表

        page (Page_search): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def _init(self, data_map: Mapping) -> "Searches":
        self._objs = [Search()._init(m) for m in data_map.get('post_list', [])]
        self._page = Page_search()._init(data_map['page'])
        return self

    def _init_null(self) -> "Searches":
        self._objs = []
        self._page = Page_search()._init_null()
        return self

    @property
    def objs(self) -> List[Search]:
        """
        搜索结果列表
        """

        return self._objs

    @property
    def page(self) -> Page_search:
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
