import dataclasses as dcs
from functools import cached_property
from typing import List

from ...enums import Gender, PrivLike, PrivReply
from ...exception import TbErrorExt
from ...helper import removeprefix
from .._classdef import Containers, TypeMessage, VirtualImage, VoteInfo
from .._classdef.contents import (
    FragAt,
    FragEmoji,
    FragLink,
    FragText,
    FragTiebaPlus,
    FragVideo,
    FragVoice,
    TypeFragment,
    TypeFragText,
)

VirtualImage_p = VirtualImage

FragText_p = FragText_pt = FragText_pc = FragText
FragEmoji_p = FragEmoji_pt = FragEmoji_pc = FragEmoji
FragAt_p = FragAt_pt = FragAt_pc = FragAt
FragLink_p = FragLink_pt = FragLink_pc = FragLink
FragTiebaPlus_p = FragTiebaPlus_pt = FragTiebaPlus_pc = FragTiebaPlus
FragVideo_pt = FragVideo
FragVoice_p = FragVoice_pt = FragVoice_pc = FragVoice


@dcs.dataclass
class FragImage_p:
    """
    图像碎片

    Attributes:
        src (str): 小图链接
        big_src (str): 大图链接
        origin_src (str): 原图链接
        origin_size (int): 原图大小
        show_width (int): 图像在客户端预览显示的宽度
        show_height (int): 图像在客户端预览显示的高度
        hash (str): 百度图床hash
    """

    src: str = ""
    big_src: str = ""
    origin_src: str = ""
    origin_size: int = 0
    show_width: int = 0
    show_height: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragImage_p":
        src = data_proto.cdn_src
        big_src = data_proto.big_cdn_src
        origin_src = data_proto.origin_src
        origin_size = data_proto.origin_size

        show_width, _, show_height = data_proto.bsize.partition(',')
        show_width = int(show_width)
        show_height = int(show_height)

        return FragImage_p(src, big_src, origin_src, origin_size, show_width, show_height)

    @cached_property
    def hash(self) -> str:
        """
        图像的百度图床hash
        """

        first_qmark_idx = self.src.find('?')
        end_idx = self.src.rfind('.', 0, first_qmark_idx)

        if end_idx == -1:
            hash_ = ''
        else:
            start_idx = self.src.rfind('/', 0, end_idx)
            hash_ = self.src[start_idx + 1 : end_idx]

        return hash_


@dcs.dataclass
class FragVideo_p:
    """
    视频碎片

    Attributes:
        src (str): 视频链接
        cover_src (str): 封面链接
        duration (int): 视频长度 以秒为单位
        width (int): 视频宽度
        height (int): 视频高度
        view_num (int): 浏览次数
    """

    src: str = ""
    cover_src: str = ""
    duration: int = 0
    width: int = 0
    height: int = 0
    view_num: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragVideo_p":
        src = data_proto.link
        cover_src = data_proto.src
        duration = data_proto.during_time
        width = data_proto.width
        height = data_proto.height
        view_num = data_proto.count
        return FragVideo_p(src, cover_src, duration, width, height, view_num)

    def __bool__(self) -> bool:
        return bool(self.width)


