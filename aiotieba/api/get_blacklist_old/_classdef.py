import dataclasses as dcs
from typing import Optional

from .._classdef import Containers, TypeMessage


@dcs.dataclass
class BlacklistOldUser:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称

        until_time (int): 解禁时间 10位时间戳 以秒为单位

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name_old: str = ''

    until_time: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "BlacklistOldUser":
        user_id = data_proto.user_id
        portrait = data_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.user_name
        nick_name_old = data_proto.name_show
        until_time = data_proto.mute_time
        return BlacklistOldUser(user_id, portrait, user_name, nick_name_old, until_time)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "BlacklistOldUser") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __int__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_old

    @property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_old}/{self.portrait}"
        else:
            return str(self.user_id)


@dcs.dataclass
class Page_blacklist:
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
            self.objs = [BlacklistOldUser(p) for p in data_proto.mute_user]
            self._page = Page_blacklist()._init(data_proto.page)
        else:
            self.objs = []
            self._page = Page_blacklist()._init_null()

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._page._has_more
