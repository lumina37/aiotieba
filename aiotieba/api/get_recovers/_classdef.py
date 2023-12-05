from typing import Mapping, Optional

from .._classdef import Containers


class UserInfo_rec(object):
    """
    用户信息

    Attributes:
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_portrait',
        '_user_name',
        '_nick_name_new',
    ]

    def _init(self, data_map: Mapping) -> "UserInfo_rec":
        if '?' in (portrait := data_map['portrait']):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_map['user_name']
        self._nick_name_new = data_map['user_nickname']
        return self

    def _init_null(self) -> "UserInfo_rec":
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
        return self

    def __str__(self) -> str:
        return self._user_name or self._portrait

    def __repr__(self) -> str:
        return str(
            {
                'portrait': self._portrait,
                'show_name': self.show_name,
            }
        )

    def __eq__(self, obj: "UserInfo_rec") -> bool:
        return self._portrait == obj._portrait

    def __hash__(self) -> int:
        return hash(self._portrait)

    def __int__(self) -> int:
        return hash(self._portrait)

    def __bool__(self) -> bool:
        return bool(self._portrait)

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
            唯一 可变 可为空\n
            请注意与用户昵称区分
        """

        return self._user_name

    @property
    def nick_name_new(self) -> str:
        """
        新版昵称
        """

        return self._nick_name_new

    @property
    def nick_name(self) -> str:
        """
        用户昵称
        """

        return self._nick_name_new

    @property
    def show_name(self) -> str:
        """
        显示名称
        """

        return self._nick_name_new or self._user_name

    @property
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        return self._user_name if self._user_name else f"{self._nick_name_new}/{self._portrait}"


class Recover(object):
    """
    待恢复帖子信息

    Attributes:
        text (str): 文本内容
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo_rec): 发布者的用户信息
        op_show_name (str): 操作人显示名称
        op_time (int): 操作时间

        is_floor (bool): 是否为楼中楼
        is_hide (bool): 是否为屏蔽
    """

    __slots__ = [
        '_text',
        '_tid',
        '_pid',
        '_user',
        '_is_floor',
        '_is_hide',
        '_op_show_name',
        '_op_time',
    ]

    def __init__(self, data_map: Mapping) -> None:
        thread_info = data_map['thread_info']
        self._tid = int(thread_info['tid'])
        if post_info := data_map['post_info']:
            self._text = post_info['abstract']
            self._pid = int(post_info['pid'])
            self._user = UserInfo_rec()._init(post_info)
        else:
            self._text = thread_info['abstract']
            self._pid = 0
            self._user = UserInfo_rec()._init(thread_info)
        self._is_floor = bool(data_map['is_foor'])  # 百度的Code Review主要起到一个装饰的作用
        self._is_hide = bool(int(data_map['is_frs_mask']))
        self._op_show_name = data_map['op_info']['name']
        self._op_time = int(data_map['op_info']['time'])

    def __repr__(self) -> str:
        return str(
            {
                'text': self._text,
                'tid': self._tid,
                'pid': self._pid,
                'user': self._user.show_name,
                'is_floor': self._is_floor,
                'is_hide': self._is_hide,
                'op_show_name': self._op_show_name,
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

        Note:
            若为主题帖则该字段为0
        """

        return self._pid

    @property
    def is_floor(self) -> bool:
        """
        是否为楼中楼
        """

        return self._is_floor

    @property
    def is_hide(self) -> bool:
        """
        是否为屏蔽
        """

        return self._is_hide

    @property
    def op_show_name(self) -> str:
        """
        操作人显示名称
        """

        return self._op_show_name

    @property
    def op_time(self) -> int:
        """
        操作时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._op_time


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
        self._page_size = data_map['rn']
        self._current_page = data_map['pn']
        self._has_more = data_map['has_more']
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

    def __init__(self, data_map: Optional[Mapping] = None) -> None:
        if data_map:
            self._objs = [Recover(t) for t in data_map['data']['thread_list']]
            self._page = Page_recover()._init(data_map['data']['page'])
        else:
            self._objs = []
            self._page = Page_recover()._init_null()

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._page._has_more
