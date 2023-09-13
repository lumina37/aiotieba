from typing import List, Optional

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


class FragImage_p(object):
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

    __slots__ = [
        '_src',
        '_big_src',
        '_origin_src',
        '_origin_size',
        '_show_width',
        '_show_height',
        '_hash',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._src = data_proto.cdn_src
        self._big_src = data_proto.big_cdn_src
        self._origin_src = data_proto.origin_src
        self._origin_size = data_proto.origin_size

        show_width, _, show_height = data_proto.bsize.partition(',')
        self._show_width = int(show_width)
        self._show_height = int(show_height)

        self._hash = None

    def __repr__(self) -> str:
        return str(
            {
                'src': self._src,
                'show_width': self._show_width,
                'show_height': self._show_height,
            }
        )

    @property
    def src(self) -> str:
        """
        小图链接

        Note:
            宽720px\n
            一定是静态图
        """

        return self._src

    @property
    def big_src(self) -> str:
        """
        大图链接

        Note:
            宽960px
        """

        return self._big_src

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
    def show_width(self) -> int:
        """
        图像在客户端显示的宽度
        """

        return self._show_width

    @property
    def show_height(self) -> int:
        """
        图像在客户端显示的高度
        """

        return self._show_height

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


class FragVideo_p(object):
    """
    视频碎片

    Attributes:
        src (str): 视频链接
        cover_src (str): 封面链接
        player_src (str): 播放页链接
        duration (int): 视频长度
        width (int): 视频宽度
        height (int): 视频高度
        view_num (int): 浏览次数
    """

    __slots__ = [
        '_src',
        '_cover_src',
        '_duration',
        '_width',
        '_height',
        '_view_num',
    ]

    def _init(self, data_proto: TypeMessage) -> "FragVideo_p":
        self._src = data_proto.link
        self._cover_src = data_proto.src
        self._duration = data_proto.during_time
        self._width = data_proto.width
        self._height = data_proto.height
        self._view_num = data_proto.count
        return self

    def _init_null(self) -> "FragVideo_p":
        self._src = ''
        self._cover_src = ''
        self._duration = 0
        self._width = 0
        self._height = 0
        self._view_num = 0
        return self

    def __repr__(self) -> str:
        return str(
            {
                'cover_src': self._cover_src,
                'width': self._width,
                'height': self._height,
            }
        )

    def __bool__(self) -> bool:
        return bool(self._width)

    @property
    def src(self) -> str:
        """
        视频链接
        """

        return self._src

    @property
    def cover_src(self) -> str:
        """
        封面链接
        """

        return self._cover_src

    @property
    def duration(self) -> int:
        """
        视频长度

        Note:
            以秒为单位
        """

        return self._duration

    @property
    def width(self) -> int:
        """
        视频宽度
        """

        return self._width

    @property
    def height(self) -> int:
        """
        视频高度
        """

        return self._height

    @property
    def view_num(self) -> int:
        """
        浏览次数
        """

        return self._view_num


class Contents_p(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        _objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_p]): 表情碎片列表
        imgs (list[FragImage_p]): 图像碎片列表
        ats (list[FragAt_p]): @碎片列表
        links (list[FragLink_p]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_p]): 贴吧plus碎片列表
        voice (FragVoice_p): 音频碎片
        video (FragVideo_p): 视频碎片
    """

    __slots__ = [
        '_text',
        '_texts',
        '_emojis',
        '_imgs',
        '_ats',
        '_links',
        '_tiebapluses',
        '_voice',
        '_video',
    ]

    def _init(self, data_proto: TypeMessage) -> "Contents_p":
        content_protos = data_proto.content

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_p(proto)
                    self._texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_p(proto)
                    self._emojis.append(frag)
                    yield frag
                # 20:tid=5470214675
                elif _type in [3, 20]:
                    frag = FragImage_p(proto)
                    self._imgs.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_p(proto)
                    self._ats.append(frag)
                    self._texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_p(proto)
                    self._links.append(frag)
                    self._texts.append(frag)
                    yield frag
                elif _type == 10:  # voice
                    frag = FragVoice_p()._init(proto)
                    self._voice = frag
                    yield frag
                elif _type == 5:  # video
                    frag = FragVideo_p()._init(proto)
                    self._video = frag
                    yield frag
                # 35|36:tid=7769728331 / 37:tid=7760184147
                elif _type in [35, 36, 37]:
                    frag = FragTiebaPlus_p(proto)
                    self._tiebapluses.append(frag)
                    self._texts.append(frag)
                    yield frag
                # outdated tiebaplus
                elif _type == 34:
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning(f"Unknown fragment type. type={_type} proto={proto}")

        self._text = None
        self._texts = []
        self._emojis = []
        self._imgs = []
        self._ats = []
        self._links = []
        self._tiebapluses = []
        self._voice = FragVoice_p()._init_null()
        self._video = FragVideo_p()._init_null()
        self._objs = list(_frags())
        return self

    def _init_null(self) -> "Contents_p":
        self._objs = []
        self._text = ""
        self._texts = []
        self._emojis = []
        self._imgs = []
        self._ats = []
        self._links = []
        self._tiebapluses = []
        self._voice = FragVoice_p()._init_null()
        self._video = FragVideo_p()._init_null()
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
    def emojis(self) -> List[FragEmoji_p]:
        """
        表情碎片列表
        """

        return self._emojis

    @property
    def imgs(self) -> List[FragImage_p]:
        """
        图像碎片列表
        """

        return self._imgs

    @property
    def ats(self) -> List[FragAt_p]:
        """
        @碎片列表
        """

        return self._ats

    @property
    def links(self) -> List[FragLink_p]:
        """
        链接碎片列表
        """

        return self._links

    @property
    def tiebapluses(self) -> List[FragTiebaPlus_p]:
        """
        贴吧plus碎片列表
        """

        return self._tiebapluses

    @property
    def voice(self) -> FragVoice_p:
        """
        音频碎片
        """

        return self._voice

    @property
    def video(self) -> FragVideo_p:
        """
        视频碎片
        """

        return self._video


class Contents_pc(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        _objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_pc]): 表情碎片列表
        ats (list[FragAt_pc]): @碎片列表
        links (list[FragLink_pc]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_pc]): 贴吧plus碎片列表
        voice (FragVoice_pc): 音频碎片
    """

    __slots__ = [
        '_text',
        '_texts',
        '_emojis',
        '_ats',
        '_links',
        '_tiebapluses',
        '_voice',
    ]

    def _init(self, data_proto: TypeMessage) -> "Contents_pc":
        content_protos = data_proto.content

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_pc(proto)
                    self._texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_pc(proto)
                    self._emojis.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_pc(proto)
                    self._ats.append(frag)
                    self._texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_pc(proto)
                    self._links.append(frag)
                    self._texts.append(frag)
                    yield frag
                elif _type == 10:  # voice
                    frag = FragVoice_pc()._init(proto)
                    self._voice = frag
                    yield frag
                # 35|36:tid=7769728331 / 37:tid=7760184147
                elif _type in [35, 36, 37]:
                    frag = FragTiebaPlus_pc(proto)
                    self._tiebapluses.append(frag)
                    self._texts.append(frag)
                    yield frag
                # outdated tiebaplus
                elif _type == 34:
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning(f"Unknown fragment type. type={_type} proto={proto}")

        self._text = None
        self._texts = []
        self._emojis = []
        self._ats = []
        self._links = []
        self._tiebapluses = []
        self._voice = FragVoice_pc()._init_null()
        self._objs = list(_frags())
        return self

    def _init_null(self) -> "Contents_pc":
        self._objs = []
        self._text = ""
        self._texts = []
        self._emojis = []
        self._ats = []
        self._links = []
        self._tiebapluses = []
        self._voice = FragVoice_pc()._init_null()
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
    def emojis(self) -> List[FragEmoji_pc]:
        """
        表情碎片列表
        """

        return self._emojis

    @property
    def ats(self) -> List[FragAt_pc]:
        """
        @碎片列表
        """

        return self._ats

    @property
    def links(self) -> List[FragLink_pc]:
        """
        链接碎片列表
        """

        return self._links

    @property
    def tiebapluses(self) -> List[FragTiebaPlus_pc]:
        """
        贴吧plus碎片列表
        """

        return self._tiebapluses

    @property
    def voice(self) -> FragVoice_pc:
        """
        音频碎片列表
        """

        return self._voice


