from .._classdef import Containers, TypeMessage


class SquareForum(object):
    """
    吧广场贴吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        member_num (int): 吧会员数
        post_num (int): 发帖量

        is_followed (bool): 是否已关注
    """

    __slots__ = [
        '_fid',
        '_fname',
        '_member_num',
        '_post_num',
        '_is_followed',
    ]

    def _init(self, data_proto: TypeMessage) -> "SquareForum":
        self._fid = data_proto.forum_id
        self._fname = data_proto.forum_name
        self._member_num = data_proto.member_count
        self._post_num = data_proto.thread_count
        self._is_followed = bool(data_proto.is_like)
        return self

    def __repr__(self) -> str:
        return str(
            {
                'fid': self._fid,
                'fname': self._fname,
                'member_num': self._member_num,
                'post_num': self._post_num,
            }
        )

    def __eq__(self, obj: "SquareForum") -> bool:
        return self._fid == obj._fid

    def __hash__(self) -> int:
        return self._fid

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

    @property
    def member_num(self) -> int:
        """
        吧会员数
        """

        return self._member_num

    @property
    def post_num(self) -> int:
        """
        发帖量
        """

        return self._post_num

    @property
    def is_followed(self) -> bool:
        """
        是否已关注
        """

        return self._is_followed


class Page_square(object):
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

    def _init(self, data_proto: TypeMessage) -> "Page_square":
        self._page_size = data_proto.page_size
        self._current_page = data_proto.current_page
        self._total_page = data_proto.total_page
        self._total_count = data_proto.total_count
        self._has_more = bool(data_proto.has_more)
        self._has_prev = bool(data_proto.has_prev)
        return self

    def _init_null(self) -> "Page_square":
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


class SquareForums(Containers[SquareForum]):
    """
    吧广场列表

    Attributes:
        _objs (list[SquareForum]): 吧广场列表

        page (Page_square): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def _init(self, data_proto: TypeMessage) -> "SquareForums":
        self._objs = [SquareForum()._init(_proto) for _proto in data_proto.forum_info]
        self._page = Page_square()._init(data_proto.page)
        return self

    def _init_null(self) -> "SquareForums":
        self._objs = []
        self._page = Page_square()._init_null()
        return self

    @property
    def page(self) -> Page_square:
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
