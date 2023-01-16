from typing import Iterable, List

from .._classdef import Containers, Forum, TypeMessage, VirtualImage, VoteInfo
from .._classdef.contents import (
    FragAt,
    FragEmoji,
    FragLink,
    FragmentUnknown,
    FragText,
    FragTiebaPlus,
    TypeFragment,
    TypeFragText,
)
from .._helper import removeprefix

Forum_p = Forum
VirtualImage_p = VirtualImage

FragAt_p = FragAt_pt = FragAt_pc = FragAt
FragEmoji_p = FragEmoji_pt = FragEmoji_pc = FragEmoji
FragLink_p = FragLink_pt = FragLink_pc = FragLink
FragmentUnknown_p = FragmentUnknown_pt = FragmentUnknown_pc = FragmentUnknown
FragText_p = FragText_pt = FragText_pc = FragText
FragTiebaPlus_p = FragTiebaPlus_pt = FragTiebaPlus_pc = FragTiebaPlus


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
                'src': self.src,
                'show_width': self._show_width,
                'show_height': self._show_height,
            }
        )

    @property
    def src(self) -> str:
        """
        小图链接

        Note:
            宽720px
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

        has_voice (bool): 是否包含音频
    """

    __slots__ = [
        '_text',
        '_texts',
        '_emojis',
        '_imgs',
        '_ats',
        '_links',
        '_tiebapluses',
        '_has_voice',
    ]

    def _init(self, protos: Iterable[TypeMessage]) -> "Contents_p":
        def _init_by_type(proto):
            _type = proto.type
            # 0纯文本 9电话号 18话题 27百科词条
            if _type in [0, 9, 18, 27]:
                fragment = FragText_p(proto)
                self._texts.append(fragment)
            # 11:tid=5047676428
            elif _type in [2, 11]:
                fragment = FragEmoji_p(proto)
                self._emojis.append(fragment)
            # 20:tid=5470214675
            elif _type in [3, 20]:
                fragment = FragImage_p(proto)
                self._imgs.append(fragment)
            elif _type == 4:
                fragment = FragAt_p(proto)
                self._ats.append(fragment)
                self._texts.append(fragment)
            elif _type == 1:
                fragment = FragLink_p(proto)
                self._links.append(fragment)
                self._texts.append(fragment)
            elif _type == 10:
                fragment = FragmentUnknown_p()
                self._has_voice = True
            elif _type == 5:  # video
                fragment = FragmentUnknown_p()
            # 35|36:tid=7769728331 / 37:tid=7760184147
            elif _type in [35, 36, 37]:
                fragment = FragTiebaPlus_p(proto)
                self._tiebapluses.append(fragment)
                self._texts.append(fragment)
            else:
                fragment = FragmentUnknown_p(proto)
                from ..._logging import get_logger as LOG

                LOG().warning(f"Unknown fragment type. type={_type} frag={fragment}")

            return fragment

        self._text = None
        self._texts = []
        self._links = []
        self._imgs = []
        self._emojis = []
        self._ats = []
        self._tiebapluses = []
        self._has_voice = False

        self._objs = [_init_by_type(p) for p in protos]

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
        self._has_voice = False
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
    def has_voice(self) -> bool:
        """
        是否包含音频
        """

        return self._has_voice


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

        has_voice (bool): 是否包含音频
    """

    __slots__ = [
        '_text',
        '_texts',
        '_emojis',
        '_ats',
        '_links',
        '_tiebapluses',
        '_has_voice',
    ]

    def _init(self, protos: Iterable[TypeMessage]) -> "Contents_pc":
        def _init_by_type(proto):
            _type = proto.type
            # 0纯文本 9电话号 18话题 27百科词条
            if _type in [0, 9, 18, 27]:
                fragment = FragText_pc(proto)
                self._texts.append(fragment)
            # 11:tid=5047676428
            elif _type in [2, 11]:
                fragment = FragEmoji_pc(proto)
                self._emojis.append(fragment)
            elif _type == 4:
                fragment = FragAt_pc(proto)
                self._ats.append(fragment)
                self._texts.append(fragment)
            elif _type == 1:
                fragment = FragLink_pc(proto)
                self._links.append(fragment)
                self._texts.append(fragment)
            elif _type == 10:
                fragment = FragmentUnknown_pc()
                self._has_voice = True
            # 35|36:tid=7769728331 / 37:tid=7760184147
            elif _type in [35, 36, 37]:
                fragment = FragTiebaPlus_pc(proto)
                self._tiebapluses.append(fragment)
                self._texts.append(fragment)
            else:
                fragment = FragmentUnknown_pc(proto)
                from ..._logging import get_logger as LOG

                LOG().warning(f"Unknown fragment type. type={_type} frag={fragment}")

            return fragment

        self._text = None
        self._texts = []
        self._links = []
        self._emojis = []
        self._ats = []
        self._tiebapluses = []
        self._has_voice = False

        self._objs = [_init_by_type(p) for p in protos]

        return self

    def _init_null(self) -> "Contents_pc":
        self._objs = []
        self._text = ""
        self._texts = []
        self._emojis = []
        self._ats = []
        self._links = []
        self._tiebapluses = []
        self._has_voice = False
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
    def has_voice(self) -> bool:
        """
        是否包含音频
        """

        return self._has_voice


class Comment_p(object):
    """
    楼中楼信息

    Attributes:
        text (str): 文本内容
        contents (Contents_pc): 正文内容碎片列表

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        ppid (int): 所在回复id
        pid (int): 楼中楼id
        user (UserInfo_p): 发布者的用户信息
        author_id (int): 发布者的user_id
        reply_to_id (int): 被回复者的user_id

        floor (int): 所在楼层数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间
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
    ]

    def _init(self, data_proto: TypeMessage) -> "Comment_p":
        contents = Contents_pc()._init(data_proto.content)

        self._reply_to_id = 0
        if contents:
            first_frag = contents[0]
            if (
                len(contents) > 1
                and isinstance(first_frag, FragText_p)
                and first_frag.text == '回复 '
                and (reply_to_id := data_proto.content[1].uid)
            ):
                self._reply_to_id = reply_to_id
                if isinstance(contents[1], FragAt_p):
                    contents._ats = contents._ats[1:]
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

        return self

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'pid': self._pid,
                'floor': self._floor,
                'user': self.user.log_name,
                'text': self.text,
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
        所在回复id
        """

        return self._pid

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
                'user_name': self._user_name,
                'portrait': self._portrait,
                'show_name': self.show_name,
                'level': self._level,
                'glevel': self._glevel,
                'gender': self._gender,
                'ip': self._ip,
                'priv_like': self._priv_like,
                'priv_reply': self._priv_reply,
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

    def _init(self, data_proto: TypeMessage) -> "Post":
        self._text = None
        self._contents = Contents_p()._init(data_proto.content)
        self._sign = "".join(p.text for p in data_proto.signature.content if p.type == 0)
        self._comments = [Comment_p()._init(p) for p in data_proto.sub_post_list.sub_post_list]
        self._pid = data_proto.id
        self._author_id = data_proto.author_id
        self._vimage = VirtualImage_p()._init(data_proto)
        self._floor = data_proto.floor
        self._reply_num = data_proto.sub_post_number
        self._agree = data_proto.agree.agree_num
        self._disagree = data_proto.agree.disagree_num
        self._create_time = data_proto.time
        return self

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
                'src': self.src,
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
        '_tiebapluses',
        '_has_voice',
        '_has_video',
    ]

    def _init(self, protos: Iterable[TypeMessage]) -> "Contents_pt":
        def _init_by_type(proto) -> TypeFragment:
            _type = proto.type
            # 0纯文本 9电话号 18话题 27百科词条
            if _type in [0, 9, 18, 27]:
                fragment = FragText_pt(proto)
                self._texts.append(fragment)
            # 11:tid=5047676428
            elif _type in [2, 11]:
                fragment = FragEmoji_pt(proto)
                self._emojis.append(fragment)
            elif _type == 4:
                fragment = FragAt_pt(proto)
                self._ats.append(fragment)
                self._texts.append(fragment)
            elif _type == 1:
                fragment = FragLink_pt(proto)
                self._links.append(fragment)
                self._texts.append(fragment)
            elif _type == 5:  # video
                fragment = FragmentUnknown_pt()
                self._has_video = True
            # 35|36:tid=7769728331 / 37:tid=7760184147
            elif _type in [35, 36, 37]:
                fragment = FragTiebaPlus_pt(proto)
                self._tiebapluses.append(fragment)
                self._texts.append(fragment)
            else:
                fragment = FragmentUnknown_pt(proto)
                from ..._logging import get_logger as LOG

                LOG().warning(f"Unknown fragment type. type={_type} frag={fragment}")

            return fragment

        self._text = None
        self._texts = []
        self._links = []
        self._emojis = []
        self._ats = []
        self._tiebapluses = []
        self._has_voice = False
        self._has_video = False

        self._objs = [_init_by_type(p) for p in protos]

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
        fan_num (int): 粉丝数
        ip (str): ip归属地

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
        '_fan_num',
        '_ip',
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
        self._fan_num = data_proto.fans_num
        self._ip = data_proto.ip_address
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
        self._fan_num = 0
        self._ip = ''
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
                'user_name': self._user_name,
                'portrait': self._portrait,
                'show_name': self.show_name,
                'level': self._level,
                'glevel': self._glevel,
                'fan_num': self._fan_num,
                'ip': self._ip,
                'priv_like': self._priv_like,
                'priv_reply': self._priv_reply,
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
    def fan_num(self) -> int:
        """
        粉丝数
        """

        return self._fan_num

    @property
    def ip(self) -> str:
        """
        ip归属地
        """

        return self._ip

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
        self._contents = Contents_pt()._init(data_proto.content)
        img_frags = [FragImage_pt(p) for p in data_proto.media]
        self._contents._objs += img_frags
        self._contents._imgs = img_frags
        self._contents._has_voice = bool(data_proto.voice_info)
        self._author_id = self._contents._ats[0]._user_id
        del self._contents._ats[0]
        del self._contents._objs[0]

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
        reply_num (int): 回复数
        share_num (int): 分享数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间
        last_time (int): 最后回复时间
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
        '_reply_num',
        '_share_num',
        '_agree',
        '_disagree',
        '_create_time',
        '_last_time',
    ]

    def _init(self, data_proto: TypeMessage) -> "Thread_p":
        self._text = None
        self._title = data_proto.title
        self._tid = data_proto.id
        self._pid = data_proto.post_id
        self._user = UserInfo_pt()._init(data_proto.author)
        self._author_id = self._user._user_id
        self._type = data_proto.thread_type
        self._is_share = bool(data_proto.is_share_thread)
        self._reply_num = data_proto.reply_num
        self._share_num = data_proto.share_num
        self._agree = data_proto.agree.agree_num
        self._disagree = data_proto.agree.disagree_num
        self._create_time = data_proto.create_time
        self._last_time = data_proto.last_time_int

        if not self._is_share:
            self._contents = Contents_pt()._init(data_proto.origin_thread_info.content)
            img_frags = [FragImage_pt(p) for p in data_proto.origin_thread_info.media]
            self._contents._objs += img_frags
            self._contents._imgs = img_frags
            self._contents._has_voice = bool(data_proto.origin_thread_info.voice_info)
            self._vote_info = VoteInfo()._init(data_proto.origin_thread_info.poll_info)
            self._share_origin = ShareThread_pt()._init_null()
        else:
            self._contents = Contents_pt()._init_null()
            self._vote_info = VoteInfo()._init_null()
            self._share_origin = ShareThread_pt()._init(data_proto.origin_thread_info)

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
        self._reply_num = 0
        self._share_num = 0
        self._agree = 0
        self._disagree = 0
        self._create_time = 0
        self._last_time = 0
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

    @property
    def last_time(self) -> int:
        """
        最后回复时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._last_time


