from typing import Optional

from .._classdef import Containers, TypeMessage


class BlacklistOldUser(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称

        until_time (int): 解禁时间

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
        '_nick_name_old',
        '_until_time',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._user_id = data_proto.user_id
        if '?' in (portrait := data_proto.portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.user_name
        self._nick_name_old = data_proto.name_show

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

    def __eq__(self, obj: "BlacklistOldUser") -> bool:
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
            唯一 不可变 不可为空\n
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
            唯一 可变 可为空\n
            请注意与用户昵称区分
        """

        return self._user_name

    @property
    def nick_name_old(self) -> str:
        """
        旧版昵称
        """

        return self._nick_name_old

    @property
    def until_time(self) -> int:
        """
        解禁时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._until_time

    @property
    def nick_name(self) -> str:
        """
        用户昵称
        """

        return self._nick_name_old

    @property
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        if self._user_name:
            return self._user_name
        elif self._portrait:
            return f"{self._nick_name_old}/{self._portrait}"
        else:
            return str(self._user_id)


class Page_blacklist(object):
    """
    页信息

    Attributes:
        current_page (int): 当前页码

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = [
        '_current_page',
        '_has_more',
        '_has_prev',
    ]

    def _init(self, data_proto: TypeMessage) -> "Page_blacklist":
        self._current_page = data_proto.current_page
        self._has_more = bool(data_proto.has_more)
        self._has_prev = bool(data_proto.has_prev)
        return self

    def _init_null(self) -> "Page_blacklist":
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


class BlacklistOldUsers(Containers[BlacklistOldUser]):
    """
    旧版用户黑名单列表

    Attributes:
        _objs (list[BlacklistOldUser]): 旧版用户黑名单列表

        page (Page_blacklist): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def __init__(self, data_proto: Optional[TypeMessage] = None) -> None:
        if data_proto:
            self._objs = [BlacklistOldUser(p) for p in data_proto.mute_user]
            self._page = Page_blacklist()._init(data_proto.page)
        else:
            self._objs = []
            self._page = Page_blacklist()._init_null()

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._page._has_more
