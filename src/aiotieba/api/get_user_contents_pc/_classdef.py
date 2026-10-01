from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import TYPE_CHECKING, Self

from ...enums import Gender, ObjType, PrivLike, PrivReply, ThreadType
from ...exception import TbErrorExt
from ...logging import get_logger as LOG
from .._classdef import Containers
from .._classdef.contents import (
    _IMAGEHASH_EXP,
    FragLink,
    FragText,
    FragUnknown,
    TypeFragment,
    TypeFragText,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


FragText_pcup = FragText
FragLink_pcup = FragLink


@dcs.dataclass
class FragEmoji_pcup:
    """
    表情碎片

    Attributes:
        id (str): 表情图片id
        desc (str): 表情描述
    """

    id: str = ""
    desc: str = ""

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        id_ = data_map["text"]
        desc = data_map.get("c", "")
        return FragEmoji_pcup(id_, desc)


@dcs.dataclass
class FragImage_pcup:
    """
    图像碎片

    Attributes:
        src (str): 小图链接 宽720px
        big_src (str): 大图链接 宽960px
        origin_src (str): 原图链接
        origin_size (int): 原图大小
        show_width (int): 图像在客户端预览显示的宽度
        show_height (int): 图像在客户端预览显示的高度
        hash (str): 百度图床hash
    """

    src: str = dcs.field(default="", repr=False)
    big_src: str = dcs.field(default="", repr=False)
    origin_src: str = dcs.field(default="", repr=False)
    origin_size: int = 0
    show_width: int = 0
    show_height: int = 0
    hash: str = ""

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        src = data_map["cdn_src"]
        big_src = data_map["big_cdn_src"]
        origin_src = data_map["origin_src"]
        origin_size = int(data_map.get("origin_size", 0))

        show_width, _, show_height = data_map.get("bsize", "").partition(",")
        show_width = int(show_width) if show_width else 0
        show_height = int(show_height) if show_height else 0

        if hash_obj := _IMAGEHASH_EXP.search(src):
            hash_ = hash_obj.group(1)
        else:
            hash_ = ""

        return FragImage_pcup(src, big_src, origin_src, origin_size, show_width, show_height, hash_)


@dcs.dataclass
class FragAt_pcup:
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

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        text = data_map["text"]
        user_id = int(data_map["uid"])
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        return FragAt_pcup(text, user_id, portrait)


@dcs.dataclass
class FragVideo_pcup:
    """
    视频碎片

    Attributes:
        src (str): 视频链接
        cover_src (str): 封面链接
        duration (int): 视频长度 以秒为单位
        width (int): 视频宽度
        height (int): 视频高度
    """

    src: str = ""
    cover_src: str = ""
    duration: int = 0
    width: int = 0
    height: int = 0

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        src = data_map["link"]
        cover_src = data_map["src"]
        duration = int(data_map.get("during_time", 0))
        width = int(data_map.get("width", 0))
        height = int(data_map.get("height", 0))
        return FragVideo_pcup(src, cover_src, duration, width, height)

    def __bool__(self) -> bool:
        return bool(self.width)


@dcs.dataclass
class FragVoice_pcup:
    """
    音频碎片

    Attributes:
        md5 (str): 音频md5
        duration (float): 音频长度 以秒为单位
    """

    md5: str = ""
    duration: float = 0.0

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        md5 = data_map["voice_md5"]
        duration = int(data_map["during_time"]) / 1000
        return FragVoice_pcup(md5, duration)

    def __bool__(self) -> bool:
        return bool(self.md5)


@dcs.dataclass
class Contents_pcup(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_pcup]): 表情碎片列表
        imgs (list[FragImage_pcup]): 图像碎片列表
        ats (list[FragAt_pcup]): @碎片列表
        links (list[FragLink_pcup]): 链接碎片列表
        video (FragVideo_pcup): 视频碎片
        voice (FragVoice_pcup): 音频碎片
    """

    texts: list[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: list[FragEmoji_pcup] = dcs.field(default_factory=list, repr=False)
    imgs: list[FragImage_pcup] = dcs.field(default_factory=list, repr=False)
    ats: list[FragAt_pcup] = dcs.field(default_factory=list, repr=False)
    links: list[FragLink_pcup] = dcs.field(default_factory=list, repr=False)
    video: FragVideo_pcup = dcs.field(default_factory=FragVideo_pcup, repr=False)
    voice: FragVoice_pcup = dcs.field(default_factory=FragVoice_pcup, repr=False)

    @staticmethod
    def from_json(content_maps: Sequence[Mapping]) -> Self:
        texts = []
        emojis = []
        imgs = []
        ats = []
        links = []
        video = FragVideo_pcup()
        voice = FragVoice_pcup()

        def _frags():
            for content_map in content_maps:
                _type = int(content_map["type"])
                # 0纯文本 9电话号 18话题 27百科词条 40梗百科
                if _type in [0, 9, 18, 27, 40]:
                    frag = FragText_pcup.from_json(content_map)
                    texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_pcup.from_json(content_map)
                    emojis.append(frag)
                    yield frag
                # 20:tid=5470214675
                elif _type in [3, 20]:
                    frag = FragImage_pcup.from_json(content_map)
                    imgs.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_pcup.from_json(content_map)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_pcup.from_json(content_map)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 5:  # video
                    nonlocal video
                    video = FragVideo_pcup.from_json(content_map)
                    yield video
                elif _type == 10:  # voice
                    nonlocal voice
                    voice = FragVoice_pcup.from_json(content_map)
                    yield voice
                else:
                    yield FragUnknown.from_json(content_map)

        objs = list(_frags())

        return Contents_pcup(objs, texts, emojis, imgs, ats, links, video, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class UserInfo_pcu:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        level (int): 吧内等级
        gender (Gender): 性别
        icons (list[str]): 印记信息

        is_bawu (bool): 是否吧务
        is_vip (bool): 是否会员
        priv_like (PrivLike): 关注吧列表的公开状态
        priv_reply (PrivReply): 帖子评论权限

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息

    Note:
        服务端对回复作者与主题帖作者下发的字段集不同\n
        回复作者不含level_id/iconinfo/is_bawu且is_mem恒为0\n
        主题帖作者不含level_id
    """

    user_id: int = 0
    portrait: str = ""
    user_name: str = ""
    nick_name_new: str = ""

    level: int = 0
    gender: Gender = Gender.UNKNOWN
    icons: list[str] = dcs.field(default_factory=list)

    is_bawu: bool = False
    is_vip: bool = False
    priv_like: PrivLike = PrivLike.PUBLIC
    priv_reply: PrivReply = PrivReply.ALL

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        user_id = int(data_map["id"])
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_map["name"]
        nick_name_new = data_map["name_show"]

        level = int(data_map.get("level_id", 0))
        gender = Gender(int(data_map.get("gender", 0)))
        icons = [name for i in data_map.get("iconinfo") or [] if (name := i.get("name"))]

        is_bawu = bool(data_map.get("is_bawu", 0))
        is_vip = int(data_map.get("is_mem", 0)) != 0
        priv_sets = data_map.get("priv_sets") or {}
        priv_like = PrivLike(priv_like) if (priv_like := int(priv_sets.get("like", 0))) else PrivLike.PUBLIC
        priv_reply = PrivReply(priv_reply) if (priv_reply := int(priv_sets.get("reply", 0))) else PrivReply.ALL

        return UserInfo_pcu(
            user_id,
            portrait,
            user_name,
            nick_name_new,
            level,
            gender,
            icons,
            is_bawu,
            is_vip,
            priv_like,
            priv_reply,
        )

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: UserInfo_pcu) -> bool:
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
class Forum_pcup:
    """
    父级贴吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名
        avatar (str): 贴吧头像链接
        member_num (int): 会员数
        post_num (int): 帖子数
        slogan (str): 一句话简介
        is_liked (bool): 是否已关注
    """

    fid: int = 0
    fname: str = ""
    avatar: str = dcs.field(default="", repr=False)
    member_num: int = 0
    post_num: int = 0
    slogan: str = ""
    is_liked: bool = False

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        fid = int(data_map["id"])
        fname = data_map["name"]
        avatar = data_map.get("avatar", "")
        member_num = int(data_map.get("member_num", 0))
        post_num = int(data_map.get("post_num", 0))
        slogan = data_map.get("slogan", "")
        is_liked = bool(data_map.get("is_liked", 0))
        return Forum_pcup(fid, fname, avatar, member_num, post_num, slogan, is_liked)

    def __bool__(self) -> bool:
        return bool(self.fid)


