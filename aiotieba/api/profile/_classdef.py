import dataclasses as dcs
from functools import cached_property
from typing import List

from ...enums import Gender, PrivLike, PrivReply
from ...exception import TbErrorExt
from .._classdef import Containers, TypeMessage, VoteInfo
from .._classdef.contents import FragAt, FragEmoji, FragLink, FragText, FragVideo, FragVoice, TypeFragment, TypeFragText

FragText_pf = FragText
FragEmoji_pf = FragEmoji
FragAt_pf = FragAt
FragLink_pf = FragLink
FragVideo_pf = FragVideo
FragVoice_pf = FragVoice


@dcs.dataclass
class VirtualImage_pf:
    """
    虚拟形象信息

    Attributes:
        enabled (bool): 是否启用虚拟形象
        state (str): 虚拟形象状态签名
    """

    enabled: bool = False
    state: str = ""

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "VirtualImage_pf":
        enabled = bool(data_proto.isset_virtual_image)
        state = data_proto.personal_state.text
        return VirtualImage_pf(enabled, state)

    def __str__(self) -> str:
        return self.state

    def __bool__(self) -> bool:
        return self.enabled


@dcs.dataclass
class UserInfo_pf(TbErrorExt):
    """
    用户信息

    Attributes:
        err (Exception | None): 捕获的异常

        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称
        tieba_uid (int): 用户个人主页uid

        glevel (int): 贴吧成长等级
        gender (Gender): 性别
        age (float): 吧龄 以年为单位
        post_num (int): 发帖数
        agree_num (int): 获赞数
        fan_num (int): 粉丝数
        follow_num (int): 关注数
        forum_num (int): 关注贴吧数
        sign (str): 个性签名
        ip (str): ip归属地
        icons (list[str]): 印记信息
        vimage (VirtualImage_pf): 虚拟形象信息

        is_vip (bool): 是否超级会员
        is_god (bool): 是否大神
        is_blocked (bool): 是否被永久封禁屏蔽
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
    tieba_uid: int = 0

    glevel: int = 0
    gender: Gender = Gender.UNKNOWN
    age: float = 0.0
    post_num: int = 0
    agree_num: int = 0
    fan_num: int = 0
    follow_num: int = 0
    forum_num: int = 0
    sign: str = ""
    ip: str = ''
    icons: List[str] = dcs.field(default_factory=list)
    vimage: VirtualImage_pf = dcs.field(default_factory=VirtualImage_pf)

    is_vip: bool = False
    is_god: bool = False
    is_blocked: bool = False
    priv_like: PrivLike = PrivLike.PUBLIC
    priv_reply: PrivReply = PrivReply.ALL

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_pf":
        user_proto = data_proto.user
        user_id = user_proto.id
        portrait = user_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = user_proto.name
        nick_name_new = user_proto.name_show
        tieba_uid = int(tieba_uid) if (tieba_uid := user_proto.tieba_uid) else 0
        glevel = user_proto.user_growth.level_id
        gender = Gender(user_proto.sex)
        age = float(age) if (age := user_proto.tb_age) else 0.0
        post_num = user_proto.post_num
        agree_num = data_proto.user_agree_info.total_agree_num
        fan_num = user_proto.fans_num
        follow_num = user_proto.concern_num
        forum_num = user_proto.my_like_num
        sign = user_proto.intro
        ip = user_proto.ip_address
        icons = [name for i in user_proto.iconinfo if (name := i.name)]
        vimage = VirtualImage_pf.from_tbdata(user_proto.virtual_image_info)
        is_vip = bool(user_proto.new_tshow_icon)
        is_god = bool(user_proto.new_god_data.status)
        anti_proto = data_proto.anti_stat
        if anti_proto.block_stat and anti_proto.hide_stat and anti_proto.days_tofree > 30:
            is_blocked = True
        else:
            is_blocked = False
        priv_like = PrivLike(priv_like) if (priv_like := user_proto.priv_sets.like) else PrivLike.PUBLIC
        priv_reply = PrivReply(priv_reply) if (priv_reply := user_proto.priv_sets.reply) else PrivReply.ALL
        return UserInfo_pf(
            user_id,
            portrait,
            user_name,
            nick_name_new,
            tieba_uid,
            glevel,
            gender,
            age,
            post_num,
            agree_num,
            fan_num,
            follow_num,
            forum_num,
            sign,
            ip,
            icons,
            vimage,
            is_vip,
            is_god,
            is_blocked,
            priv_like,
            priv_reply,
        )

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_pf") -> bool:
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
class FragImage_pf:
    """
    图像碎片

    Attributes:
        src (str): 大图链接 宽960px
        origin_src (str): 原图链接
        width (int): 图像宽度
        height (int): 图像高度
        hash (str): 百度图床hash
    """

    src: str = ""
    origin_src: str = ""
    origin_size: int = 0
    width: int = 0
    height: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragImage_pf":
        src = data_proto.big_pic
        origin_src = data_proto.origin_pic
        origin_size = data_proto.origin_size
        width = data_proto.width
        height = data_proto.height
        return FragImage_pf(src, origin_src, origin_size, width, height)

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
class Contents_pf(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_pf]): 表情碎片列表
        imgs (list[FragImage_pf]): 图像碎片列表
        ats (list[FragAt_pf]): @碎片列表
        links (list[FragLink_pf]): 链接碎片列表
        video (FragVideo_pf): 视频碎片
        voice (FragVoice_pf): 音频碎片
    """

    texts: List[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: List[FragEmoji_pf] = dcs.field(default_factory=list, repr=False)
    imgs: List[FragImage_pf] = dcs.field(default_factory=list, repr=False)
    ats: List[FragAt_pf] = dcs.field(default_factory=list, repr=False)
    links: List[FragLink_pf] = dcs.field(default_factory=list, repr=False)
    video: FragVideo_pf = dcs.field(default_factory=FragVideo_pf, repr=False)
    voice: FragVoice_pf = dcs.field(default_factory=FragVoice_pf, repr=False)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Contents_pf":
        content_protos = data_proto.first_post_content

        texts = []
        emojis = []
        imgs = [FragImage_pf.from_tbdata(p) for p in data_proto.media if p.type != 5]
        ats = []
        links = []

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_pf.from_tbdata(proto)
                    texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_pf.from_tbdata(proto)
                    emojis.append(frag)
                    yield frag
                elif _type in [3, 20]:
                    continue
                elif _type == 4:
                    frag = FragAt_pf.from_tbdata(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_pf.from_tbdata(proto)
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
            video = FragVideo_pf.from_tbdata(data_proto.video_info)
            objs.append(video)
        else:
            video = FragVideo_pf()

        if data_proto.voice_info:
            voice = FragVoice_pf.from_tbdata(data_proto.voice_info[0])
            objs.append(voice)
        else:
            voice = FragVoice_pf()

        return Contents_pf(objs, texts, emojis, imgs, ats, links, video, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class Thread_pf:
    """
    主题帖信息

    Attributes:
        text (str): 文本内容
        contents (Contents_pf): 正文内容碎片列表
        title (str): 标题

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼回复pid
        user (UserInfo_pf): 发布者的用户信息
        author_id (int): 发布者的user_id

        vote_info (VoteInfo): 投票信息
        view_num (int): 浏览量
        reply_num (int): 回复数
        share_num (int): 分享数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    contents: Contents_pf = dcs.field(default_factory=Contents_pf)
    title: str = ""

    fid: int = 0
    fname: str = ''
    tid: int = 0
    pid: int = 0
    user: UserInfo_pf = dcs.field(default_factory=UserInfo_pf)

    vote_info: VoteInfo = dcs.field(default_factory=VoteInfo)
    view_num: int = 0
    reply_num: int = 0
    share_num: int = 0
    agree: int = 0
    disagree: int = 0
    create_time: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Thread_pf":
        contents = Contents_pf.from_tbdata(data_proto)
        title = data_proto.title
        fid = data_proto.forum_id
        fname = data_proto.forum_name
        tid = data_proto.thread_id
        pid = data_proto.post_id
        vote_info = VoteInfo.from_tbdata(data_proto.poll_info)
        view_num = data_proto.freq_num
        reply_num = data_proto.reply_num
        share_num = data_proto.share_num
        agree = data_proto.agree.agree_num
        disagree = data_proto.agree.disagree_num
        create_time = data_proto.create_time
        return Thread_pf(
            contents,
            title,
            fid,
            fname,
            tid,
            pid,
            None,
            vote_info,
            view_num,
            reply_num,
            share_num,
            agree,
            disagree,
            create_time,
        )

    def __eq__(self, obj: "Thread_pf") -> bool:
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
    def author_id(self) -> int:
        return self.user.user_id


@dcs.dataclass
class Homepage(TbErrorExt, Containers[Thread_pf]):
    """
    用户个人页信息

    Attributes:
        objs (list[Thread_pf]): 用户发布主题帖列表
        err (Exception | None): 捕获的异常

        user (UserInfo_pf): 用户信息
    """

    vote_info: UserInfo_pf = dcs.field(default_factory=UserInfo_pf)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Homepage":
        objs = [Thread_pf.from_tbdata(p) for p in data_proto.post_list]
        user = UserInfo_pf.from_tbdata(data_proto)

        for thread in objs:
            thread.user = user

        return Homepage(objs, user)
