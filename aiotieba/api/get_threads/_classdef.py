import dataclasses as dcs
from functools import cached_property
from typing import Dict, List

from ...enums import Gender, PrivLike, PrivReply
from ...exception import TbErrorExt
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

VirtualImage_t = VirtualImage

FragText_t = FragText_st = FragText
FragEmoji_t = FragEmoji_st = FragEmoji
FragAt_t = FragAt_st = FragAt
FragLink_t = FragLink_st = FragLink
FragTiebaPlus_t = FragTiebaPlus_st = FragTiebaPlus
FragVideo_t = FragVideo_st = FragVideo
FragVoice_t = FragVoice_st = FragVoice


@dcs.dataclass
class FragImage_t:
    """
    图像碎片

    Attributes:
        src (str): 小图链接 宽720px 一定是静态图
        big_src (str): 大图链接 宽960px
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
    def from_tbdata(data_proto: TypeMessage) -> "FragImage_t":
        src = data_proto.cdn_src
        big_src = data_proto.big_cdn_src
        origin_src = data_proto.origin_src
        origin_size = data_proto.origin_size

        show_width, _, show_height = data_proto.bsize.partition(',')
        show_width = int(show_width)
        show_height = int(show_height)

        return FragImage_t(src, big_src, origin_src, origin_size, show_width, show_height)

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
class Contents_t(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_t]): 表情碎片列表
        imgs (list[FragImage_t]): 图像碎片列表
        ats (list[FragAt_t]): @碎片列表
        links (list[FragLink_t]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_t]): 贴吧plus碎片列表
        video (FragVideo_t): 视频碎片
        voice (FragVoice_t): 音频碎片
    """

    texts: List[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: List[FragEmoji_t] = dcs.field(default_factory=list, repr=False)
    imgs: List[FragImage_t] = dcs.field(default_factory=list, repr=False)
    ats: List[FragAt_t] = dcs.field(default_factory=list, repr=False)
    links: List[FragLink_t] = dcs.field(default_factory=list, repr=False)
    tiebapluses: List[FragTiebaPlus_t] = dcs.field(default_factory=list, repr=False)
    video: FragVideo_t = dcs.field(default_factory=FragVideo_t, repr=False)
    voice: FragVoice_t = dcs.field(default_factory=FragVoice_t, repr=False)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Contents_t":
        content_protos = data_proto.first_post_content

        texts = []
        emojis = []
        imgs = []
        ats = []
        links = []
        tiebapluses = []

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_t.from_tbdata(proto)
                    texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_t.from_tbdata(proto)
                    emojis.append(frag)
                    yield frag
                # 20:tid=5470214675
                elif _type in [3, 20]:
                    frag = FragImage_t.from_tbdata(proto)
                    imgs.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_t.from_tbdata(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_t.from_tbdata(proto)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 10:  # voice
                    continue
                elif _type == 5:  # video
                    continue
                # 35|36:tid=7769728331 / 37:tid=7760184147
                elif _type in [35, 36, 37]:
                    frag = FragTiebaPlus_t.from_tbdata(proto)
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

        if data_proto.video_info.video_width:
            video = FragVideo_t.from_tbdata(data_proto.video_info)
            objs.append(video)
        else:
            video = FragVideo_t()

        if data_proto.voice_info:
            voice = FragVoice_t.from_tbdata(data_proto.voice_info[0])
            objs.append(voice)
        else:
            voice = FragVoice_t()

        return Contents_t(objs, texts, emojis, imgs, ats, links, tiebapluses, video, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class Page_t:
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
    def from_tbdata(data_proto: TypeMessage) -> "Page_t":
        page_size = data_proto.page_size
        current_page = data_proto.current_page
        total_page = data_proto.total_page
        total_count = data_proto.total_count
        has_more = bool(data_proto.has_more)
        has_prev = bool(data_proto.has_prev)
        return Page_t(page_size, current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class UserInfo_t:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        level (int): 等级
        glevel (int): 贴吧成长等级
        gender (Gender): 性别
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
    icons: List[str] = dcs.field(default_factory=list)

    is_bawu: bool = False
    is_vip: bool = False
    is_god: bool = False
    priv_like: PrivLike = PrivLike.PUBLIC
    priv_reply: PrivReply = PrivReply.ALL

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_t":
        user_id = data_proto.id
        portrait = data_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.name
        nick_name_new = data_proto.name_show
        level = data_proto.level_id
        glevel = data_proto.user_growth.level_id
        gender = Gender(data_proto.gender)
        icons = [name for i in data_proto.iconinfo if (name := i.name)]
        is_bawu = bool(data_proto.is_bawu)
        is_vip = bool(data_proto.new_tshow_icon)
        is_god = bool(data_proto.new_god_data.status)
        priv_like = PrivLike(priv_like) if (priv_like := data_proto.priv_sets.like) else PrivLike.PUBLIC
        priv_reply = PrivReply(priv_reply) if (priv_reply := data_proto.priv_sets.reply) else PrivReply.ALL
        return UserInfo_t(
            user_id,
            portrait,
            user_name,
            nick_name_new,
            level,
            glevel,
            gender,
            icons,
            is_bawu,
            is_vip,
            is_god,
            priv_like,
            priv_reply,
        )

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_t") -> bool:
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
class FragImage_st:
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
    def from_tbdata(data_proto: TypeMessage) -> "FragImage_st":
        src = data_proto.water_pic
        big_src = data_proto.small_pic
        origin_src = data_proto.big_pic
        show_width = data_proto.width
        show_height = data_proto.height
        return FragImage_st(src, big_src, origin_src, show_width, show_height)

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
class Contents_st(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_st]): 表情碎片列表
        imgs (list[FragImage_st]): 图像碎片列表
        ats (list[FragAt_st]): @碎片列表
        links (list[FragLink_st]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_st]): 贴吧plus碎片列表
        video (FragVideo_st): 视频碎片
        voice (FragVoice_st): 视频碎片
    """

    texts: List[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: List[FragEmoji_st] = dcs.field(default_factory=list, repr=False)
    imgs: List[FragImage_st] = dcs.field(default_factory=list, repr=False)
    ats: List[FragAt_st] = dcs.field(default_factory=list, repr=False)
    links: List[FragLink_st] = dcs.field(default_factory=list, repr=False)
    tiebapluses: List[FragTiebaPlus_st] = dcs.field(default_factory=list, repr=False)
    video: FragVideo_st = dcs.field(default_factory=FragVideo_st, repr=False)
    voice: FragVoice_st = dcs.field(default_factory=FragVoice_st, repr=False)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Contents_st":
        content_protos = data_proto.content

        texts = []
        emojis = []
        imgs = [FragImage_st.from_tbdata(p) for p in data_proto.media]
        ats = []
        links = []
        tiebapluses = []

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_st.from_tbdata(proto)
                    texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_st.from_tbdata(proto)
                    emojis.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_st.from_tbdata(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_st.from_tbdata(proto)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 5:  # video
                    continue
                # 35|36:tid=7769728331 / 37:tid=7760184147
                elif _type in [35, 36, 37]:
                    frag = FragTiebaPlus_st.from_tbdata(proto)
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
            video = FragVideo_st.from_tbdata(data_proto.video_info)
            objs.append(video)
        else:
            video = FragVideo_st()

        if data_proto.voice_info:
            voice = FragVoice_st.from_tbdata(data_proto.voice_info[0])
            objs.append(voice)
        else:
            voice = FragVoice_st()

        return Contents_st(objs, texts, emojis, imgs, ats, links, tiebapluses, video, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class ShareThread:
    """
    被分享的主题帖信息

    Attributes:
        text (str): 文本内容
        contents (Contents_st): 正文内容碎片列表
        title (str): 标题内容

        author_id (int): 发布者的user_id

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼的回复id

        vote_info (VoteInfo): 投票内容
    """

    contents: Contents_st = dcs.field(default_factory=Contents_st)
    title: str = ""

    author_id: int = 0

    fid: int = 0
    fname: str = ''
    tid: int = 0
    pid: int = 0

    vote_info: VoteInfo = dcs.field(default_factory=VoteInfo)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "ShareThread":
        contents = Contents_st.from_tbdata(data_proto)
        author_id = data_proto.content[0].uid if data_proto.content else 0
        title = data_proto.title
        fid = data_proto.fid
        fname = data_proto.fname
        tid = int(tid) if (tid := data_proto.tid) else 0
        pid = data_proto.pid
        vote_info = VoteInfo.from_tbdata(data_proto.poll_info)
        return ShareThread(contents, title, author_id, fid, fname, tid, pid, vote_info)

    def __eq__(self, obj: "ShareThread") -> bool:
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
class Thread:
    """
    主题帖信息

    Attributes:
        text (str): 文本内容
        contents (Contents_t): 正文内容碎片列表
        title (str): 标题

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼回复pid
        user (UserInfo_t): 发布者的用户信息
        author_id (int): 发布者的user_id
        vimage (VirtualImage_t): 虚拟形象信息

        type (int): 帖子类型
        tab_id (int): 帖子所在分区id
        is_good (bool): 是否精品帖
        is_top (bool): 是否置顶帖
        is_share (bool): 是否分享帖
        is_hide (bool): 是否被屏蔽
        is_livepost (bool): 是否为置顶话题
        is_help (bool): 是否为求助帖

        vote_info (VoteInfo): 投票信息
        share_origin (ShareThread): 转发来的原帖内容
        view_num (int): 浏览量
        reply_num (int): 回复数
        share_num (int): 分享数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间 10位时间戳 以秒为单位
        last_time (int): 最后回复时间 10位时间戳 以秒为单位
    """

    contents: Contents_t = dcs.field(default_factory=Contents_t)
    title: str = ""

    fid: int = 0
    fname: str = ''
    tid: int = 0
    pid: int = 0
    user: UserInfo_t = dcs.field(default_factory=UserInfo_t)
    author_id: int = 0
    vimage: VirtualImage_t = dcs.field(default_factory=VirtualImage_t)

    type: int = 0
    tab_id: int = 0
    is_good: bool = False
    is_top: bool = False
    is_share: bool = False
    is_hide: bool = False
    is_livepost: bool = False

    vote_info: VoteInfo = dcs.field(default_factory=VoteInfo)
    share_origin: ShareThread = dcs.field(default_factory=ShareThread)
    view_num: int = 0
    reply_num: int = 0
    share_num: int = 0
    agree: int = 0
    disagree: int = 0
    create_time: int = 0
    last_time: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> None:
        contents = Contents_t.from_tbdata(data_proto)
        title = data_proto.title
        tid = data_proto.id
        pid = data_proto.first_post_id
        author_id = data_proto.author_id
        vimage = VirtualImage_t.from_tbdata(data_proto)
        type_ = data_proto.thread_type
        tab_id = data_proto.tab_id
        is_good = bool(data_proto.is_good)
        is_top = bool(data_proto.is_top)
        is_share = bool(data_proto.is_share_thread)
        is_hide = bool(data_proto.is_frs_mask)
        is_livepost = bool(data_proto.is_livepost)
        vote_info = VoteInfo.from_tbdata(data_proto.poll_info)
        if is_share:
            if data_proto.origin_thread_info.pid:
                share_origin = ShareThread.from_tbdata(data_proto.origin_thread_info)
            else:
                is_share = False
                share_origin = ShareThread()
        else:
            share_origin = ShareThread()
        view_num = data_proto.view_num
        reply_num = data_proto.reply_num
        share_num = data_proto.share_num
        agree = data_proto.agree.agree_num
        disagree = data_proto.agree.disagree_num
        create_time = data_proto.create_time
        last_time = data_proto.last_time_int
        return Thread(
            contents,
            title,
            0,
            '',
            tid,
            pid,
            None,
            author_id,
            vimage,
            type_,
            tab_id,
            is_good,
            is_top,
            is_share,
            is_hide,
            is_livepost,
            vote_info,
            share_origin,
            view_num,
            reply_num,
            share_num,
            agree,
            disagree,
            create_time,
            last_time,
        )

    def __eq__(self, obj: "Thread") -> bool:
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
class Forum_t:
    """
    吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        member_num (int): 吧会员数
        post_num (int): 发帖量
        thread_num (int): 主题帖数

        has_bawu (bool): 是否有吧务
        has_rule (bool): 是否有吧规
    """

    fid: int = 0
    fname: str = ''

    member_num: int = 0
    post_num: int = 0
    thread_num: int = 0

    has_bawu: bool = False
    has_rule: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Forum_t":
        forum_proto = data_proto.forum
        fid = forum_proto.id
        fname = forum_proto.name
        member_num = forum_proto.member_num
        post_num = forum_proto.post_num
        thread_num = forum_proto.thread_num
        has_bawu = bool(forum_proto.managers)
        has_rule = bool(data_proto.forum_rule.has_forum_rule)
        return Forum_t(fid, fname, member_num, post_num, thread_num, has_bawu, has_rule)


@dcs.dataclass
class Threads(TbErrorExt, Containers[Thread]):
    """
    主题帖列表

    Attributes:
        objs (list[Thread]): 主题帖列表
        err (Exception | None): 捕获的异常

        page (Page_t): 页信息
        has_more (bool): 是否还有下一页

        forum (Forum_t): 所在吧信息
        tab_map (dict[str, int]): 分区名到分区id的映射表
    """

    page: Page_t = dcs.field(default_factory=Page_t)
    forum: Forum_t = dcs.field(default_factory=Forum_t)
    tab_map: Dict[str, int] = dcs.field(default_factory=dict)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Threads":
        page = Page_t.from_tbdata(data_proto.page)
        forum = Forum_t.from_tbdata(data_proto)
        tab_map = {p.tab_name: p.tab_id for p in data_proto.nav_tab_info.tab}

        objs = [Thread.from_tbdata(p) for p in data_proto.thread_list]
        users = {i: UserInfo_t.from_tbdata(p) for p in data_proto.user_list if (i := p.id)}
        for thread in objs:
            thread.fname = forum.fname
            thread.fid = forum.fid
            thread.user = users[thread.author_id]

        return Threads(objs, page, forum, tab_map)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