class Comment_p(object):
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
        create_time (int): 创建时间
        is_thread_author (bool): 是否楼主
    """

    __slots__ = [
        '_contents',
        '_fid',
        '_fname',
        '_tid',
        '_ppid',
        '_pid',
        '_user',
        '_author_id',
        '_reply_to_id',
        '_floor',
        '_agree',
        '_disagree',
        '_create_time',
        '_is_thread_author',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        contents = Contents_pc()._init(data_proto)

        self._reply_to_id = 0
        if contents:
            first_frag = contents[0]
            if (
                isinstance(first_frag, FragText_p)
                and first_frag.text == '回复 '
                and (reply_to_id := data_proto.content[1].uid)
            ):
                self._reply_to_id = reply_to_id
                if isinstance(contents[1], FragAt_p):
                    del contents._ats[0]
                contents._objs = contents._objs[2:]
                contents._texts = contents._texts[2:]
                if contents.texts:
                    first_text_frag = contents.texts[0]
                    first_text_frag._text = removeprefix(first_text_frag._text, ' :')

        self._contents = contents

        self._pid = data_proto.id
        self._author_id = data_proto.author_id
        self._agree = data_proto.agree.agree_num
        self._disagree = data_proto.agree.disagree_num
        self._create_time = data_proto.time

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'pid': self._pid,
                'user': self.user.log_name,
                'text': self.text,
                'floor': self._floor,
            }
        )

    def __eq__(self, obj: "Comment_p") -> bool:
        return self._pid == obj._pid

    def __hash__(self) -> int:
        return self._pid

    @property
    def text(self) -> str:
        """
        文本内容
        """

        return self._contents.text

    @property
    def contents(self) -> Contents_pc:
        """
        正文内容碎片列表
        """

        return self._contents

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
        所在主题帖id
        """

        return self._tid

    @property
    def ppid(self) -> int:
        """
        所在楼层id
        """

        return self._ppid

    @property
    def pid(self) -> int:
        """
        楼中楼id
        """

        return self._pid

    @property
    def user(self) -> "UserInfo_p":
        """
        发布者的用户信息
        """

        return self._user

    @property
    def author_id(self) -> int:
        """
        发布者的user_id
        """

        if not self._author_id:
            self._author_id = self.user.user_id
        return self._author_id

    @property
    def reply_to_id(self) -> int:
        """
        被回复者的user_id
        """

        return self._reply_to_id

    @property
    def floor(self) -> int:
        """
        点赞数
        """

        return self._floor

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

    @property
    def is_thread_author(self) -> bool:
        """
        是否楼主
        """

        return self._is_thread_author