@dcs.dataclass
class Contents_p(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_p]): 表情碎片列表
        imgs (list[FragImage_p]): 图像碎片列表
        ats (list[FragAt_p]): @碎片列表
        links (list[FragLink_p]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_p]): 贴吧plus碎片列表
        video (FragVideo_p): 视频碎片
        voice (FragVoice_p): 音频碎片
    """

    texts: List[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: List[FragEmoji_p] = dcs.field(default_factory=list, repr=False)
    imgs: List[FragImage_p] = dcs.field(default_factory=list, repr=False)
    ats: List[FragAt_p] = dcs.field(default_factory=list, repr=False)
    links: List[FragLink_p] = dcs.field(default_factory=list, repr=False)
    tiebapluses: List[FragTiebaPlus_p] = dcs.field(default_factory=list, repr=False)
    video: FragVideo_p = dcs.field(default_factory=FragVideo_p, repr=False)
    voice: FragVoice_p = dcs.field(default_factory=FragVoice_p, repr=False)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Contents_p":
        content_protos = data_proto.content

        texts = []
        emojis = []
        imgs = []
        ats = []
        links = []
        tiebapluses = []
        video = FragVideo_p()
        voice = FragVoice_p()

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_p.from_tbdata(proto)
                    texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_p.from_tbdata(proto)
                    emojis.append(frag)
                    yield frag
                # 20:tid=5470214675
                elif _type in [3, 20]:
                    frag = FragImage_p.from_tbdata(proto)
                    imgs.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_p.from_tbdata(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_p.from_tbdata(proto)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 10:  # voice
                    frag = FragVoice_p.from_tbdata(proto)
                    nonlocal voice
                    voice = frag
                    yield frag
                elif _type == 5:  # video
                    frag = FragVideo_p.from_tbdata(proto)
                    nonlocal video
                    video = frag
                    yield frag
                # 35|36:tid=7769728331 / 37:tid=7760184147
                elif _type in [35, 36, 37]:
                    frag = FragTiebaPlus_p.from_tbdata(proto)
                    tiebapluses.append(frag)
                    texts.append(frag)
                    yield frag
                # outdated tiebaplus
                elif _type == 34:
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning(f"Unknown fragment type. type={_type} proto={proto}")

        objs = list(_frags())

        return Contents_p(objs, texts, emojis, imgs, ats, links, tiebapluses, video, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class Contents_pc(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_pc]): 表情碎片列表
        ats (list[FragAt_pc]): @碎片列表
        links (list[FragLink_pc]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_pc]): 贴吧plus碎片列表
        voice (FragVoice_pc): 音频碎片
    """

    texts: List[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: List[FragEmoji_pc] = dcs.field(default_factory=list, repr=False)
    ats: List[FragAt_pc] = dcs.field(default_factory=list, repr=False)
    links: List[FragLink_pc] = dcs.field(default_factory=list, repr=False)
    tiebapluses: List[FragTiebaPlus_pc] = dcs.field(default_factory=list, repr=False)
    voice: FragVoice_pc = dcs.field(default_factory=FragVoice_pc, repr=False)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Contents_pc":
        content_protos = data_proto.content

        texts = []
        emojis = []
        ats = []
        links = []
        tiebapluses = []
        voice = FragVoice_pc()

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_pc.from_tbdata(proto)
                    texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_pc.from_tbdata(proto)
                    emojis.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_pc.from_tbdata(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_pc.from_tbdata(proto)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 10:  # voice
                    frag = FragVoice_pc.from_tbdata(proto)
                    nonlocal voice
                    voice = frag
                    yield frag
                # 35|36:tid=7769728331 / 37:tid=7760184147
                elif _type in [35, 36, 37]:
                    frag = FragTiebaPlus_pc.from_tbdata(proto)
                    tiebapluses.append(frag)
                    texts.append(frag)
                    yield frag
                # outdated tiebaplus
                elif _type == 34:
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning(f"Unknown fragment type. type={_type} proto={proto}")

        objs = list(_frags())

        return Contents_pc(objs, texts, emojis, ats, links, tiebapluses, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class UserInfo_p:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        level (int): 等级
        glevel (int): 贴吧成长等级
        gender (int): 性别
        ip (str): ip归属地
        icons (list[str]): 印记信息

        is_bawu (bool): 是否吧务
        is_vip (bool): 是否超级会员
        is_god (bool): 是否大神
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

    level: int = 0
    glevel: int = 0
    gender: Gender = Gender.UNKNOWN
    ip: str = ''
    icons: List[str] = dcs.field(default_factory=list)

    is_bawu: bool = False
    is_vip: bool = False
    is_god: bool = False
    priv_like: PrivLike = PrivLike.PUBLIC
    priv_reply: PrivReply = PrivReply.ALL

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_p":
        user_id = data_proto.id
        portrait = data_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.name
        nick_name_new = data_proto.name_show
        level = data_proto.level_id
        glevel = data_proto.user_growth.level_id
        gender = Gender(data_proto.gender)
        ip = data_proto.ip_address
        icons = [name for i in data_proto.iconinfo if (name := i.name)]
        is_bawu = bool(data_proto.is_bawu)
        is_vip = bool(data_proto.new_tshow_icon)
        is_god = bool(data_proto.new_god_data.status)
        priv_like = PrivLike(priv_like) if (priv_like := data_proto.priv_sets.like) else PrivLike.PUBLIC
        priv_reply = PrivReply(priv_reply) if (priv_reply := data_proto.priv_sets.reply) else PrivReply.ALL
        return UserInfo_p(
            user_id,
            portrait,
            user_name,
            nick_name_new,
            level,
            glevel,
            gender,
            ip,
            icons,
            is_bawu,
            is_vip,
            is_god,
            priv_like,
            priv_reply,
        )

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_p") -> bool:
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
class Comment_p:
    """
    楼中楼信息

    Attributes:
        text (str): 文本内容
        contents (Contents_pc): 正文内容碎片列表

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        ppid (int): 所在楼层id
        pid (int): 楼中楼id
        user (UserInfo_p): 发布者的用户信息
        author_id (int): 发布者的user_id
        reply_to_id (int): 被回复者的user_id

        floor (int): 所在楼层数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间 10位时间戳 以秒为单位
        is_thread_author (bool): 是否楼主
    """

    contents: Contents_pc = dcs.field(default_factory=Contents_pc)

    fid: int = 0
    fname: str = ''
    tid: int = 0
    ppid: int = 0
    pid: int = 0
    user: UserInfo_p = dcs.field(default_factory=UserInfo_p)
    author_id: int = 0
    reply_to_id: int = 0

    floor: int = 0
    agree: int = 0
    disagree: int = 0
    create_time: int = 0
    is_thread_author: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Comment_p":
        contents = Contents_pc.from_tbdata(data_proto)

        reply_to_id = 0
        if contents:
            first_frag = contents[0]
            if (
                isinstance(first_frag, FragText_p)
                and first_frag.text == '回复 '
                and (reply_to_id := data_proto.content[1].uid)
            ):
                reply_to_id = reply_to_id
                if isinstance(contents[1], FragAt_p):
                    del contents.ats[0]
                contents.objs = contents.objs[2:]
                contents.texts = contents.texts[2:]
                if contents.texts:
                    first_text_frag = contents.texts[0]
                    first_text_frag.text = removeprefix(first_text_frag.text, ' :')

        contents = contents

        pid = data_proto.id
        author_id = data_proto.author_id
        agree = data_proto.agree.agree_num
        disagree = data_proto.agree.disagree_num
        create_time = data_proto.time

        return Comment_p(
            contents, 0, '', 0, 0, pid, None, author_id, reply_to_id, 0, agree, disagree, create_time, False
        )

    def __eq__(self, obj: "Comment_p") -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @property
    def text(self) -> str:
        return self.contents.text


@dcs.dataclass
class Post:
    """
    楼层信息

    Attributes:
        text (str): 文本内容
        contents (Contents_p): 正文内容碎片列表
        sign (str): 小尾巴文本内容
        comments (list[Comment_p]): 楼中楼列表

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo_p): 发布者的用户信息
        author_id (int): 发布者的user_id
        vimage (VirtualImage_p): 虚拟形象信息

        floor (int): 楼层数
        reply_num (int): 楼中楼数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间
        is_thread_author (bool): 是否楼主
    """

    contents: Contents_p = dcs.field(default_factory=Contents_p)
    sign: str = ""
    comments: List[Comment_p] = dcs.field(default_factory=list)

    fid: int = 0
    fname: str = ''
    tid: int = 0
    pid: int = 0
    user: UserInfo_p = dcs.field(default_factory=UserInfo_p)
    author_id: int = 0
    vimage: VirtualImage_p = dcs.field(default_factory=VirtualImage_p)

    floor: int = 0
    reply_num: int = 0
    agree: int = 0
    disagree: int = 0
    create_time: int = 0
    is_thread_author: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Post":
        contents = Contents_p.from_tbdata(data_proto)
        sign = "".join(p.text for p in data_proto.signature.content if p.type == 0)
        comments = [Comment_p.from_tbdata(p) for p in data_proto.sub_post_list.sub_post_list]
        pid = data_proto.id
        author_id = data_proto.author_id
        vimage = VirtualImage_p.from_tbdata(data_proto)
        floor = data_proto.floor
        reply_num = data_proto.sub_post_number
        agree = data_proto.agree.agree_num
        disagree = data_proto.agree.disagree_num
        create_time = data_proto.time
        return Post(
            contents,
            sign,
            comments,
            0,
            '',
            0,
            pid,
            None,
            author_id,
            vimage,
            floor,
            reply_num,
            agree,
            disagree,
            create_time,
            False,
        )

    def __eq__(self, obj: "Post") -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @cached_property
    def text(self) -> str:
        if self.sign:
            text = f'{self.contents.text}\n{self.sign}'
        else:
            text = self.contents.text
        return text


@dcs.dataclass
class Page_p:
    """
    页信息

    Attributes:
        page_size (int): 页大小
        current_page (int): 当前页码
        total_page (int): 总页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    page_size: int = 0
    current_page: int = 0
    total_page: int = 0
    total_count: int = 0

    has_more: bool = False
    has_prev: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Page_p":
        page_size = data_proto.page_size
        current_page = data_proto.current_page
        total_page = data_proto.total_page
        total_count = data_proto.total_count
        has_more = bool(data_proto.has_more)
        has_prev = bool(data_proto.has_prev)
        return Page_p(page_size, current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class Forum_p:
    """
    吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        member_num (int): 吧会员数
        post_num (int): 发帖量
    """

    fid: int = 0
    fname: str = ''

    member_num: int = 0
    post_num: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Forum_p":
        fid = data_proto.id
        fname = data_proto.name
        member_num = data_proto.member_num
        post_num = data_proto.post_num
        return Forum_p(fid, fname, member_num, post_num)


@dcs.dataclass
class FragImage_pt:
    """
    图像碎片

    Attributes:
        src (str): 小图链接 宽580px
        big_src (str): 大图链接 宽720px
        origin_src (str): 原图链接
        show_width (int): 图像在客户端预览显示的宽度
        show_height (int): 图像在客户端预览显示的高度
        hash (str): 百度图床hash
    """

    src: str = ""
    big_src: str = ""
    origin_src: str = ""
    show_width: int = 0
    show_height: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragImage_pt":
        src = data_proto.water_pic
        big_src = data_proto.small_pic
        origin_src = data_proto.big_pic
        show_width = data_proto.width
        show_height = data_proto.height
        return FragImage_pt(src, big_src, origin_src, show_width, show_height)

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
class Contents_pt(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_pt]): 表情碎片列表
        imgs (list[FragImage_pt]): 图像碎片列表
        ats (list[FragAt_pt]): @碎片列表
        links (list[FragLink_pt]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_pt]): 贴吧plus碎片列表
        video (FragVideo_pt): 视频碎片
        voice (FragVoice_pt): 音频碎片
    """

    texts: List[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: List[FragEmoji_pt] = dcs.field(default_factory=list, repr=False)
    imgs: List[FragImage_pt] = dcs.field(default_factory=list, repr=False)
    ats: List[FragAt_pt] = dcs.field(default_factory=list, repr=False)
    links: List[FragLink_pt] = dcs.field(default_factory=list, repr=False)
    tiebapluses: List[FragTiebaPlus_pt] = dcs.field(default_factory=list, repr=False)
    video: FragVideo_pt = dcs.field(default_factory=FragVideo_pt, repr=False)
    voice: FragVoice_pt = dcs.field(default_factory=FragVoice_pt, repr=False)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Contents_pt":
        content_protos = data_proto.content

        texts = []
        emojis = []
        imgs = [FragImage_pt.from_tbdata(p) for p in data_proto.media]
        ats = []
        links = []
        tiebapluses = []

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_pt.from_tbdata(proto)
                    texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_pt.from_tbdata(proto)
                    emojis.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_pt.from_tbdata(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_pt.from_tbdata(proto)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                # 35|36:tid=7769728331 / 37:tid=7760184147
                elif _type in [35, 36, 37]:
                    frag = FragTiebaPlus_pt.from_tbdata(proto)
                    tiebapluses.append(frag)
                    texts.append(frag)
                    yield frag
                # outdated tiebaplus
                elif _type == 34:
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning(f"Unknown fragment type. type={_type} proto={proto}")

        objs = list(_frags())

        del ats[0]
        del objs[0]
        objs += imgs

        if data_proto.video_info.video_width:
            video = FragVideo_pt.from_tbdata(data_proto.video_info)
            objs.append(video)
        else:
            video = FragVideo_pt()

        if data_proto.voice_info:
            voice = FragVoice_pt.from_tbdata(data_proto.voice_info[0])
            objs.append(voice)
        else:
            voice = FragVoice_pt()

        return Contents_pt(objs, texts, emojis, imgs, ats, links, tiebapluses, video, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class UserInfo_pt:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        level (int): 等级
        glevel (int): 贴吧成长等级
        ip (str): ip归属地
        icons (list[str]): 印记信息

        is_bawu (bool): 是否吧务
        is_vip (bool): 是否超级会员
        is_god (bool): 是否大神
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

    level: int = 0
    glevel: int = 0
    ip: str = ''
    icons: List[str] = dcs.field(default_factory=list)

    is_bawu: bool = False
    is_vip: bool = False
    is_god: bool = False
    priv_like: PrivLike = PrivLike.PUBLIC
    priv_reply: PrivReply = PrivReply.ALL

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_pt":
        user_id = data_proto.id
        portrait = data_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.name
        nick_name_new = data_proto.name_show
        level = data_proto.level_id
        glevel = data_proto.user_growth.level_id
        ip = data_proto.ip_address
        icons = [name for i in data_proto.iconinfo if (name := i.name)]
        is_bawu = bool(data_proto.is_bawu)
        is_vip = bool(data_proto.new_tshow_icon)
        is_god = bool(data_proto.new_god_data.status)
        priv_like = PrivLike(priv_like) if (priv_like := data_proto.priv_sets.like) else PrivLike.PUBLIC
        priv_reply = PrivReply(priv_reply) if (priv_reply := data_proto.priv_sets.reply) else PrivReply.ALL
        return UserInfo_pt(
            user_id,
            portrait,
            user_name,
            nick_name_new,
            level,
            glevel,
            ip,
            icons,
            is_bawu,
            is_vip,
            is_god,
            priv_like,
            priv_reply,
        )

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_pt") -> bool:
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
class ShareThread_pt:
    """
    被分享的主题帖信息

    Attributes:
        text (str): 文本内容
        contents (Contents_pt): 正文内容碎片列表
        title (str): 标题内容

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        author_id (int): 发布者的user_id

        vote_info (VoteInfo): 投票内容
    """

    contents: Contents_pt = dcs.field(default_factory=Contents_pt)
    title: str = ""

    fid: int = 0
    fname: str = ''
    tid: int = 0
    author_id: int = 0

    vote_info: VoteInfo = dcs.field(default_factory=VoteInfo)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "ShareThread_pt":
        contents = Contents_pt.from_tbdata(data_proto)
        title = data_proto.title
        fid = data_proto.fid
        fname = data_proto.fname
        tid = int(tid) if (tid := data_proto.tid) else 0
        author_id = data_proto.content[0].uid if data_proto.content else 0
        vote_info = VoteInfo.from_tbdata(data_proto.poll_info)
        return ShareThread_pt(contents, title, fid, fname, tid, author_id, vote_info)

    def __eq__(self, obj: "ShareThread_pt") -> bool:
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
class Thread_p:
    """
    主题帖信息

    Attributes:
        text (str): 文本内容
        contents (Contents_pt): 正文内容碎片列表
        title (str): 标题

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼回复pid
        user (UserInfo_pt): 发布者的用户信息
        author_id (int): 发布者的user_id

        type (int): 帖子类型
        is_share (bool): 是否分享帖
        is_help (bool): 是否为求助帖

        vote_info (VoteInfo): 投票信息
        share_origin (ShareThread_pt): 转发来的原帖内容
        view_num (int): 浏览量
        reply_num (int): 回复数
        share_num (int): 分享数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    contents: Contents_pt = dcs.field(default_factory=Contents_pt)
    title: str = ""

    fid: int = 0
    fname: str = ''
    tid: int = 0
    pid: int = 0
    user: UserInfo_pt = dcs.field(default_factory=UserInfo_pt)

    type: int = 0
    is_share: bool = False

    vote_info: VoteInfo = dcs.field(default_factory=VoteInfo)
    share_origin: ShareThread_pt = dcs.field(default_factory=ShareThread_pt)
    view_num: int = 0
    reply_num: int = 0
    share_num: int = 0
    agree: int = 0
    disagree: int = 0
    create_time: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Thread_p":
        thread_proto = data_proto.thread
        title = thread_proto.title
        tid = thread_proto.id
        pid = thread_proto.post_id
        user = UserInfo_pt.from_tbdata(thread_proto.author)
        type_ = thread_proto.thread_type
        is_share = bool(thread_proto.is_share_thread)
        view_num = data_proto.thread_freq_num
        reply_num = thread_proto.reply_num
        share_num = thread_proto.share_num
        agree = thread_proto.agree.agree_num
        disagree = thread_proto.agree.disagree_num
        create_time = thread_proto.create_time

        if not is_share:
            real_thread_proto = thread_proto.origin_thread_info
            contents = Contents_pt.from_tbdata(real_thread_proto)
            vote_info = VoteInfo.from_tbdata(real_thread_proto.poll_info)
            share_origin = ShareThread_pt()
        else:
            contents = Contents_pt()
            vote_info = VoteInfo()
            share_origin = ShareThread_pt.from_tbdata(thread_proto.origin_thread_info)

        return Thread_p(
            contents,
            title,
            0,
            '',
            tid,
            pid,
            user,
            type_,
            is_share,
            vote_info,
            share_origin,
            view_num,
            reply_num,
            share_num,
            agree,
            disagree,
            create_time,
        )

    def __eq__(self, obj: "Thread_p") -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @property
    def text(self) -> str:
        if self.title:
            text = f"{self.title}\n{self.contents.text}"
        else:
            text = self.contents.text
        return text

    @property
    def author_id(self) -> int:
        return self.user.user_id

    @property
    def is_help(self) -> bool:
        return self.type == 71


@dcs.dataclass
class Posts(TbErrorExt, Containers[Post]):
    """
    回复列表

    Attributes:
        objs (list[Post]): 回复列表
        err (Exception | None): 捕获的异常

        page (Page_p): 页信息
        has_more (bool): 是否还有下一页

        forum (Forum_p): 所在吧信息
        thread (Thread_p): 所在主题帖信息
    """

    page: Page_p = dcs.field(default_factory=Page_p)
    forum: Forum_p = dcs.field(default_factory=Forum_p)
    thread: Thread_p = dcs.field(default_factory=Thread_p)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Posts":
        page = Page_p.from_tbdata(data_proto.page)
        forum = Forum_p.from_tbdata(data_proto.forum)
        thread = Thread_p.from_tbdata(data_proto)

        thread.fid = forum.fid
        thread.fname = forum.fname

        objs = [Post.from_tbdata(p) for p in data_proto.post_list]
        users = {i: UserInfo_p.from_tbdata(p) for p in data_proto.user_list if (i := p.id)}
        for post in objs:
            post.fid = forum.fid
            post.fname = forum.fname
            post.tid = thread.tid
            post.user = users[post.author_id]
            post.is_thread_author = thread.author_id == post.author_id
            for comment in post.comments:
                comment.fid = post.fid
                comment.fname = post.fname
                comment.tid = post.tid
                comment.ppid = post.pid
                comment.floor = post.floor
                comment.user = users[comment.author_id]
                comment.is_thread_author = thread.author_id == comment.author_id

        return Posts(objs, page, forum, thread)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
