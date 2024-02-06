import dataclasses as dcs
from functools import cached_property
from typing import Mapping

from ...enums import PrivLike, PrivReply
from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class Page_at:
    """
    页信息

    Attributes:
        current_page (int): 当前页码

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    current_page: int = 0

    has_more: bool = False
    has_prev: int = False

    @staticmethod
    def from_dict(data_map: Mapping) -> "Page_at":
        current_page = int(data_map['current_page'])
        has_more = bool(int(data_map['has_more']))
        has_prev = bool(int(data_map['has_prev']))
        return Page_at(current_page, has_more, has_prev)


@dcs.dataclass
class UserInfo_at:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        priv_like (PrivLike): 关注吧列表的公开状态
        priv_reply (PrivReply): 帖子评论权限

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name_new: str = ''

    priv_like: PrivLike = PrivLike.PUBLIC
    priv_reply: PrivReply = PrivReply.ALL

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "UserInfo_at":
        user_id = int(data_map['id'])
        portrait = data_map['portrait']
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_map['name']
        nick_name_new = data_map['name_show']
        if priv_sets := data_map['priv_sets']:
            priv_like = PrivLike(int(priv_sets.get('like', 1)))
            priv_reply = PrivReply(int(priv_sets.get('reply', 1)))
        else:
            priv_like = PrivLike.PUBLIC
            priv_reply = PrivReply.ALL

        return UserInfo_at(user_id, portrait, user_name, nick_name_new, priv_like, priv_reply)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_at") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_new}/{self.portrait}"
        else:
            return str(self.user_id)


@dcs.dataclass
class At:
    """
    @信息

    Attributes:
        text (str): 文本内容

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo_at): 发布者的用户信息
        author_id (int): 发布者的user_id

        is_comment (bool): 是否楼中楼
        is_thread (bool): 是否主题帖

        create_time (int): 创建时间
    """

    text: str = ""

    fname: str = ''
    tid: int = 0
    pid: int = 0
    user: UserInfo_at = dcs.field(default_factory=UserInfo_at)

    is_comment: bool = False
    is_thread: bool = False

    create_time: int = 0

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "At":
        text = data_map['content']
        fname = data_map['fname']
        tid = int(data_map['thread_id'])
        pid = int(data_map['post_id'])
        user = UserInfo_at.from_tbdata(data_map['replyer'])
        is_comment = bool(int(data_map['is_floor']))
        is_thread = bool(int(data_map['is_first_post']))
        create_time = int(data_map['time'])
        return At(text, fname, tid, pid, user, is_comment, is_thread, create_time)

    def __eq__(self, obj: "At") -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @property
    def author_id(self) -> int:
        return self.user.user_id


@dcs.dataclass
class Ats(TbErrorExt, Containers[At]):
    """
    @信息列表

    Attributes:
        objs (list[At]): @信息列表
        err (Exception | None): 捕获的异常

        page (Page_at): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_at = dcs.field(default_factory=Page_at)

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Ats":
        objs = [At.from_tbdata(m) for m in data_map.get('at_list', [])]
        page = Page_at.from_dict(data_map['page'])
        return Ats(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