class UserInfo_p(object):
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
        '_level',
        '_glevel',
        '_gender',
        '_ip',
        '_icons',
        '_is_bawu',
        '_is_vip',
        '_is_god',
        '_priv_like',
        '_priv_reply',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_p":
        self._user_id = data_proto.id
        if '?' in (portrait := data_proto.portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.name
        self._nick_name_new = data_proto.name_show
        self._level = data_proto.level_id
        self._glevel = data_proto.user_growth.level_id
        self._gender = data_proto.gender
        self._ip = data_proto.ip_address
        self._icons = [name for i in data_proto.iconinfo if (name := i.name)]
        self._is_bawu = bool(data_proto.is_bawu)
        self._is_vip = bool(data_proto.new_tshow_icon)
        self._is_god = bool(data_proto.new_god_data.status)
        self._priv_like = priv_like if (priv_like := data_proto.priv_sets.like) else 1
        self._priv_reply = priv_reply if (priv_reply := data_proto.priv_sets.reply) else 1
        return self

    def _init_null(self) -> "UserInfo_p":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
        self._level = 0
        self._glevel = 0
        self._gender = 0
        self._ip = ''
        self._icons = []
        self._is_bawu = False
        self._is_vip = False
        self._is_god = False
        self._priv_like = 1
        self._priv_reply = 1
        return self

    def __str__(self) -> str:
        return self._user_name or self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'show_name': self.show_name,
                'level': self._level,
            }
        )

    def __eq__(self, obj: "UserInfo_p") -> bool:
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
    def level(self) -> int:
        """
        等级
        """

        return self._level

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


