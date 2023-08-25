from typing import List, Optional

from .._classdef import Containers, TypeMessage, VoteInfo
from .._classdef.contents import FragAt, FragEmoji, FragLink, FragText, FragVideo, FragVoice, TypeFragment, TypeFragText

FragText_pf = FragText
FragEmoji_pf = FragEmoji
FragAt_pf = FragAt
FragLink_pf = FragLink
FragVideo_pf = FragVideo
FragVoice_pf = FragVoice


class VirtualImage_pf(object):
    """
    虚拟形象信息

    Attributes:
        enabled (bool): 是否启用虚拟形象
        state (str): 虚拟形象状态签名
    """

    __slots__ = [
        '_enabled',
        '_state',
    ]

    def _init(self, data_proto: TypeMessage) -> "VirtualImage_pf":
        self._enabled = bool(data_proto.isset_virtual_image)
        self._state = data_proto.personal_state.text
        return self

    def _init_null(self) -> "VirtualImage_pf":
        self._enabled = False
        self._state = ''
        return self

    def __str__(self) -> str:
        return self._state

    def __repr__(self) -> str:
        return str(
            {
                'enabled': self._enabled,
                'state': self._state,
            }
        )

    def __bool__(self) -> bool:
        return self._enabled

    @property
    def enabled(self) -> bool:
        """
        是否启用虚拟形象
        """

        return self._enabled

    @property
    def state(self) -> str:
        """
        虚拟形象状态签名
        """

        return self._state