@dcs.dataclass
class Thread_pcup:
    """
    父级主题帖信息

    Attributes:
        contents (Contents_pcup): 首楼正文内容碎片列表
        title (str): 标题内容

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼回复pid
        user (UserInfo_pcu): 发布者的用户信息
        forum (Forum_pcup): 所在贴吧信息

        type (ThreadType): 帖子类型
        view_num (int): 浏览量
        reply_num (int): 回复数
        share_num (int): 分享数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间 10位时间戳 以秒为单位
        last_time (int): 最后回复时间 10位时间戳 以秒为单位
        is_good (bool): 是否精品帖
        is_top (bool): 是否置顶帖
        is_deleted (bool): 是否已删除
    """

    contents: Contents_pcup = dcs.field(default_factory=Contents_pcup)
    title: str = ""

    fid: int = 0
    fname: str = ""
    tid: int = 0
    pid: int = 0
    user: UserInfo_pcu = dcs.field(default_factory=UserInfo_pcu)
    forum: Forum_pcup = dcs.field(default_factory=Forum_pcup)

    type: ThreadType = ThreadType.UNKNOWN
    view_num: int = 0
    reply_num: int = 0
    share_num: int = 0
    agree: int = 0
    disagree: int = 0
    create_time: int = 0
    last_time: int = 0
    is_good: bool = False
    is_top: bool = False
    is_deleted: bool = False

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        contents = Contents_pcup.from_json(data_map.get("first_post_content") or [])
        title = data_map["title"]

        fid = int(data_map["fid"])
        fname = data_map["fname"]
        tid = int(data_map["tid"])
        pid = int(data_map["first_post_id"])
        user = UserInfo_pcu.from_json(data_map["author"])
        forum = Forum_pcup.from_json(data_map["forum_info"])

        thread_type = int(data_map["thread_type"])
        type_ = ThreadType(thread_type)
        if type_ == ThreadType.UNKNOWN:
            LOG().debug("Unknown thread type. tid=%d, type=%s", tid, thread_type)

        view_num = int(data_map["view_num"])
        reply_num = int(data_map["reply_num"])
        share_num = int(data_map["share_num"])
        agree_map = data_map["agree"]
        agree = int(agree_map["agree_num"])
        disagree = int(agree_map["disagree_num"])
        create_time = int(data_map["create_time"])
        last_time = int(data_map["last_time_int"])
        is_good = bool(data_map["is_good"])
        is_top = bool(data_map["is_top"])
        is_deleted = bool(data_map["is_deleted"])

        return Thread_pcup(
            contents,
            title,
            fid,
            fname,
            tid,
            pid,
            user,
            forum,
            type_,
            view_num,
            reply_num,
            share_num,
            agree,
            disagree,
            create_time,
            last_time,
            is_good,
            is_top,
            is_deleted,
        )

    def __eq__(self, obj: Thread_pcup) -> bool:
        return self.tid == obj.tid

    def __hash__(self) -> int:
        return self.tid

    def __bool__(self) -> bool:
        return bool(self.tid)

    @cached_property
    def text(self) -> str:
        if self.title:
            text = f"{self.title}\n{self.contents.text}"
        else:
            text = self.contents.text
        return text

    @property
    def author_id(self) -> int:
        return self.user.user_id


