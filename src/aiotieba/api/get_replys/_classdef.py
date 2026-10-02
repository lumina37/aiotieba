from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import Self

from ...enums import ObjType, PrivLike, PrivReply
from ...exception import TbErrorExt
from .._classdef import Containers, TypeMessage
from .._classdef.contents import (
    FragAt,
    FragEmoji,
    FragText,
    FragUnknown,
    TypeFragment,
    TypeFragText,
)

FragText_rep = FragText
FragEmoji_rep = FragEmoji
FragAt_rep = FragAt


@dcs.dataclass
class Contents_rep(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_rep]): 表情碎片列表
        ats (list[FragAt_rep]): @碎片列表
    """

    texts: list[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: list[FragEmoji_rep] = dcs.field(default_factory=list, repr=False)
    ats: list[FragAt_rep] = dcs.field(default_factory=list, repr=False)

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        content_protos = data_proto.content

        texts = []
        emojis = []
        ats = []

        def _frags():
            for proto in content_protos:
                _type = proto.type
                if _type == 0:
                    frag = FragText_rep.from_proto(proto)
                    texts.append(frag)
                    yield frag
                elif _type == 2:
                    frag = FragEmoji_rep.from_proto(proto)
                    emojis.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_rep.from_proto(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                else:
                    yield FragUnknown.from_proto(proto)

        objs = list(_frags())

        return cls(objs, texts, emojis, ats)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


def _strip_quote_header(contents: Contents_rep) -> None:
    objs = contents.objs
    if len(objs) < 2 or not isinstance(objs[0], FragAt_rep):
        return

    text_frag = objs[1]
    if not isinstance(text_frag, FragText_rep) or not text_frag.text.startswith(": "):
        return

    text_frag.text = text_frag.text.removeprefix(": ")
    skip = 1 if text_frag.text else 2

    contents.objs = objs[skip:]
    contents.texts = contents.texts[skip:]
    contents.ats = contents.ats[1:]


@dcs.dataclass
class UserInfo_rep:
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
    portrait: str = ""
    user_name: str = ""
    nick_name_new: str = ""

    priv_like: PrivLike = PrivLike.PUBLIC
    priv_reply: PrivReply = PrivReply.ALL

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        user_id = data_proto.id
        portrait = data_proto.portrait
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.name
        nick_name_new = data_proto.name_show
        priv_like = PrivLike(priv_like) if (priv_like := data_proto.priv_sets.like) else PrivLike.PUBLIC
        priv_reply = PrivReply(priv_reply) if (priv_reply := data_proto.priv_sets.reply) else PrivReply.ALL
        return cls(user_id, portrait, user_name, nick_name_new, priv_like, priv_reply)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: UserInfo_rep) -> bool:
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
class UserInfo_rep_p:
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
    user_name: str = ""
    nick_name_new: str = ""

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        user_id = data_proto.id
        user_name = data_proto.name
        nick_name_new = data_proto.name_show
        return cls(user_id, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or str(self.user_id)

    def __eq__(self, obj: UserInfo_rep_p) -> bool:
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
        return self.user_name or f"{self.nick_name_new}/{self.user_id}"


@dcs.dataclass
class UserInfo_rep_t:
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
    portrait: str = ""
    nick_name_new: str = ""

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        user_id = data_proto.id
        portrait = data_proto.portrait
        nick_name_new = data_proto.name_show
        return cls(user_id, portrait, nick_name_new)

    def __str__(self) -> str:
        return self.portrait or str(self.user_id)

    def __eq__(self, obj: UserInfo_rep_t) -> bool:
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
class Post_rep:
    """
    父级回复信息

    Attributes:
        pid (int): 父级回复id
        contents (Contents_rep): 正文内容碎片列表
        user (UserInfo_rep_p): 发布者的用户信息
    """

    pid: int = 0
    contents: Contents_rep = dcs.field(default_factory=Contents_rep)
    user: UserInfo_rep_p = dcs.field(default_factory=UserInfo_rep_p)

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        pid = data_proto.quote_pid

        new_floor_infos = data_proto.new_floor_info
        contents = Contents_rep()
        if len(new_floor_infos) > 2:
            contents = Contents_rep.from_proto(new_floor_infos[-2])
            _strip_quote_header(contents)

        user = UserInfo_rep_p.from_proto(data_proto.quote_user)

        return cls(pid, contents, user)

    def __bool__(self) -> bool:
        return bool(self.contents)


@dcs.dataclass
class Thread_rep:
    """
    父级主题帖信息

    Attributes:
        tid (int): 父级主题帖id
        contents (Contents_rep): 正文内容碎片列表
        user (UserInfo_rep_t): 发布者的用户信息
    """

    tid: int = 0
    contents: Contents_rep = dcs.field(default_factory=Contents_rep)
    user: UserInfo_rep_t = dcs.field(default_factory=UserInfo_rep_t)

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        tid = data_proto.thread_id

        new_floor_infos = data_proto.new_floor_info
        contents = Contents_rep()
        if len(new_floor_infos) > 1:
            contents = Contents_rep.from_proto(new_floor_infos[0])
            _strip_quote_header(contents)

        user = UserInfo_rep_t.from_proto(data_proto.thread_author_user)

        return cls(tid, contents, user)

    def __bool__(self) -> bool:
        return bool(self.contents)


@dcs.dataclass
class Reply:
    """
    回复信息
    Attributes:
        text (str): 文本内容
        contents (Contents_rep): 正文内容碎片列表

        fname (str): 所在贴吧名
        pid (int): 回复id
        user (UserInfo_rep): 发布者的用户信息
        author_id (int): 发布者的user_id
        post (Post_rep): 父级回复信息
        thread (Thread_rep): 父级主题帖信息

        obj_type (ObjType): 帖子对象类型
        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    contents: Contents_rep = dcs.field(default_factory=Contents_rep)

    fname: str = ""
    pid: int = 0
    user: UserInfo_rep = dcs.field(default_factory=UserInfo_rep)
    post: Post_rep = dcs.field(default_factory=Post_rep)
    thread: Thread_rep = dcs.field(default_factory=Thread_rep)

    obj_type: ObjType = ObjType.UNKNOWN
    create_time: int = 0

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        new_floor_infos = data_proto.new_floor_info
        contents = Contents_rep.from_proto(new_floor_infos[-1]) if new_floor_infos else Contents_rep()
        fname = data_proto.fname
        pid = data_proto.post_id
        user = UserInfo_rep.from_proto(data_proto.replyer)
        post = Post_rep.from_proto(data_proto)
        thread = Thread_rep.from_proto(data_proto)
        obj_type = ObjType.COMMENT if data_proto.is_floor else ObjType.POST
        create_time = data_proto.time
        return cls(contents, fname, pid, user, post, thread, obj_type, create_time)

    def __eq__(self, obj: Reply) -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @property
    def text(self) -> str:
        return self.contents.text

    @property
    def author_id(self) -> int:
        return self.user.user_id


@dcs.dataclass
class Page_rep:
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

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        current_page = data_proto.current_page
        has_more = bool(data_proto.has_more)
        has_prev = bool(data_proto.has_prev)
        return cls(current_page, has_more, has_prev)


@dcs.dataclass
class Replys(TbErrorExt, Containers[Reply]):
    """
    收到回复列表

    Attributes:
        objs (list[Reply]): 收到回复列表
        err (Exception | None): 捕获的异常

        page (Page_rep): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_rep = dcs.field(default_factory=Page_rep)

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        objs = [Reply.from_proto(p) for p in data_proto.reply_list]
        page = Page_rep.from_proto(data_proto.page)
        return cls(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