class UserInfo_pf(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称
        tieba_uid (int): 用户个人主页uid

        glevel (int): 贴吧成长等级
        gender (int): 性别
        age (float): 吧龄
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
        priv_like (int): 公开关注吧列表的设置状态
        priv_reply (int): 帖子评论权限的设置状态

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
        '_nick_name_new',
        '_tieba_uid',
        '_glevel',
        '_gender',
        '_age',
        '_post_num',
        '_agree_num',
        '_fan_num',
        '_follow_num',
        '_forum_num',
        '_sign',
        '_icons',
        '_vimage',
        '_ip',
        '_is_vip',
        '_is_god',
        '_is_blocked',
        '_priv_like',
        '_priv_reply',
    ]

    def __init__(self, data_proto: Optional[TypeMessage] = None) -> None:
        if data_proto:
            user_proto = data_proto.user
            self._user_id = user_proto.id
            if '?' in (portrait := user_proto.portrait):
                self._portrait = portrait[:-13]
            else:
                self._portrait = portrait
            self._user_name = user_proto.name
            self._nick_name_new = user_proto.name_show
            self._tieba_uid = int(tieba_uid) if (tieba_uid := user_proto.tieba_uid) else 0
            self._glevel = user_proto.user_growth.level_id
            self._gender = user_proto.sex
            self._age = float(age) if (age := user_proto.tb_age) else 0.0
            self._post_num = user_proto.post_num
            self._agree_num = data_proto.user_agree_info.total_agree_num
            self._fan_num = user_proto.fans_num
            self._follow_num = user_proto.concern_num
            self._forum_num = user_proto.my_like_num
            self._sign = user_proto.intro
            self._ip = user_proto.ip_address
            self._icons = [name for i in user_proto.iconinfo if (name := i.name)]
            self._vimage = VirtualImage_pf()._init(user_proto.virtual_image_info)
            self._is_vip = bool(user_proto.new_tshow_icon)
            self._is_god = bool(user_proto.new_god_data.status)
            anti_proto = data_proto.anti_stat
            if anti_proto.block_stat and anti_proto.hide_stat and anti_proto.days_tofree > 30:
                self._is_blocked = True
            else:
                self._is_blocked = False
            self._priv_like = priv_like if (priv_like := user_proto.priv_sets.like) else 1
            self._priv_reply = priv_reply if (priv_reply := user_proto.priv_sets.reply) else 1

        else:
            self._user_id = 0
            self._portrait = ''
            self._user_name = ''
            self._nick_name_new = ''
            self._tieba_uid = 0
            self._glevel = 0
            self._gender = 0
            self._age = 0.0
            self._post_num = 0
            self._agree_num = 0
            self._fan_num = 0
            self._follow_num = 0
            self._forum_num = 0
            self._sign = ''
            self._icons = []
            self._vimage = VirtualImage_pf()._init_null()
            self._ip = ''
            self._is_vip = False
            self._is_god = False
            self._is_blocked = False
            self._priv_like = 1
            self._priv_reply = 1

    def __str__(self) -> str:
        return self._user_name or self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'show_name': self.show_name,
            }
        )

    def __eq__(self, obj: "UserInfo_pf") -> bool:
        return self._user_id == obj._user_id

    def __hash__(self) -> int:
        return self._user_id

    def __int__(self) -> int:
        return self._user_id

    def __bool__(self) -> bool:
        return bool(self._user_id)

    @property
    def user_id(self) -> int:
        """
        用户user_id

        Note:
            唯一 不可变 不可为空\n
            请注意与用户个人页的tieba_uid区分
        """

        return self._user_id

    @property
    def portrait(self) -> str:
        """
        用户portrait

        Note:
            唯一 不可变 不可为空
        """

        return self._portrait

    @property
    def user_name(self) -> str:
        """
        用户名

        Note:
            唯一 可变 可为空\n
            请注意与用户昵称区分
        """

        return self._user_name

    @property
    def nick_name_new(self) -> str:
        """
        新版昵称
        """

        return self._nick_name_new

    @property
    def tieba_uid(self) -> int:
        """
        用户个人主页uid

        Note:
            唯一 不可变 可为空\n
            请注意与user_id区分
        """

        return self._tieba_uid

    @property
    def glevel(self) -> int:
        """
        贴吧成长等级
        """

        return self._glevel

    @property
    def gender(self) -> int:
        """
        性别

        Note:
            0未知 1男 2女
        """

        return self._gender

    @property
    def age(self) -> float:
        """
        吧龄

        Note:
            以年为单位
        """

        return self._age

    @property
    def post_num(self) -> int:
        """
        发帖数

        Note:
            是回复数和主题帖数的总和
        """

        return self._post_num

    @property
    def agree_num(self) -> int:
        """
        获赞数
        """

        return self._agree_num

    @property
    def fan_num(self) -> int:
        """
        粉丝数
        """

        return self._fan_num

    @property
    def follow_num(self) -> int:
        """
        关注数
        """

        return self._follow_num

    @property
    def forum_num(self) -> int:
        """
        关注贴吧数
        """

        return self._forum_num

    @property
    def sign(self) -> str:
        """
        个性签名
        """

        return self._sign

    @property
    def ip(self) -> str:
        """
        ip归属地
        """

        return self._ip

    @property
    def icons(self) -> List[str]:
        """
        印记信息
        """

        return self._icons

    @property
    def vimage(self) -> VirtualImage_pf:
        """
        虚拟形象信息
        """

        return self._vimage

    @property
    def is_vip(self) -> bool:
        """
        是否超级会员
        """

        return self._is_vip

    @property
    def is_god(self) -> bool:
        """
        是否贴吧大神
        """

        return self._is_god

    @property
    def is_blocked(self) -> bool:
        """
        是否被永久封禁屏蔽
        """

        return self._is_blocked

    @property
    def priv_like(self) -> int:
        """
        公开关注吧列表的设置状态

        Note:
            1完全可见 2好友可见 3完全隐藏
        """

        return self._priv_like

    @property
    def priv_reply(self) -> int:
        """
        帖子评论权限的设置状态

        Note:
            1允许所有人 5仅允许我的粉丝 6仅允许我的关注
        """

        return self._priv_reply

    @property
    def nick_name(self) -> str:
        """
        用户昵称
        """

        return self._nick_name_new

    @property
    def show_name(self) -> str:
        """
        显示名称
        """

        return self._nick_name_new or self._user_name

    @property
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        if self._user_name:
            return self._user_name
        elif self._portrait:
            return f"{self._nick_name_new}/{self._portrait}"
        else:
            return str(self._user_id)