class Post(object):
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

    __slots__ = [
        '_text',
        '_contents',
        '_sign',
        '_comments',
        '_fid',
        '_fname',
        '_tid',
        '_pid',
        '_user',
        '_author_id',
        '_vimage',
        '_floor',
        '_reply_num',
        '_agree',
        '_disagree',
        '_create_time',
        '_is_thread_author',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._text = None
        self._contents = Contents_p()._init(data_proto)
        self._sign = "".join(p.text for p in data_proto.signature.content if p.type == 0)
        self._comments = [Comment_p(p) for p in data_proto.sub_post_list.sub_post_list]
        self._pid = data_proto.id
        self._author_id = data_proto.author_id
        self._vimage = VirtualImage_p()._init(data_proto)
        self._floor = data_proto.floor
        self._reply_num = data_proto.sub_post_number
        self._agree = data_proto.agree.agree_num
        self._disagree = data_proto.agree.disagree_num
        self._create_time = data_proto.time

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'user': self._user.log_name,
                'text': self.text,
                'vimage': self._vimage._state,
                'floor': self._floor,
            }
        )

    def __eq__(self, obj: "Post") -> bool:
        return self._pid == obj._pid

    def __hash__(self) -> int:
        return self._pid

    @property
    def text(self) -> str:
        """
        文本内容

        Note:
            如果有小尾巴的话还会在正文后附上小尾巴
        """

        if self._text is None:
            if self._sign:
                self._text = f'{self._contents.text}\n{self._sign}'
            else:
                self._text = self._contents.text
        return self._text

    @property
    def contents(self) -> Contents_p:
        """
        正文内容碎片列表
        """

        return self._contents

    @property
    def sign(self) -> str:
        """
        小尾巴文本内容
        """

        return self._sign

    @property
    def comments(self) -> List["Comment_p"]:
        """
        楼中楼列表

        Note:
            不包含用户等级和ip属地信息
        """

        return self._comments

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
        所在主题帖id
        """

        return self._tid

    @property
    def pid(self) -> int:
        """
        回复id
        """

        return self._pid

    @property
    def user(self) -> UserInfo_p:
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
    def vimage(self) -> VirtualImage_p:
        """
        虚拟形象信息
        """

        return self._vimage

    @property
    def floor(self) -> int:
        """
        楼层数
        """

        return self._floor

    @property
    def reply_num(self) -> int:
        """
        楼中楼数
        """

        return self._reply_num

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

    @property
    def is_thread_author(self) -> bool:
        """
        是否楼主
        """

        return self._is_thread_author


class Page_p(object):
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

    __slots__ = [
        '_page_size',
        '_current_page',
        '_total_page',
        '_total_count',
        '_has_more',
        '_has_prev',
    ]

    def _init(self, data_proto: TypeMessage) -> "Page_p":
        self._page_size = data_proto.page_size
        self._current_page = data_proto.current_page
        self._total_page = data_proto.total_page
        self._total_count = data_proto.total_count
        self._has_more = bool(data_proto.has_more)
        self._has_prev = bool(data_proto.has_prev)
        return self

    def _init_null(self) -> "Page_p":
        self._page_size = 0
        self._current_page = 0
        self._total_page = 0
        self._total_count = 0
        self._has_more = False
        self._has_prev = False
        return self

    def __repr__(self) -> str:
        return str(
            {
                'current_page': self._current_page,
                'total_page': self._total_page,
                'has_more': self._has_more,
                'has_prev': self._has_prev,
            }
        )

    @property
    def page_size(self) -> int:
        """
        页大小
        """

        return self._page_size

    @property
    def current_page(self) -> int:
        """
        当前页码
        """

        return self._current_page

    @property
    def total_page(self) -> int:
        """
        总页码
        """

        return self._total_page

    @property
    def total_count(self) -> int:
        """
        总计数
        """

        return self._total_count

    @property
    def has_more(self) -> bool:
        """
        是否有后继页
        """

        return self._has_more

    @property
    def has_prev(self) -> bool:
        """
        是否有前驱页
        """

        return self._has_prev


class Forum_p(object):
    """
    吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        member_num (int): 吧会员数
        post_num (int): 发帖量
    """

    __slots__ = [
        '_fid',
        '_fname',
        '_member_num',
        '_post_num',
    ]

    def _init(self, data_proto: TypeMessage) -> "Forum_p":
        self._fid = data_proto.id
        self._fname = data_proto.name
        self._member_num = data_proto.member_num
        self._post_num = data_proto.post_num
        return self

    def _init_null(self) -> "Forum_p":
        self._fid = 0
        self._fname = ''
        self._member_num = 0
        self._post_num = 0
        return self

    def __repr__(self) -> str:
        return str(
            {
                'fid': self._fid,
                'fname': self._fname,
            }
        )

    @property
    def fid(self) -> int:
        """
        贴吧id
        """

        return self._fid

    @property
    def fname(self) -> str:
        """
        贴吧名
        """

        return self._fname

    @property
    def member_num(self) -> int:
        """
        吧会员数
        """

        return self._member_num

    @property
    def post_num(self) -> int:
        """
        发帖量
        """

        return self._post_num


class FragImage_pt(object):
    """
    图像碎片

    Attributes:
        src (str): 小图链接
        big_src (str): 大图链接
        origin_src (str): 原图链接
        show_width (int): 图像在客户端预览显示的宽度
        show_height (int): 图像在客户端预览显示的高度
        hash (str): 百度图床hash
    """

    __slots__ = [
        '_src',
        '_big_src',
        '_origin_src',
        '_origin_size',
        '_show_width',
        '_show_height',
        '_hash',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._src = data_proto.water_pic
        self._big_src = data_proto.small_pic
        self._origin_src = data_proto.big_pic
        self._show_width = data_proto.width
        self._show_height = data_proto.height
        self._hash = None

    def __repr__(self) -> str:
        return str(
            {
                'src': self._src,
                'show_width': self._show_width,
                'show_height': self._show_height,
            }
        )

    @property
    def src(self) -> str:
        """
        小图链接

        Note:
            宽580px
        """

        return self._src

    @property
    def big_src(self) -> str:
        """
        大图链接

        Note:
            宽720px
        """

        return self._big_src

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
        """

        return self._origin_size

    @property
    def show_width(self) -> int:
        """
        图像在客户端显示的宽度
        """

        return self._show_width

    @property
    def show_height(self) -> int:
        """
        图像在客户端显示的高度
        """

        return self._show_height

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


