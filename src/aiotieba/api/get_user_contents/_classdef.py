from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import Self

from ...enums import ContentType, ThreadType
from ...exception import TbErrorExt
from ...logging import get_logger as LOG
from .._classdef import Containers, TypeMessage, VoteInfo
from .._classdef.contents import (
    _IMAGEHASH_EXP,
    FragAt,
    FragEmoji,
    FragLink,
    FragText,
    FragUnknown,
    FragVideo,
    FragVoice,
    TypeFragment,
    TypeFragText,
)

FragText_up = FragText_ut = FragText
FragEmoji_ut = FragEmoji
FragAt_ut = FragAt
FragLink_up = FragLink_ut = FragLink
FragVideo_ut = FragVideo
FragVoice_ut = FragVoice

# post_type -> ContentType
_POST_TYPE2OBJ_TYPE = {0: ContentType.POST, 1: ContentType.COMMENT}


@dcs.dataclass
class FragVoice_up:
    """
    音频碎片

    Attributes:
        md5 (str): 音频md5
        duration (float): 音频长度 以秒为单位
    """

    md5: str = ""
    duration: float = 0.0

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        md5 = data_proto.voice_md5
        duration = int(data_proto.during_time) / 1000
        return cls(md5, duration)

    def __bool__(self) -> bool:
        return bool(self.md5)


@dcs.dataclass
class FragImage_up:
    """
    图像碎片

    Attributes:
        src (str): 图像链接
        hash (str): 百度图床hash
    """

    src: str = dcs.field(default="", repr=False)
    hash: str = ""

    @classmethod
    def _build(cls, src: str) -> Self:
        if hash_obj := _IMAGEHASH_EXP.search(src):
            hash_ = hash_obj.group(1)
        else:
            hash_ = ""
        return cls(src, hash_)

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        return cls._build(data_proto.src)


@dcs.dataclass
class FragAt_up:
    """
    @碎片

    Attributes:
        text (str): 被@用户的昵称 含@
        user_name (str): 被@用户的用户名
    """

    text: str = ""
    user_name: str = ""

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        return cls(data_proto.text, data_proto.un)


