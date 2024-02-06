import dataclasses as dcs
from functools import cached_property
from typing import List

from ...exception import TbErrorExt
from .._classdef import Containers, TypeMessage, VoteInfo
from .._classdef.contents import FragAt, FragEmoji, FragLink, FragText, FragVideo, FragVoice, TypeFragment, TypeFragText

FragText_up = FragText_ut = FragText
FragEmoji_ut = FragEmoji
FragAt_ut = FragAt
FragLink_up = FragLink_ut = FragLink
FragVideo_ut = FragVideo
FragVoice_ut = FragVoice


@dcs.dataclass
class FragVoice_up:
    """
    音频碎片

    Attributes:
        md5 (str): 音频md5
        duration (int): 音频长度 以秒为单位
    """

    md5: str = ""
    duration: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragVoice_up":
        voice_md5 = data_proto.voice_md5
        md5 = voice_md5[: voice_md5.rfind('_')]
        duration = int(data_proto.during_time) / 1000
        return FragVoice_up(md5, duration)

    def __bool__(self) -> bool:
        return bool(self.md5)


@dcs.dataclass
class Contents_up(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        links (list[FragLink_up]): 链接碎片列表
        voice (FragVoice_up): 音频碎片
    """

    texts: List[TypeFragText] = dcs.field(default_factory=list, repr=False)
    links: List[FragLink_up] = dcs.field(default_factory=list, repr=False)
    voice: FragVoice_up = dcs.field(default_factory=FragVoice_up, repr=False)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Contents_up":
        content_protos = data_proto.post_content

        texts = []
        links = []
        voice = FragVoice_up()

        def _frags():
            for proto in content_protos:
                _type = proto.type
                if _type in [0, 4]:
                    frag = FragText_up.from_tbdata(proto)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_up.from_tbdata(proto)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 10:  # voice
                    nonlocal voice
                    voice = FragVoice_up.from_tbdata(proto)
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning(f"Unknown fragment type. type={_type} proto={proto}")

        objs = list(_frags())

        return Contents_up(objs, texts, links, voice)

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
    portrait: str = ''
    user_name: str = ''
    nick_name_new: str = ''

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_u":
        user_id = data_proto.user_id
        portrait = data_proto.user_portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.user_name
        nick_name_new = data_proto.name_show
        return UserInfo_u(user_id, portrait, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_u") -> bool:
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

        is_comment (bool): 是否为楼中楼

        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    contents: Contents_up = dcs.field(default_factory=Contents_up)

    fid: int = 0
    tid: int = 0
    pid: int = 0
    user: UserInfo_u = dcs.field(default_factory=UserInfo_u)

    is_comment: bool = False

    create_time: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserPost":
        contents = Contents_up.from_tbdata(data_proto)
        pid = data_proto.post_id
        is_comment = bool(data_proto.post_type)
        create_time = data_proto.create_time
        return UserPost(contents, 0, 0, pid, None, is_comment, create_time)

    def __eq__(self, obj: "UserPost") -> bool:
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
    """

    fid: int = 0
    tid: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserPosts":
        fid = data_proto.forum_id
        tid = data_proto.thread_id
        objs = [UserPost.from_tbdata(p) for p in data_proto.content]
        for upost in objs:
            upost.fid = fid
            upost.tid = tid
        return UserPosts(objs, fid, tid)


@dcs.dataclass
class UserPostss(TbErrorExt, Containers[UserPosts]):
    """
    用户历史回复信息列表的列表

    Attributes:
        objs (list[UserPosts]): 用户历史回复信息列表的列表
        err (Exception | None): 捕获的异常
    """

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserPostss":
        objs = [UserPosts.from_tbdata(p) for p in data_proto.post_list]
        if objs:
            user = UserInfo_u.from_tbdata(data_proto.post_list[0])
            for uposts in objs:
                for upost in uposts:
                    upost.user = user
        return UserPostss(objs)


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

    src: str = ""
    big_src: str = ""
    origin_src: str = ""
    origin_size: int = 0
    width: int = 0
    height: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragImage_ut":
        src = data_proto.small_pic
        big_src = data_proto.big_pic
        origin_src = data_proto.origin_pic
        origin_size = data_proto.origin_size
        width = data_proto.width
        height = data_proto.height
        return FragImage_ut(src, big_src, origin_src, origin_size, width, height)

    @cached_property
    def hash(self) -> str:
        first_qmark_idx = self.src.find('?')
        end_idx = self.src.rfind('.', 0, first_qmark_idx)

        if end_idx == -1:
            hash_ = ''
        else:
            start_idx = self.src.rfind('/', 0, end_idx)
            hash_ = self.src[start_idx + 1 : end_idx]

        return hash_


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

    texts: List[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: List[FragEmoji_ut] = dcs.field(default_factory=list, repr=False)
    imgs: List[FragImage_ut] = dcs.field(default_factory=list, repr=False)
    ats: List[FragAt_ut] = dcs.field(default_factory=list, repr=False)
    links: List[FragLink_ut] = dcs.field(default_factory=list, repr=False)
    video: FragVideo_ut = dcs.field(default_factory=FragVideo_ut, repr=False)
    voice: FragVoice_ut = dcs.field(default_factory=FragVoice_ut, repr=False)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Contents_ut":
        content_protos = data_proto.first_post_content

        texts = []
        emojis = []
        imgs = [FragImage_ut.from_tbdata(p) for p in data_proto.media if p.type != 5]
        ats = []
        links = []

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_ut.from_tbdata(proto)
                    texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_ut.from_tbdata(proto)
                    emojis.append(frag)
                    yield frag
                # img will be init elsewhere
                elif _type in [3, 20]:
                    continue
                elif _type == 4:
                    frag = FragAt_ut.from_tbdata(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_ut.from_tbdata(proto)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 5:  # video
                    continue
                elif _type == 10:  # voice
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning(f"Unknown fragment type. type={_type} proto={proto}")

        objs = list(_frags())
        objs += imgs

        if data_proto.video_info.video_width:
            video = FragVideo_ut.from_tbdata(data_proto.video_info)
            objs.append(video)
        else:
            video = FragVideo_ut()

        if data_proto.voice_info:
            voice = FragVoice_ut.from_tbdata(data_proto.voice_info[0])
            objs.append(voice)
        else:
            voice = FragVoice_ut()

        return Contents_ut(objs, texts, emojis, imgs, ats, links, video, voice)

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
        title (str): 标题

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼回复pid
        user (UserInfo_u): 发布者的用户信息
        author_id (int): 发布者的user_id

        type (int): 帖子类型
        is_help (bool): 是否为求助帖

        vote_info (VoteInfo): 投票信息
        view_num (int): 浏览量
        reply_num (int): 回复数
        share_num (int): 分享数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    contents: Contents_ut = dcs.field(default_factory=Contents_ut)
    title: str = ''

    fid: int = 0
    fname: str = ''
    tid: int = 0
    pid: int = 0
    user: UserInfo_u = dcs.field(default_factory=UserInfo_u)

    type: int = 0

    vote_info: VoteInfo = dcs.field(default_factory=VoteInfo)
    view_num: int = 0
    reply_num: int = 0
    share_num: int = 0
    agree: int = 0
    disagree: int = 0
    create_time: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserThread":
        contents = Contents_ut.from_tbdata(data_proto)
        title = data_proto.title
        fid = data_proto.forum_id
        fname = data_proto.forum_name
        tid = data_proto.thread_id
        pid = data_proto.post_id
        type_ = data_proto.thread_type
        vote_info = VoteInfo.from_tbdata(data_proto.poll_info)
        view_num = data_proto.freq_num
        reply_num = data_proto.reply_num
        share_num = data_proto.share_num
        agree = data_proto.agree.agree_num
        disagree = data_proto.agree.disagree_num
        create_time = data_proto.create_time
        return UserThread(
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

    def __eq__(self, obj: "UserThread") -> bool:
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

    @property
    def is_help(self) -> bool:
        return self.type == 71


@dcs.dataclass
class UserThreads(TbErrorExt, Containers[UserThread]):
    """
    用户发布主题帖列表

    Attributes:
        objs (list[UserThread]): 用户发布主题帖列表
        err (Exception | None): 捕获的异常
    """

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserThreads":
        objs = [UserThread.from_tbdata(p) for p in data_proto.post_list]
        if objs:
            user = UserInfo_u.from_tbdata(data_proto.post_list[0])
            for uthread in objs:
                uthread.user = user
        return UserPostss(objs)