class Contents_pt(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        _objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_pt]): 表情碎片列表
        imgs (list[FragImage_pt]): 图像碎片列表
        ats (list[FragAt_pt]): @碎片列表
        links (list[FragLink_pt]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_pt]): 贴吧plus碎片列表
        video (FragVideo_pt): 视频碎片
        voice (FragVoice_pt): 视频碎片
    """

    __slots__ = [
        '_text',
        '_texts',
        '_emojis',
        '_imgs',
        '_ats',
        '_links',
        '_tiebapluses',
        '_video',
        '_voice',
    ]

    def _init(self, data_proto: TypeMessage) -> "Contents_pt":
        content_protos = data_proto.content

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_pt(proto)
                    self._texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_pt(proto)
                    self._emojis.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_pt(proto)
                    self._ats.append(frag)
                    self._texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_pt(proto)
                    self._links.append(frag)
                    self._texts.append(frag)
                    yield frag
                # 35|36:tid=7769728331 / 37:tid=7760184147
                elif _type in [35, 36, 37]:
                    frag = FragTiebaPlus_pt(proto)
                    self._tiebapluses.append(frag)
                    self._texts.append(frag)
                    yield frag
                # outdated tiebaplus
                elif _type == 34:
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning(f"Unknown fragment type. type={_type} proto={proto}")

        self._text = None
        self._texts = []
        self._emojis = []
        self._imgs = [FragImage_pt(p) for p in data_proto.media]
        self._ats = []
        self._links = []
        self._tiebapluses = []

        self._objs = list(_frags())
        del self._ats[0]
        del self._objs[0]
        self._objs += self._imgs

        if data_proto.video_info.video_width:
            self._video = FragVideo_pt()._init(data_proto.video_info)
            self._objs.append(self._video)
        else:
            self._video = FragVideo_pt()._init_null()

        if data_proto.voice_info:
            self._voice = FragVoice_pt()._init(data_proto.voice_info[0])
            self._objs.append(self._voice)
        else:
            self._voice = FragVoice_pt()._init_null()

        return self

    def _init_null(self) -> "Contents_pt":
        self._objs = []
        self._text = ""
        self._texts = []
        self._emojis = []
        self._imgs = []
        self._ats = []
        self._links = []
        self._tiebapluses = []
        self._video = FragVideo_pt()._init_null()
        self._voice = FragVoice_pt()._init_null()
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
    def emojis(self) -> List[FragEmoji_pt]:
        """
        表情碎片列表
        """

        return self._emojis

    @property
    def imgs(self) -> List[FragImage_pt]:
        """
        图像碎片列表
        """

        return self._imgs

    @property
    def ats(self) -> List[FragAt_pt]:
        """
        @碎片列表
        """

        return self._ats

    @property
    def links(self) -> List[FragLink_pt]:
        """
        链接碎片列表
        """

        return self._links

    @property
    def tiebapluses(self) -> List[FragTiebaPlus_pt]:
        """
        贴吧plus碎片列表
        """

        return self._tiebapluses

    @property
    def video(self) -> FragVideo_pt:
        """
        视频碎片
        """

        return self._video

    @property
    def voice(self) -> FragVoice_pt:
        """
        音频碎片
        """

        return self._voice


class UserInfo_pt(object):
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
        '_level',
        '_glevel',
        '_ip',
        '_icons',
        '_is_bawu',
        '_is_vip',
        '_is_god',
        '_priv_like',
        '_priv_reply',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_pt":
        self._user_id = data_proto.id
        if '?' in (portrait := data_proto.portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.name
        self._nick_name_new = data_proto.name_show
        self._level = data_proto.level_id
        self._glevel = data_proto.user_growth.level_id
        self._ip = data_proto.ip_address
        self._icons = [name for i in data_proto.iconinfo if (name := i.name)]
        self._is_bawu = bool(data_proto.is_bawu)
        self._is_vip = bool(data_proto.new_tshow_icon)
        self._is_god = bool(data_proto.new_god_data.status)
        self._priv_like = priv_like if (priv_like := data_proto.priv_sets.like) else 1
        self._priv_reply = priv_reply if (priv_reply := data_proto.priv_sets.reply) else 1
        return self

    def _init_null(self) -> "UserInfo_pt":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
        self._level = 0
        self._glevel = 0
        self._ip = ''
        self._icons = []
        self._is_bawu = False
        self._is_vip = False
        self._is_god = False
        self._priv_like = 1
        self._priv_reply = 1
        return self

    def __str__(self) -> str:
        return self._user_name or self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'show_name': self.show_name,
                'level': self._level,
            }
        )

    def __eq__(self, obj: "UserInfo_pt") -> bool:
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
    def level(self) -> int:
        """
        等级
        """

        return self._level

    @property
    def glevel(self) -> int:
        """
        贴吧成长等级
        """

        return self._glevel

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


class ShareThread_pt(object):
    """
    被分享的主题帖信息

    Attributes:
        text (str): 文本内容
        contents (Contents_pt): 正文内容碎片列表
        title (str): 标题内容

        author_id (int): 发布者的user_id

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid

        vote_info (VoteInfo): 投票内容
    """

    __slots__ = [
        '_text',
        '_contents',
        '_title',
        '_author_id',
        '_fid',
        '_fname',
        '_tid',
        '_vote_info',
    ]

    def _init(self, data_proto: TypeMessage) -> "ShareThread_pt":
        self._text = None
        self._contents = Contents_pt()._init(data_proto)
        self._author_id = data_proto.content[0].uid if data_proto.content else 0
        self._title = data_proto.title
        self._fid = data_proto.fid
        self._fname = data_proto.fname
        self._tid = int(tid) if (tid := data_proto.tid) else 0
        self._vote_info = VoteInfo()._init(data_proto.poll_info)

        return self

    def _init_null(self) -> "ShareThread_pt":
        self._text = ""
        self._contents = Contents_pt()._init_null()
        self._title = ''
        self._fid = 0
        self._fname = ''
        self._tid = 0
        self._vote_info = VoteInfo()._init_null()
        return self

    def __repr__(self) -> str:
        return str(
            {
                'fname': self._fname,
                'tid': self._tid,
                'text': self.text,
            }
        )

    def __eq__(self, obj: "ShareThread_pt") -> bool:
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
    def contents(self) -> Contents_pt:
        """
        正文内容碎片列表
        """

        return self._contents

    @property
    def title(self) -> str:
        """
        帖子标题
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
    def author_id(self) -> int:
        """
        发布者的user_id
        """

        return self._author_id

    @property
    def vote_info(self) -> VoteInfo:
        """
        投票内容
        """

        return self._vote_info