@dcs.dataclass
class Contents_up(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        imgs (list[FragImage_up]): 图像碎片列表
        ats (list[FragAt_up]): @碎片列表
        links (list[FragLink_up]): 链接碎片列表
        voice (FragVoice_up): 音频碎片
    """

    texts: list[TypeFragText] = dcs.field(default_factory=list, repr=False)
    imgs: list[FragImage_up] = dcs.field(default_factory=list, repr=False)
    ats: list[FragAt_up] = dcs.field(default_factory=list, repr=False)
    links: list[FragLink_up] = dcs.field(default_factory=list, repr=False)
    voice: FragVoice_up = dcs.field(default_factory=FragVoice_up, repr=False)

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        content_protos = data_proto.post_content

        texts = []
        imgs = []
        ats = []
        links = []
        voice = FragVoice_up()

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 摘要形式不区分图像type 图像以src标记
                if proto.src:
                    frag = FragImage_up.from_proto(proto)
                    imgs.append(frag)
                    yield frag
                # 0纯文本 9电话号 18话题 27百科词条 40梗百科
                elif _type in [0, 9, 18, 27, 40]:
                    frag = FragText_up.from_proto(proto)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_up.from_proto(proto)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_up.from_proto(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 10:  # voice
                    nonlocal voice
                    voice = FragVoice_up.from_proto(proto)
                    yield voice
                else:
                    yield FragUnknown.from_proto(proto)

        objs = list(_frags())

        return cls(objs, texts, imgs, ats, links, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class UserInfo_u:
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
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        user_id = data_proto.user_id
        portrait = data_proto.user_portrait
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.user_name
        nick_name_new = data_proto.name_show
        return cls(user_id, portrait, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: UserInfo_u) -> bool:
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
class Thread_up:
    """
    父级主题帖信息

    Attributes:
        fid (int): 所在吧id
        tid (int): 主题帖id
        title (str): 标题内容 已去除服务端为回复添加的`回复：`前缀

        type (ThreadType): 帖子类型
        view_num (int): 浏览量
        reply_num (int): 回复数
        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    fid: int = 0
    tid: int = 0
    title: str = ""

    type: ThreadType = ThreadType.UNKNOWN
    view_num: int = 0
    reply_num: int = 0
    create_time: int = 0

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        fid = data_proto.forum_id
        tid = data_proto.thread_id
        # 服务端仅为回复添加`回复：`前缀 主题帖自身不带
        title = data_proto.title.removeprefix("回复：")

        thread_type = data_proto.thread_type
        type_ = ThreadType(thread_type)
        if type_ == ThreadType.UNKNOWN:
            LOG().debug("Unknown thread type. tid=%d, type=%s", tid, thread_type)

        view_num = data_proto.freq_num
        reply_num = data_proto.reply_num
        create_time = data_proto.create_time

        return cls(fid, tid, title, type_, view_num, reply_num, create_time)

    def __eq__(self, obj: Thread_up) -> bool:
        return self.tid == obj.tid

    def __hash__(self) -> int:
        return self.tid

    def __bool__(self) -> bool:
        return bool(self.tid)


@dcs.dataclass
class UserPost:
    """
    用户历史回复信息

    Attributes:
        text (str): 文本内容
        contents (Contents_up): 正文内容碎片列表

        fid (int): 所在吧id
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo_u): 发布者的用户信息
        author_id (int): 发布者的user_id
        thread (Thread_up): 父级主题帖信息

        content_type (ContentType): 帖子对象类型

        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    contents: Contents_up = dcs.field(default_factory=Contents_up)

    fid: int = 0
    tid: int = 0
    pid: int = 0
    user: UserInfo_u = dcs.field(default_factory=UserInfo_u)
    thread: Thread_up = dcs.field(default_factory=Thread_up)

    content_type: ContentType = ContentType.UNKNOWN

    create_time: int = 0

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        contents = Contents_up.from_proto(data_proto)
        pid = data_proto.post_id
        content_type = _POST_TYPE2OBJ_TYPE[data_proto.post_type]
        create_time = data_proto.create_time
        return cls(contents, 0, 0, pid, None, Thread_up(), content_type, create_time)

    def __eq__(self, obj: UserPost) -> bool:
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
class UserPosts(Containers[UserPost]):
    """
    用户历史回复信息列表

    Attributes:
        objs (list[UserPost]): 用户历史回复信息列表

        fid (int): 所在吧id
        tid (int): 所在主题帖id
        thread (Thread_up): 父级主题帖信息
    """

    fid: int = 0
    tid: int = 0
    thread: Thread_up = dcs.field(default_factory=Thread_up)

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        fid = data_proto.forum_id
        tid = data_proto.thread_id
        thread = Thread_up.from_proto(data_proto)
        objs = [UserPost.from_proto(p) for p in data_proto.content]
        for upost in objs:
            upost.fid = fid
            upost.tid = tid
            upost.thread = thread
        return cls(objs, fid, tid, thread)


@dcs.dataclass
class UserPostss(TbErrorExt, Containers[UserPosts]):
    """
    用户历史回复信息列表的列表

    Attributes:
        objs (list[UserPosts]): 用户历史回复信息列表的列表
        err (Exception | None): 捕获的异常
    """

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        objs = [UserPosts.from_proto(p) for p in data_proto.post_list]
        if objs:
            user = UserInfo_u.from_proto(data_proto.post_list[0])
            for uposts in objs:
                for upost in uposts:
                    upost.user = user
        return cls(objs)


@dcs.dataclass
class FragImage_ut:
    """
    图像碎片

    Attributes:
        src (str): 小图链接 宽580px 一定是静态图
        big_src (str): 大图链接 宽960px
        origin_src (str): 原图链接
        origin_size (int): 原图大小
        width (int): 图像宽度
        height (int): 图像高度
        hash (str): 百度图床hash
    """

    src: str = dcs.field(default="", repr=False)
    big_src: str = dcs.field(default="", repr=False)
    origin_src: str = dcs.field(default="", repr=False)
    origin_size: int = 0
    width: int = 0
    height: int = 0
    hash: str = ""

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        src = data_proto.small_pic
        big_src = data_proto.big_pic
        origin_src = data_proto.origin_pic
        origin_size = data_proto.origin_size

        width = data_proto.width
        height = data_proto.height

        hash_ = _IMAGEHASH_EXP.search(src).group(1)

        return cls(src, big_src, origin_src, origin_size, width, height, hash_)


@dcs.dataclass
class Contents_ut(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_ut]): 表情碎片列表
        imgs (list[FragImage_ut]): 图像碎片列表
        ats (list[FragAt_ut]): @碎片列表
        links (list[FragLink_ut]): 链接碎片列表
        video (FragVideo_ut): 视频碎片
        voice (FragVoice_ut): 音频碎片
    """

    texts: list[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: list[FragEmoji_ut] = dcs.field(default_factory=list, repr=False)
    imgs: list[FragImage_ut] = dcs.field(default_factory=list, repr=False)
    ats: list[FragAt_ut] = dcs.field(default_factory=list, repr=False)
    links: list[FragLink_ut] = dcs.field(default_factory=list, repr=False)
    video: FragVideo_ut = dcs.field(default_factory=FragVideo_ut, repr=False)
    voice: FragVoice_ut = dcs.field(default_factory=FragVoice_ut, repr=False)

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        content_protos = data_proto.first_post_content

        texts = []
        emojis = []
        imgs = [FragImage_ut.from_proto(p) for p in data_proto.media if p.type != 5]
        ats = []
        links = []

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_ut.from_proto(proto)
                    texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_ut.from_proto(proto)
                    emojis.append(frag)
                    yield frag
                # img will be init elsewhere
                elif _type in [3, 20]:
                    continue
                elif _type == 4:
                    frag = FragAt_ut.from_proto(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_ut.from_proto(proto)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 5:  # video
                    continue
                elif _type == 10:  # voice
                    continue
                else:
                    yield FragUnknown.from_proto(proto)

        objs = list(_frags())
        objs += imgs

        if data_proto.video_info.video_width:
            video = FragVideo_ut.from_proto(data_proto.video_info)
            objs.append(video)
        else:
            video = FragVideo_ut()

        if data_proto.voice_info:
            voice = FragVoice_ut.from_proto(data_proto.voice_info[0])
            objs.append(voice)
        else:
            voice = FragVoice_ut()

        return cls(objs, texts, emojis, imgs, ats, links, video, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class UserThread:
    """
    主题帖信息

    Attributes:
        text (str): 文本内容
        contents (Contents_ut): 正文内容碎片列表
        title (str): 标题内容

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼回复pid
        user (UserInfo_u): 发布者的用户信息

        type (ThreadType): 帖子类型

        vote_info (VoteInfo): 投票信息
        view_num (int): 浏览量
        reply_num (int): 回复数
        share_num (int): 分享数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    contents: Contents_ut = dcs.field(default_factory=Contents_ut)
    title: str = ""

    fid: int = 0
    fname: str = ""
    tid: int = 0
    pid: int = 0
    user: UserInfo_u = dcs.field(default_factory=UserInfo_u)

    type: ThreadType = ThreadType.UNKNOWN

    vote_info: VoteInfo = dcs.field(default_factory=VoteInfo)
    view_num: int = 0
    reply_num: int = 0
    share_num: int = 0
    agree: int = 0
    disagree: int = 0
    create_time: int = 0

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        contents = Contents_ut.from_proto(data_proto)
        title = data_proto.title
        fid = data_proto.forum_id
        fname = data_proto.forum_name
        tid = data_proto.thread_id
        pid = data_proto.post_id

        type_ = ThreadType(data_proto.thread_type)
        if type_ == ThreadType.UNKNOWN:
            LOG().debug("Unknown thread type. tid=%d, type=%s", tid, data_proto.thread_type)

        vote_info = VoteInfo.from_proto(data_proto.poll_info)
        view_num = data_proto.freq_num
        reply_num = data_proto.reply_num
        share_num = data_proto.share_num
        agree = data_proto.agree.agree_num
        disagree = data_proto.agree.disagree_num
        create_time = data_proto.create_time
        return cls(
            contents,
            title,
            fid,
            fname,
            tid,
            pid,
            None,
            type_,
            vote_info,
            view_num,
            reply_num,
            share_num,
            agree,
            disagree,
            create_time,
        )

    def __eq__(self, obj: UserThread) -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @cached_property
    def text(self) -> str:
        if self.title:
            text = f"{self.title}\n{self.contents.text}"
        else:
            text = self.contents.text
        return text


@dcs.dataclass
class UserThreads(TbErrorExt, Containers[UserThread]):
    """
    用户发布主题帖列表

    Attributes:
        objs (list[UserThread]): 用户发布主题帖列表
        err (Exception | None): 捕获的异常
    """

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        objs = [UserThread.from_proto(p) for p in data_proto.post_list]
        if objs:
            user = UserInfo_u.from_proto(data_proto.post_list[0])
            for uthread in objs:
                uthread.user = user
        return cls(objs)
