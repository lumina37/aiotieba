from typing import Iterable, List

from .._classdef import Containers, TypeMessage, VoteInfo
from .._classdef.contents import FragAt, FragEmoji, FragLink, FragmentUnknown, FragText, TypeFragment, TypeFragText

FragAt_home = FragAt
FragEmoji_home = FragEmoji
FragLink_home = FragLink
FragmentUnknown_home = FragmentUnknown
FragText_home = FragText


class VirtualImage_home(object):
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

    def _init(self, data_proto: TypeMessage) -> "VirtualImage_home":
        self._enabled = bool(data_proto.isset_virtual_image)
        self._state = data_proto.personal_state.text
        return self

    def _init_null(self) -> "VirtualImage_home":
        self._enabled = False
        self._state = ''
        return self

    def __str__(self) -> str:
        return self._state

    def __repr__(self) -> str:
        return str(
            {
                'enabled': self.enabled,
                'state': self.state,
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


class UserInfo_home(object):
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
        fan_num (int): 粉丝数
        follow_num (int): 关注数
        sign (str): 个性签名
        ip (str): ip归属地
        vimage (VirtualImage_home): 虚拟形象信息

        is_bawu (bool): 是否吧务
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
        '_fan_num',
        '_follow_num',
        '_sign',
        '_vimage',
        '_ip',
        '_is_bawu',
        '_is_vip',
        '_is_god',
        '_is_blocked',
        '_priv_like',
        '_priv_reply',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_home":
        self._user_id = data_proto.id
        if '?' in (portrait := data_proto.portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.name
        self._nick_name_new = data_proto.name_show
        self._tieba_uid = int(tieba_uid) if (tieba_uid := data_proto.tieba_uid) else 0
        self._glevel = data_proto.user_growth.level_id
        self._gender = data_proto.sex
        self._age = float(age) if (age := data_proto.tb_age) else 0.0
        self._post_num = data_proto.post_num
        self._fan_num = data_proto.fans_num
        self._follow_num = data_proto.concern_num
        self._sign = data_proto.intro
        self._ip = data_proto.ip_address
        self._vimage = VirtualImage_home()._init(data_proto.virtual_image_info)
        self._is_bawu = bool(data_proto.is_bawu)
        self._is_vip = bool(data_proto.new_tshow_icon)
        self._is_god = bool(data_proto.new_god_data.status)
        self._priv_like = priv_like if (priv_like := data_proto.priv_sets.like) else 1
        self._priv_reply = priv_reply if (priv_reply := data_proto.priv_sets.reply) else 1
        return self

    def _init_null(self) -> "UserInfo_home":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
        self._tieba_uid = 0
        self._glevel = 0
        self._gender = 0
        self._age = 0.0
        self._post_num = 0
        self._fan_num = 0
        self._follow_num = 0
        self._sign = ''
        self._vimage = VirtualImage_home()._init_null()
        self._ip = ''
        self._is_bawu = False
        self._is_vip = False
        self._is_god = False
        self._is_blocked = False
        self._priv_like = 1
        self._priv_reply = 1
        return self

    def __str__(self) -> str:
        return self._user_name or self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'user_name': self._user_name,
                'portrait': self._portrait,
                'show_name': self.show_name,
                'tieba_uid': self._tieba_uid,
                'glevel': self._glevel,
                'gender': self._gender,
                'age': self._age,
                'post_num': self._post_num,
                'sign': self._sign,
                'vimage': self._vimage._state,
                'ip': self._ip,
                'priv_like': self._priv_like,
            }
        )

    def __eq__(self, obj: "UserInfo_home") -> bool:
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
            唯一 不可变 不可为空
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
            唯一 可变 可为空
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
            唯一 不可变 可为空
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
    def vimage(self) -> VirtualImage_home:
        """
        虚拟形象信息
        """

        return self._vimage

    @property
    def is_bawu(self) -> bool:
        """
        是否吧务
        """

        return self._is_bawu

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


class FragImage_home(object):
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
                'src': self.src,
                'width': self._width,
                'height': self._height,
            }
        )

    @property
    def src(self) -> str:
        """
        原图链接
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


class Contents_home(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        _objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_home]): 表情碎片列表
        imgs (list[FragImage_home]): 图像碎片列表
        ats (list[FragAt_home]): @碎片列表
        links (list[FragLink_home]): 链接碎片列表

        has_voice (bool): 是否包含音频
        has_video (bool): 是否包含视频
    """

    __slots__ = [
        '_text',
        '_texts',
        '_emojis',
        '_imgs',
        '_ats',
        '_links',
        '_has_voice',
        '_has_video',
    ]

    def _init(self, protos: Iterable[TypeMessage]) -> "Contents_home":
        def _init_by_type(proto):
            _type = proto.type
            # 0纯文本 9电话号 18话题 27百科词条
            if _type in [0, 9, 18, 27]:
                fragment = FragText_home(proto)
                self._texts.append(fragment)
            # 11:tid=5047676428
            elif _type in [2, 11]:
                fragment = FragEmoji_home(proto)
                self._emojis.append(fragment)
            elif _type == 3:
                fragment = FragmentUnknown_home()
            elif _type == 4:
                fragment = FragAt_home(proto)
                self._ats.append(fragment)
                self._texts.append(fragment)
            elif _type == 1:
                fragment = FragLink_home(proto)
                self._links.append(fragment)
                self._texts.append(fragment)
            elif _type == 5:  # video
                fragment = FragmentUnknown_home()
                self._has_video = True
            elif _type == 10:
                fragment = FragmentUnknown_home()
                self._has_voice = True
            else:
                fragment = FragmentUnknown_home(proto)
                from ..._logging import get_logger as LOG

                LOG().warning(f"Unknown fragment type. type={_type} frag={fragment}")

            return fragment

        self._text = None
        self._texts = []
        self._links = []
        self._imgs = []
        self._emojis = []
        self._ats = []
        self._has_voice = False
        self._has_video = False

        self._objs = [_init_by_type(p) for p in protos]

        return self

    def _init_null(self) -> "Contents_home":
        self._objs = []
        self._text = ""
        self._texts = []
        self._emojis = []
        self._imgs = []
        self._ats = []
        self._links = []
        self._has_voice = False
        self._has_video = False
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
    def emojis(self) -> List[FragEmoji_home]:
        """
        表情碎片列表
        """

        return self._emojis

    @property
    def imgs(self) -> List[FragImage_home]:
        """
        图像碎片列表
        """

        return self._imgs

    @property
    def ats(self) -> List[FragAt_home]:
        """
        @碎片列表
        """

        return self._ats

    @property
    def links(self) -> List[FragLink_home]:
        """
        链接碎片列表
        """

        return self._links

    @property
    def has_voice(self) -> bool:
        """
        是否包含音频
        """

        return self._has_voice

    @property
    def has_video(self) -> bool:
        """
        是否包含视频
        """

        return self._has_video


class Thread_home(object):
    """
    主题帖信息

    Attributes:
        text (str): 文本内容
        contents (Contents_home): 正文内容碎片列表
        title (str): 标题

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼回复pid
        user (UserInfo_home): 发布者的用户信息
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

    def _init(self, data_proto: TypeMessage) -> "Thread_home":
        self._text = None
        self._contents = Contents_home()._init(data_proto.first_post_content)
        img_frags = [FragImage_home(p) for p in data_proto.media]
        self._contents._objs += img_frags
        self._contents._imgs = img_frags
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
        return self

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'pid': self._pid,
                'user': self._user.log_name,
                'text': self.text,
            }
        )

    def __eq__(self, obj: "Thread_home") -> bool:
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
    def contents(self) -> Contents_home:
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
    def user(self) -> UserInfo_home:
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