class Thread_p(object):
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
        '_type',
        '_is_share',
        '_vote_info',
        '_share_origin',
        '_view_num',
        '_reply_num',
        '_share_num',
        '_agree',
        '_disagree',
        '_create_time',
    ]

    def _init(self, data_proto: TypeMessage) -> "Thread_p":
        thread_proto = data_proto.thread
        self._text = None
        self._title = thread_proto.title
        self._tid = thread_proto.id
        self._pid = thread_proto.post_id
        self._user = UserInfo_pt()._init(thread_proto.author)
        self._author_id = self._user._user_id
        self._type = thread_proto.thread_type
        self._is_share = bool(thread_proto.is_share_thread)
        self._view_num = data_proto.thread_freq_num
        self._reply_num = thread_proto.reply_num
        self._share_num = thread_proto.share_num
        self._agree = thread_proto.agree.agree_num
        self._disagree = thread_proto.agree.disagree_num
        self._create_time = thread_proto.create_time

        if not self._is_share:
            real_thread_proto = thread_proto.origin_thread_info
            self._contents = Contents_pt()._init(real_thread_proto)
            self._vote_info = VoteInfo()._init(real_thread_proto.poll_info)
            self._share_origin = ShareThread_pt()._init_null()
        else:
            self._contents = Contents_pt()._init_null()
            self._vote_info = VoteInfo()._init_null()
            self._share_origin = ShareThread_pt()._init(thread_proto.origin_thread_info)

        return self

    def _init_null(self) -> "Thread_p":
        self._text = ""
        self._contents = Contents_pt()._init_null()
        self._title = ''
        self._fid = 0
        self._fname = ''
        self._tid = 0
        self._pid = 0
        self._user = UserInfo_pt()._init_null()
        self._author_id = 0
        self._type = 0
        self._is_share = False
        self._vote_info = VoteInfo()._init_null()
        self._share_origin = ShareThread_pt()._init_null()
        self._view_num = 0
        self._reply_num = 0
        self._share_num = 0
        self._agree = 0
        self._disagree = 0
        self._create_time = 0
        return self

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'user': self._user.log_name,
                'text': self.text,
            }
        )

    def __eq__(self, obj: "Thread_p") -> bool:
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
    def contents(self) -> Contents_pt:
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
    def user(self) -> UserInfo_pt:
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
    def type(self) -> int:
        """
        帖子类型
        """

        return self._type

    @property
    def is_share(self) -> bool:
        """
        是否分享帖
        """

        return self._is_share

    @property
    def is_help(self) -> bool:
        """
        是否为求助帖
        """

        return self._type == 71

    @property
    def vote_info(self) -> VoteInfo:
        """
        投票信息
        """

        return self._vote_info

    @property
    def share_origin(self) -> ShareThread_pt:
        """
        转发来的原帖内容
        """

        return self._share_origin

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


