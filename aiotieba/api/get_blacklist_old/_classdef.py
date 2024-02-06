import dataclasses as dcs
from functools import cached_property

from ...exception import TbErrorExt
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

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_old

    @cached_property
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

    current_page: int = 0

    has_more: bool = False
    has_prev: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Page_blacklist":
        current_page = data_proto.current_page
        has_more = bool(data_proto.has_more)
        has_prev = bool(data_proto.has_prev)
        return Page_blacklist(current_page, has_more, has_prev)


@dcs.dataclass
class BlacklistOldUsers(TbErrorExt, Containers[BlacklistOldUser]):
    """
    旧版用户黑名单列表

    Attributes:
        objs (list[BlacklistOldUser]): 旧版用户黑名单列表
        err (Exception | None): 捕获的异常

        page (Page_blacklist): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_blacklist = dcs.field(default_factory=Page_blacklist)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "BlacklistOldUsers":
        objs = [BlacklistOldUser.from_tbdata(p) for p in data_proto.mute_user]
        page = Page_blacklist.from_tbdata(data_proto.page)
        return BlacklistOldUsers(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