class FragImage_pf(object):
    """
    图像碎片

    Attributes:
        src (str): 大图链接
        origin_src (str): 原图链接
        width (int): 图像宽度
        height (int): 图像高度
        hash (str): 百度图床hash
    """

    __slots__ = [
        '_src',
        '_origin_src',
        '_origin_size',
        '_width',
        '_height',
        '_hash',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._src = data_proto.big_pic
        self._origin_src = data_proto.origin_pic
        self._origin_size = data_proto.origin_size
        self._width = data_proto.width
        self._height = data_proto.height
        self._hash = None

    def __repr__(self) -> str:
        return str(
            {
                'src': self._src,
                'width': self._width,
                'height': self._height,
            }
        )

    @property
    def src(self) -> str:
        """
        大图链接

        Note:
            宽960px
        """

        return self._src

    @property
    def origin_src(self) -> str:
        """
        原图链接
        """

        return self._origin_src

    @property
    def origin_size(self) -> int:
        """
        原图大小

        Note:
            以字节为单位
        """

        return self._origin_size

    @property
    def width(self) -> int:
        """
        图像宽度
        """

        return self._width

    @property
    def height(self) -> int:
        """
        图像高度
        """

        return self._height

    @property
    def hash(self) -> str:
        """
        图像的百度图床hash
        """

        if self._hash is None:
            first_qmark_idx = self._src.find('?')
            end_idx = self._src.rfind('.', 0, first_qmark_idx)

            if end_idx == -1:
                self._hash = ''
            else:
                start_idx = self._src.rfind('/', 0, end_idx)
                self._hash = self._src[start_idx + 1 : end_idx]

        return self._hash


class Contents_pf(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        _objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_pf]): 表情碎片列表
        imgs (list[FragImage_pf]): 图像碎片列表
        ats (list[FragAt_pf]): @碎片列表
        links (list[FragLink_pf]): 链接碎片列表
        video (FragVideo_pf): 视频碎片
        voice (FragVoice_pf): 音频碎片
    """

    __slots__ = [
        '_text',
        '_texts',
        '_emojis',
        '_imgs',
        '_ats',
        '_links',
        '_video',
        '_voice',
    ]

    def _init(self, data_proto: TypeMessage) -> "Contents_pf":
        content_protos = data_proto.first_post_content

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_pf(proto)
                    self._texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_pf(proto)
                    self._emojis.append(frag)
                    yield frag
                elif _type in [3, 20]:
                    continue
                elif _type == 4:
                    frag = FragAt_pf(proto)
                    self._ats.append(frag)
                    self._texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_pf(proto)
                    self._links.append(frag)
                    self._texts.append(frag)
                    yield frag
                elif _type == 5:  # video
                    continue
                elif _type == 10:  # voice
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning(f"Unknown fragment type. type={_type} proto={proto}")

        self._text = None
        self._texts = []
        self._imgs = [FragImage_pf(p) for p in data_proto.media if p.type != 5]
        self._emojis = []
        self._ats = []
        self._links = []

        self._objs = list(_frags())
        self._objs += self._imgs

        if data_proto.video_info.video_width:
            self._video = FragVideo_pf()._init(data_proto.video_info)
            self._objs.append(self._video)
        else:
            self._video = FragVideo_pf()._init_null()

        if data_proto.voice_info:
            self._voice = FragVoice_pf()._init(data_proto.voice_info[0])
            self._objs.append(self._voice)
        else:
            self._voice = FragVoice_pf()._init_null()

        return self

    def _init_null(self) -> "Contents_pf":
        self._objs = []
        self._text = ""
        self._texts = []
        self._emojis = []
        self._imgs = []
        self._ats = []
        self._links = []
        self._video = FragVideo_pf()._init_null()
        self._voice = FragVoice_pf()._init_null()
        return self

    def __repr__(self) -> str:
        return str(self._objs)

    @property
    def text(self) -> str:
        """
        文本内容
        """

        if self._text is None:
            self._text = "".join(frag.text for frag in self.texts)
        return self._text

    @property
    def texts(self) -> List[TypeFragText]:
        """
        纯文本碎片列表
        """

        return self._texts

    @property
    def emojis(self) -> List[FragEmoji_pf]:
        """
        表情碎片列表
        """

        return self._emojis

    @property
    def imgs(self) -> List[FragImage_pf]:
        """
        图像碎片列表
        """

        return self._imgs

    @property
    def ats(self) -> List[FragAt_pf]:
        """
        @碎片列表
        """

        return self._ats

    @property
    def links(self) -> List[FragLink_pf]:
        """
        链接碎片列表
        """

        return self._links

    @property
    def video(self) -> FragVideo_pf:
        """
        视频碎片
        """

        return self._video

    @property
    def voice(self) -> FragVoice_pf:
        """
        音频碎片
        """

        return self._voice


class Thread_pf(object):
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
        create_time (int): 创建时间
    """

    __slots__ = [
        '_text',
        '_contents',
        '_title',
        '_fid',
        '_fname',
        '_tid',
        '_pid',
        '_user',
        '_author_id',
        '_vote_info',
        '_view_num',
        '_reply_num',
        '_share_num',
        '_agree',
        '_disagree',
        '_create_time',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._text = None
        self._contents = Contents_pf()._init(data_proto)
        self._title = data_proto.title
        self._fid = data_proto.forum_id
        self._fname = data_proto.forum_name
        self._tid = data_proto.thread_id
        self._pid = data_proto.post_id
        self._vote_info = VoteInfo()._init(data_proto.poll_info)
        self._view_num = data_proto.freq_num
        self._reply_num = data_proto.reply_num
        self._share_num = data_proto.share_num
        self._agree = data_proto.agree.agree_num
        self._disagree = data_proto.agree.disagree_num
        self._create_time = data_proto.create_time

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'user': self._user.log_name,
                'text': self.text,
            }
        )

    def __eq__(self, obj: "Thread_pf") -> bool:
        return self._pid == obj._pid

    def __hash__(self) -> int:
        return self._pid

    @property
    def text(self) -> str:
        """
        文本内容

        Note:
            如果有标题的话还会在正文前附上标题
        """

        if self._text is None:
            if self.title:
                self._text = f"{self._title}\n{self._contents.text}"
            else:
                self._text = self._contents.text
        return self._text

    @property
    def contents(self) -> Contents_pf:
        """
        正文内容碎片列表
        """

        return self._contents

    @property
    def title(self) -> str:
        """
        标题
        """

        return self._title

    @property
    def fid(self) -> int:
        """
        所在吧id
        """

        return self._fid

    @property
    def fname(self) -> str:
        """
        所在贴吧名
        """

        return self._fname

    @property
    def tid(self) -> int:
        """
        主题帖id
        """

        return self._tid

    @property
    def pid(self) -> int:
        """
        首楼回复id
        """

        return self._pid

    @property
    def user(self) -> UserInfo_pf:
        """
        发布者的用户信息
        """

        return self._user

    @property
    def author_id(self) -> int:
        """
        发布者的user_id
        """

        return self._author_id

    @property
    def vote_info(self) -> VoteInfo:
        """
        投票信息
        """

        return self._vote_info

    @property
    def view_num(self) -> int:
        """
        浏览量
        """

        return self._view_num

    @property
    def reply_num(self) -> int:
        """
        回复数
        """

        return self._reply_num

    @property
    def share_num(self) -> int:
        """
        分享数
        """

        return self._share_num

    @property
    def agree(self) -> int:
        """
        点赞数
        """

        return self._agree

    @property
    def disagree(self) -> int:
        """
        点踩数
        """

        return self._disagree

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._create_time