class Posts(Containers[Post]):
    """
    回复列表

    Attributes:
        _objs (list[Post]): 回复列表

        page (Page_p): 页信息
        has_more (bool): 是否还有下一页

        forum (Forum_p): 所在吧信息
        thread (Thread_p): 所在主题帖信息
    """

    __slots__ = [
        '_page',
        '_forum',
        '_thread',
    ]

    def __init__(self, data_proto: Optional[TypeMessage] = None) -> None:
        if data_proto:
            self._page = Page_p()._init(data_proto.page)
            self._forum = Forum_p()._init(data_proto.forum)
            self._thread = Thread_p()._init(data_proto)

            self._thread._fid = self._forum._fid
            self._thread._fname = self._forum._fname

            self._objs = [Post(p) for p in data_proto.post_list]
            users = {i: UserInfo_p()._init(p) for p in data_proto.user_list if (i := p.id)}
            for post in self._objs:
                post._fid = self._forum._fid
                post._fname = self._forum._fname
                post._tid = self._thread._tid
                post._user = users[post._author_id]
                post._is_thread_author = self._thread._author_id == post._author_id
                for comment in post.comments:
                    comment._fid = post._fid
                    comment._fname = post._fname
                    comment._tid = post._tid
                    comment._ppid = post._pid
                    comment._floor = post._floor
                    comment._user = users[comment._author_id]
                    comment._is_thread_author = self._thread._author_id == comment._author_id

        else:
            self._objs = []
            self._page = Page_p()._init_null()
            self._forum = Forum_p()._init_null()
            self._thread = Thread_p()._init_null()

    @property
    def page(self) -> Page_p:
        """
        页信息
        """

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._page._has_more

    @property
    def forum(self) -> Forum_p:
        """
        所在吧信息
        """

        return self._forum

    @property
    def thread(self) -> Thread_p:
        """
        所在主题帖信息
        """

        return self._thread
