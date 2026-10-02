from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import TYPE_CHECKING, Self

from ...enums import ContentType, PrivLike, PrivReply
from ...exception import TbErrorExt
from .._classdef import Containers
from .._classdef.contents import (
    _IMAGEHASH_EXP,
    FragLink,
    FragText,
    TypeFragment,
    TypeFragText,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

FragLink_at = FragLink
FragText_at = FragText


@dcs.dataclass
class FragEmoji_at:
    """
    表情碎片

    Attributes:
        id (str): 表情图片id
        desc (str): 表情描述
    """

    id: str = ""
    desc: str = ""

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        id_ = data_map["text"]
        desc = data_map["c"]
        return cls(id_, desc)


@dcs.dataclass
class FragImage_at:
    """
    图像碎片

    Attributes:
        src (str): 小图链接
        origin_size (int): 原图大小
        show_width (int): 图像在客户端预览显示的宽度
        show_height (int): 图像在客户端预览显示的高度
        hash (str): 百度图床hash
    """

    src: str = dcs.field(default="", repr=False)
    origin_size: int = 0
    show_width: int = 0
    show_height: int = 0
    hash: str = ""

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        src = data_map["src"]
        origin_size = int(data_map["size"])

        show_width, _, show_height = data_map["bsize"].partition(",")
        show_width = int(show_width)
        show_height = int(show_height)

        if hash_obj := _IMAGEHASH_EXP.search(src):
            hash_ = hash_obj.group(1)
        else:
            hash_ = ""

        return cls(src, origin_size, show_width, show_height, hash_)


@dcs.dataclass
class FragAt_at:
    """
    @碎片

    Attributes:
        text (str): 被@用户的昵称 含@
        user_id (int): 被@用户的user_id
        portrait (str): 被@用户的portrait
    """

    text: str = ""
    user_id: int = 0
    portrait: str = ""

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        text = data_map["text"]
        user_id = int(data_map["uid"])
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        return cls(text, user_id, portrait)


@dcs.dataclass
class Contents_at(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_at]): 表情碎片列表
        imgs (list[FragImage_at]): 图像碎片列表
        ats (list[FragAt_at]): @碎片列表
        links (list[FragLink_at]): 链接碎片列表
    """

    texts: list[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: list[FragEmoji_at] = dcs.field(default_factory=list, repr=False)
    imgs: list[FragImage_at] = dcs.field(default_factory=list, repr=False)
    ats: list[FragAt_at] = dcs.field(default_factory=list, repr=False)
    links: list[FragLink_at] = dcs.field(default_factory=list, repr=False)

    @classmethod
    def from_json(cls, content_maps: Sequence[Mapping]) -> Self:
        texts = []
        emojis = []
        imgs = []
        ats = []
        links = []

        def _frags():
            for data_map in content_maps:
                if "src" in data_map:
                    frag = FragImage_at.from_json(data_map)
                    imgs.append(frag)
                    yield frag
                elif "link" in data_map:
                    frag = FragLink_at.from_json(data_map)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif int(data_map["type"]) == 4:
                    frag = FragAt_at.from_json(data_map)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif int(data_map["type"]) == 2:
                    frag = FragEmoji_at.from_json(data_map)
                    emojis.append(frag)
                    yield frag
                else:
                    frag = FragText_at.from_json(data_map)
                    texts.append(frag)
                    yield frag

        objs = list(_frags())

        return cls(objs, texts, emojis, imgs, ats, links)

    @cached_property
    def text(self) -> str:
        return "".join(frag.text for frag in self.texts)


def _strip_quote_header(contents: Contents_at) -> None:
    objs = contents.objs
    if len(objs) < 2 or not isinstance(objs[0], FragAt_at):
        return

    text_frag = objs[1]
    if not isinstance(text_frag, FragText_at) or not text_frag.text.startswith(": "):
        return

    text_frag.text = text_frag.text.removeprefix(": ")
    skip = 1 if text_frag.text else 2

    contents.objs = objs[skip:]
    contents.texts = contents.texts[skip:]
    contents.ats = contents.ats[1:]


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
    has_prev: bool = False

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        current_page = int(data_map["current_page"])
        has_more = bool(int(data_map["has_more"]))
        has_prev = bool(int(data_map["has_prev"]))
        return cls(current_page, has_more, has_prev)


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
    portrait: str = ""
    user_name: str = ""
    nick_name_new: str = ""

    priv_like: PrivLike = PrivLike.PUBLIC
    priv_reply: PrivReply = PrivReply.ALL

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user_id = int(data_map["id"])
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_map["name"]
        nick_name_new = data_map["name_show"]
        if priv_sets := data_map["priv_sets"]:
            priv_like = PrivLike(int(priv_sets.get("like", 1)))
            priv_reply = PrivReply(int(priv_sets.get("reply", 1)))
        else:
            priv_like = PrivLike.PUBLIC
            priv_reply = PrivReply.ALL

        return cls(user_id, portrait, user_name, nick_name_new, priv_like, priv_reply)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: UserInfo_at) -> bool:
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
class UserInfo_at_p:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ""
    user_name: str = ""
    nick_name_new: str = ""

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user_id = int(data_map["id"])
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_map["name"]
        nick_name_new = data_map["name_show"]
        return cls(user_id, portrait, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: UserInfo_at_p) -> bool:
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
class UserInfo_at_t:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ""
    user_name: str = ""
    nick_name_new: str = ""

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        user_id = int(data_map["id"])
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_map["name"]
        nick_name_new = data_map["name_show"]
        return cls(user_id, portrait, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: UserInfo_at_t) -> bool:
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
class Post_at:
    """
    父级回复信息

    Attributes:
        pid (int): 父级回复id
        contents (Contents_at): 正文内容碎片列表
        user (UserInfo_at_p): 发布者的用户信息
    """

    pid: int = 0
    contents: Contents_at = dcs.field(default_factory=Contents_at)
    user: UserInfo_at_p = dcs.field(default_factory=UserInfo_at_p)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        pid = int(data_map.get("quote_pid") or 0)

        new_floor_infos = data_map["new_floor_info"]
        contents = Contents_at()
        if len(new_floor_infos) > 2:
            contents = Contents_at.from_json(new_floor_infos[-2]["content"])
            _strip_quote_header(contents)

        user = UserInfo_at_p.from_json(data_map["quote_user"])
        return cls(pid, contents, user)

    def __bool__(self) -> bool:
        return bool(self.contents)


@dcs.dataclass
class Thread_at:
    """
    父级主题帖信息

    Attributes:
        tid (int): 父级主题帖id
        contents (Contents_at): 主题帖内容碎片列表
        user (UserInfo_at_t): 发布者的用户信息
    """

    tid: int = 0
    contents: Contents_at = dcs.field(default_factory=Contents_at)
    user: UserInfo_at_t = dcs.field(default_factory=UserInfo_at_t)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        tid = int(data_map["thread_id"])
        new_floor_infos = data_map["new_floor_info"]
        contents = Contents_at()
        if new_floor_infos:
            contents = Contents_at.from_json(new_floor_infos[0]["content"])
            _strip_quote_header(contents)
        user = UserInfo_at_t.from_json(data_map["thread_author_user"])
        return cls(tid, contents, user)

    def __bool__(self) -> bool:
        return bool(self.contents)


@dcs.dataclass
class At:
    """
    @信息

    Attributes:
        text (str): 文本内容

        fname (str): 所在贴吧名
        fid (int): 所在贴吧id
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo_at): 发布者的用户信息
        author_id (int): 发布者的user_id
        post (Post_at): 父级回复信息
        thread (Thread_at): 父级主题帖信息

        content_type (ContentType): 帖子对象类型

        create_time (int): 创建时间
    """

    text: str = ""

    fname: str = ""
    fid: int = 0
    tid: int = 0
    pid: int = 0
    user: UserInfo_at = dcs.field(default_factory=UserInfo_at)
    post: Post_at = dcs.field(default_factory=Post_at)
    thread: Thread_at = dcs.field(default_factory=Thread_at)

    content_type: ContentType = ContentType.UNKNOWN

    create_time: int = 0

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        text = data_map["content"]
        fname = data_map["fname"]
        fid = int(data_map["fid"])
        tid = int(data_map["thread_id"])
        pid = int(data_map["post_id"])
        user = UserInfo_at.from_json(data_map["replyer"])
        post = Post_at.from_json(data_map)
        thread = Thread_at.from_json(data_map)
        content_type = ContentType(int(data_map["type"]))
        create_time = int(data_map["time"])
        return cls(text, fname, fid, tid, pid, user, post, thread, content_type, create_time)

    def __eq__(self, obj: At) -> bool:
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

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        objs = [At.from_json(m) for m in data_map.get("at_list", [])]
        page = Page_at.from_json(data_map["page"])
        return cls(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