@dcs.dataclass
class PcUserPost:
    """
    用户历史回复信息

    Attributes:
        contents (Contents_pcup): 正文内容碎片列表

        fid (int): 所在吧id
        tid (int): 所在主题帖id
        ppid (int): 父级回复id 仅楼中楼有效 楼层回复恒为0
        pid (int): 回复id 主题帖为主题帖id 回复为楼层pid 楼中楼为楼中楼pid
        user (UserInfo_pcu): 发布者的用户信息
        thread (Thread_pcup): 父级主题帖信息

        obj_type (ObjType): 帖子对象类型
        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    contents: Contents_pcup = dcs.field(default_factory=Contents_pcup)

    fid: int = 0
    tid: int = 0
    ppid: int = 0
    pid: int = 0
    user: UserInfo_pcu = dcs.field(default_factory=UserInfo_pcu)
    thread: Thread_pcup = dcs.field(default_factory=Thread_pcup)

    obj_type: ObjType = ObjType.UNKNOWN

    create_time: int = 0

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        thread = Thread_pcup.from_json(data_map["thread_info"])

        post_info = data_map.get("post_info")
        if post_info:
            contents = Contents_pcup.from_json(post_info.get("content") or [])
            # quote_id仅在回复为楼中楼时下发 其值为所在楼层的pid 楼层回复恒为0
            ppid = int(post_info.get("quote_id") or 0)
            pid = int(post_info["id"])
            user = UserInfo_pcu.from_json(post_info["author"])
            create_time = int(post_info["time"])
        else:
            contents = thread.contents
            ppid = 0
            pid = thread.pid
            user = thread.user
            create_time = thread.create_time

        obj_type = ObjType(int(data_map["type"]))

        return PcUserPost(contents, thread.fid, thread.tid, ppid, pid, user, thread, obj_type, create_time)

    def __eq__(self, obj: PcUserPost) -> bool:
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
class PcUserPosts(TbErrorExt, Containers[PcUserPost]):
    """
    用户历史回复信息列表

    Attributes:
        objs (list[PcUserPost]): 用户历史回复信息列表
        err (Exception | None): 捕获的异常
    """

    @staticmethod
    def from_json(data_map: Mapping) -> Self:
        objs = [PcUserPost.from_json(m) for m in data_map.get("list") or []]

        return PcUserPosts(objs)
