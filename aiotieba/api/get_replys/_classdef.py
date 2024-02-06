import dataclasses as dcs
from functools import cached_property

from ...enums import PrivLike, PrivReply
from ...exception import TbErrorExt
from .._classdef import Containers, TypeMessage


@dcs.dataclass
class UserInfo_reply:
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
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_reply":
        user_id = data_proto.id
        portrait = data_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.name
        nick_name_new = data_proto.name_show
        priv_like = PrivLike(priv_like) if (priv_like := data_proto.priv_sets.like) else PrivLike.PUBLIC
        priv_reply = PrivReply(priv_reply) if (priv_reply := data_proto.priv_sets.reply) else PrivReply.ALL
        return UserInfo_reply(user_id, portrait, user_name, nick_name_new, priv_like, priv_reply)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_reply") -> bool:
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
class UserInfo_reply_p:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    user_name: str = ''
    nick_name_new: str = ''

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_reply_p":
        user_id = data_proto.id
        user_name = data_proto.name
        nick_name_new = data_proto.name_show
        return UserInfo_reply_p(user_id, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or str(self.user_id)

    def __eq__(self, obj: "UserInfo_reply_p") -> bool:
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
        return self.user_name if self.user_name else f"{self.nick_name_new}/{self.user_id}"


@dcs.dataclass
class UserInfo_reply_t:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    nick_name_new: str = ''

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_reply_t":
        user_id = data_proto.id
        portrait = data_proto.portrait
        nick_name_new = data_proto.name_show
        return UserInfo_reply_t(user_id, portrait, nick_name_new)

    def __str__(self) -> str:
        return self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_reply_t") -> bool:
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
        return self.nick_name_new

    @cached_property
    def log_name(self) -> str:
        return str(self.user_id) if not self.portrait else f"{self.nick_name_new}/{self.portrait}"


@dcs.dataclass
class Reply:
    """
    回复信息
    Attributes:
        text (str): 文本内容

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        ppid (int): 所在楼层pid
        pid (int): 回复id
        user (UserInfo_reply): 发布者的用户信息
        author_id (int): 发布者的user_id
        post_user (UserInfo_reply_p): 楼层用户信息
        thread_user (UserInfo_reply_t): 楼主用户信息

        is_comment (bool): 是否楼中楼
        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    text: str = ""

    fname: str = ''
    tid: int = 0
    ppid: int = 0
    pid: int = 0
    user: UserInfo_reply = dcs.field(default_factory=UserInfo_reply)
    post_user: UserInfo_reply_p = dcs.field(default_factory=UserInfo_reply_p)
    thread_user: UserInfo_reply_t = dcs.field(default_factory=UserInfo_reply_t)

    is_comment: bool = False
    create_time: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Reply":
        text = data_proto.content
        fname = data_proto.fname
        tid = data_proto.thread_id
        ppid = data_proto.quote_pid
        pid = data_proto.post_id
        user = UserInfo_reply.from_tbdata(data_proto.replyer)
        post_user = UserInfo_reply_p.from_tbdata(data_proto.quote_user)
        thread_user = UserInfo_reply_t.from_tbdata(data_proto.thread_author_user)
        is_comment = bool(data_proto.is_floor)
        create_time = data_proto.time
        return Reply(text, fname, tid, ppid, pid, user, post_user, thread_user, is_comment, create_time)

    def __eq__(self, obj: "Reply") -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @property
    def author_id(self) -> int:
        return self.user.user_id


@dcs.dataclass
class Page_reply:
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
    def from_tbdata(data_proto: TypeMessage) -> "Page_reply":
        current_page = data_proto.current_page
        has_more = bool(data_proto.has_more)
        has_prev = bool(data_proto.has_prev)
        return Page_reply(current_page, has_more, has_prev)


@dcs.dataclass
class Replys(TbErrorExt, Containers[Reply]):
    """
    收到回复列表

    Attributes:
        objs (list[Reply]): 收到回复列表
        err (Exception | None): 捕获的异常

        page (Page_reply): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_reply = dcs.field(default_factory=Page_reply)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Replys":
        objs = [Reply.from_tbdata(p) for p in data_proto.reply_list]
        page = Page_reply.from_tbdata(data_proto.page)
        return Replys(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