class Posts(Containers[Post]):
    """
    回复列表

    Attributes:
        _objs (list[Post]): 回复列表

        page (Page_p): 页信息
        has_more (bool): 是否还有下一页

        forum (Forum_p): 所在吧信息
        thread (Thread_p): 所在主题帖信息

        has_fold (bool): 是否存在折叠楼层
    """

    __slots__ = [
        '_page',
        '_forum',
        '_thread',
        '_has_fold',
    ]

    def _init(self, data_proto: TypeMessage) -> "Posts":

        self._page = Page_p()._init(data_proto.page)
        self._forum = Forum_p()._init(data_proto.forum)
        self._thread = Thread_p()._init(data_proto.thread)
        self._has_fold = bool(data_proto.has_fold_comment)

        self._thread._fid = self._forum._fid
        self._thread._fname = self._forum._fname

        self._objs = [Post()._init(p) for p in data_proto.post_list]
        users = {p.id: UserInfo_p()._init(p) for p in data_proto.user_list if p.id}
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

        return self

    def _init_null(self) -> "Posts":
        self._objs = []
        self._page = Page_p()._init_null()
        self._forum = Forum_p()._init_null()
        self._thread = Thread_p()._init_null()
        self._has_fold = False
        return self

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

    @property
    def has_fold(self) -> bool:
        """
        是否存在折叠楼层
        """

        return self._has_fold
