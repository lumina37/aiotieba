from typing import Iterable, List

from .._classdef import Containers, Forum, TypeMessage
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

Forum_c = Forum

FragAt_c = FragAt_cp = FragAt
FragEmoji_c = FragEmoji_cp = FragEmoji
FragLink_c = FragLink_cp = FragLink
FragmentUnknown_c = FragmentUnknown_cp = FragmentUnknown
FragText_c = FragText_cp = FragText
FragTiebaPlus_c = FragTiebaPlus_cp = FragTiebaPlus


class Contents_c(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        _objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_c]): 表情碎片列表
        ats (list[FragAt_c]): @碎片列表
        links (list[FragLink_c]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_c]): 贴吧plus碎片列表

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

    def _init(self, protos: Iterable[TypeMessage]) -> "Contents_c":
        def _init_by_type(proto):
            _type = proto.type
            # 0纯文本 9电话号 18话题 27百科词条
            if _type in [0, 9, 18, 27]:
                fragment = FragText_c(proto)
                self._texts.append(fragment)
            # 11:tid=5047676428
            elif _type in [2, 11]:
                fragment = FragEmoji_c(proto)
                self._emojis.append(fragment)
            elif _type == 4:
                fragment = FragAt_c(proto)
                self._ats.append(fragment)
                self._texts.append(fragment)
            elif _type == 1:
                fragment = FragLink_c(proto)
                self._links.append(fragment)
                self._texts.append(fragment)
            elif _type == 10:
                fragment = FragmentUnknown_c()
                self._has_voice = True
            # 35|36:tid=7769728331 / 37:tid=7760184147
            elif _type in [35, 36, 37]:
                fragment = FragTiebaPlus_c(proto)
                self._tiebapluses.append(fragment)
                self._texts.append(fragment)
            else:
                fragment = FragmentUnknown_c(proto)
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

    def _init_null(self) -> "Contents_c":
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
    def emojis(self) -> List[FragEmoji_c]:
        """
        表情碎片列表
        """

        return self._emojis

    @property
    def ats(self) -> List[FragAt_c]:
        """
        @碎片列表
        """

        return self._ats

    @property
    def links(self) -> List[FragLink_c]:
        """
        链接碎片列表
        """

        return self._links

    @property
    def tiebapluses(self) -> List[FragTiebaPlus_c]:
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


class UserInfo_c(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        level (int): 等级
        gender (int): 性别

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
        '_gender',
        '_is_bawu',
        '_is_vip',
        '_is_god',
        '_priv_like',
        '_priv_reply',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_c":
        self._user_id = data_proto.id
        if '?' in (portrait := data_proto.portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.name
        self._nick_name_new = data_proto.name_show
        self._level = data_proto.level_id
        self._gender = data_proto.gender
        self._is_bawu = bool(data_proto.is_bawu)
        self._is_vip = bool(data_proto.new_tshow_icon)
        self._is_god = bool(data_proto.new_god_data.status)
        self._priv_like = priv_like if (priv_like := data_proto.priv_sets.like) else 1
        self._priv_reply = priv_reply if (priv_reply := data_proto.priv_sets.reply) else 1
        return self

    def _init_null(self) -> "UserInfo_c":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
        self._level = 0
        self._gender = 0
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
                'gender': self._gender,
                'priv_like': self._priv_like,
                'priv_reply': self._priv_reply,
            }
        )

    def __eq__(self, obj: "UserInfo_c") -> bool:
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
    def gender(self) -> int:
        """
        性别

        Note:
            0未知 1男 2女
        """

        return self._gender

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


class Comment(object):
    """
    楼中楼信息

    Attributes:
        text (str): 文本内容
        contents (Contents_c): 正文内容碎片列表

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        ppid (int): 所在回复id
        pid (int): 楼中楼id
        user (UserInfo_c): 发布者的用户信息
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

    def _init(self, data_proto: TypeMessage) -> "Comment":
        contents = Contents_c()._init(data_proto.content)

        self._reply_to_id = 0
        if contents:
            first_frag = contents[0]
            if (
                len(contents) > 1
                and isinstance(first_frag, FragText_c)
                and first_frag.text == '回复 '
                and (reply_to_id := data_proto.content[1].uid)
            ):
                self._reply_to_id = reply_to_id
                if isinstance(contents[1], FragAt_c):
                    contents._ats = contents._ats[1:]
                contents._objs = contents._objs[2:]
                contents._texts = contents._texts[2:]
                if contents.texts:
                    first_text_frag = contents.texts[0]
                    first_text_frag._text = removeprefix(first_text_frag._text, ' :')

        self._contents = contents

        self._pid = data_proto.id
        self._user = UserInfo_c()._init(data_proto.author)
        self._author_id = self._user._user_id
        self._agree = data_proto.agree.agree_num
        self._disagree = data_proto.agree.disagree_num
        self._create_time = data_proto.time

        return self

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'ppid': self._ppid,
                'pid': self._pid,
                'user': self._user.log_name,
                'text': self._contents.text,
                'floor': self._floor,
            }
        )

    def __eq__(self, obj: "Comment") -> bool:
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
    def contents(self) -> Contents_c:
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

        return self._ppid

    @property
    def pid(self) -> int:
        """
        楼中楼id
        """

        return self._pid

    @property
    def user(self) -> UserInfo_c:
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
        所在楼层数
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


class Page_c(object):
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

    def _init(self, data_proto: TypeMessage) -> "Page_c":
        self._page_size = data_proto.page_size
        self._current_page = data_proto.current_page
        self._total_page = data_proto.total_page
        self._total_count = data_proto.total_count
        self._has_more = self._current_page < self._total_page
        self._has_prev = self._current_page > 1
        return self

    def _init_null(self) -> "Page_c":
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


class UserInfo_ct(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        level (int): 等级

        is_god (bool): 是否大神

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
        '_is_god',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_ct":
        self._user_id = data_proto.id
        if '?' in (portrait := data_proto.portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.name
        self._nick_name_new = data_proto.name_show
        self._level = data_proto.level_id
        self._is_god = bool(data_proto.new_god_data.status)
        return self

    def _init_null(self) -> "UserInfo_ct":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
        self._level = 0
        self._is_god = False
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
            }
        )

    def __eq__(self, obj: "UserInfo_ct") -> bool:
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
    def is_god(self) -> bool:
        """
        是否贴吧大神
        """

        return self._is_god

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


class Thread_c(object):
    """
    主题帖信息

    Attributes:
        title (str): 标题

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        user (UserInfo_ct): 发布者的用户信息
        author_id (int): 发布者的user_id

        type (int): 帖子类型
        is_help (bool): 是否为求助帖

        reply_num (int): 回复数
    """

    __slots__ = [
        '_text',
        '_title',
        '_fid',
        '_fname',
        '_tid',
        '_user',
        '_author_id',
        '_type',
        '_reply_num',
    ]

    def _init(self, data_proto: TypeMessage) -> "Thread_c":
        self._title = data_proto.title
        self._tid = data_proto.id
        self._user = UserInfo_ct()._init(data_proto.author)
        self._author_id = self._user._user_id
        self._type = data_proto.thread_type
        self._reply_num = data_proto.reply_num
        return self

    def _init_null(self) -> "Thread_c":
        self._title = ""
        self._fid = 0
        self._fname = ''
        self._tid = 0
        self._user = UserInfo_ct()._init_null()
        self._author_id = 0
        self._type = 0
        self._reply_num = 0
        return self

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'user': self._user.log_name,
                'title': self._title,
            }
        )

    def __eq__(self, obj: "Thread_c") -> bool:
        return self._tid == obj._tid

    def __hash__(self) -> int:
        return self._tid

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
    def user(self) -> UserInfo_ct:
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
    def is_help(self) -> bool:
        """
        是否为求助帖
        """

        return self._type == 71

    @property
    def reply_num(self) -> int:
        """
        回复数
        """

        return self._reply_num


class FragImage_cp(object):
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


class Contents_cp(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        _objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_cp]): 表情碎片列表
        imgs (list[FragImage_cp]): 图像碎片列表
        ats (list[FragAt_cp]): @碎片列表
        links (list[FragLink_cp]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_cp]): 贴吧plus碎片列表

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

    def _init(self, protos: Iterable[TypeMessage]) -> "Contents_cp":
        def _init_by_type(proto):
            _type = proto.type
            # 0纯文本 9电话号 18话题 27百科词条
            if _type in [0, 9, 18, 27]:
                fragment = FragText_cp(proto)
                self._texts.append(fragment)
            # 11:tid=5047676428
            elif _type in [2, 11]:
                fragment = FragEmoji_cp(proto)
                self._emojis.append(fragment)
            # 20:tid=5470214675
            elif _type in [3, 20]:
                fragment = FragImage_cp(proto)
                self._imgs.append(fragment)
            elif _type == 4:
                fragment = FragAt_cp(proto)
                self._ats.append(fragment)
                self._texts.append(fragment)
            elif _type == 1:
                fragment = FragLink_cp(proto)
                self._links.append(fragment)
                self._texts.append(fragment)
            elif _type == 10:
                fragment = FragmentUnknown_cp()
                self._has_voice = True
            # 35|36:tid=7769728331 / 37:tid=7760184147
            elif _type in [35, 36, 37]:
                fragment = FragTiebaPlus_cp(proto)
                self._tiebapluses.append(fragment)
                self._texts.append(fragment)
            else:
                fragment = FragmentUnknown_cp(proto)
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

    def _init_null(self) -> "Contents_cp":
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
    def emojis(self) -> List[FragEmoji_cp]:
        """
        表情碎片列表
        """

        return self._emojis

    @property
    def imgs(self) -> List[FragImage_cp]:
        """
        图像碎片列表
        """

        return self._imgs

    @property
    def ats(self) -> List[FragAt_cp]:
        """
        @碎片列表
        """

        return self._ats

    @property
    def links(self) -> List[FragLink_cp]:
        """
        链接碎片列表
        """

        return self._links

    @property
    def tiebapluses(self) -> List[FragTiebaPlus_cp]:
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


class UserInfo_cp(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        level (int): 等级
        gender (int): 性别

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
        '_gender',
        '_is_bawu',
        '_is_vip',
        '_is_god',
        '_priv_like',
        '_priv_reply',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_cp":
        self._user_id = data_proto.id
        if '?' in (portrait := data_proto.portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.name
        self._nick_name_new = data_proto.name_show
        self._level = data_proto.level_id
        self._gender = data_proto.gender
        self._is_bawu = bool(data_proto.is_bawu)
        self._is_vip = bool(data_proto.new_tshow_icon)
        self._is_god = bool(data_proto.new_god_data.status)
        self._priv_like = priv_like if (priv_like := data_proto.priv_sets.like) else 1
        self._priv_reply = priv_reply if (priv_reply := data_proto.priv_sets.reply) else 1
        return self

    def _init_null(self) -> "UserInfo_cp":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
        self._level = 0
        self._gender = 0
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
                'gender': self._gender,
                'priv_like': self._priv_like,
                'priv_reply': self._priv_reply,
            }
        )

    def __eq__(self, obj: "UserInfo_cp") -> bool:
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
    def gender(self) -> int:
        """
        性别

        Note:
            0未知 1男 2女
        """

        return self._gender

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


class Post_c(object):
    """
    楼层信息

    Attributes:
        text (str): 文本内容
        contents (Contents_cp): 正文内容碎片列表
        sign (str): 小尾巴文本内容

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo_cp): 发布者的用户信息
        author_id (int): 发布者的user_id

        floor (int): 楼层数
        create_time (int): 创建时间
    """

    __slots__ = [
        '_text',
        '_contents',
        '_sign',
        '_fid',
        '_fname',
        '_tid',
        '_pid',
        '_user',
        '_author_id',
        '_floor',
        '_create_time',
    ]

    def _init(self, data_proto: TypeMessage) -> "Post_c":
        self._text = None
        self._contents = Contents_cp()._init(data_proto.content)
        self._sign = "".join(p.text for p in data_proto.signature.content if p.type == 0)
        self._pid = data_proto.id
        self._user = UserInfo_cp()._init(data_proto.author)
        self._author_id = self._user._user_id
        self._floor = data_proto.floor
        self._create_time = data_proto.time
        return self

    def _init_null(self) -> "Post_c":
        self._text = ""
        self._contents = Contents_cp()._init_null()
        self._sign = ""
        self._fid = 0
        self._fname = ''
        self._tid = 0
        self._pid = 0
        self._user = UserInfo_cp()._init_null()
        self._author_id = 0
        self._floor = 0
        self._create_time = 0
        return self

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'pid': self._pid,
                'user': self._user.log_name,
                'text': self.text,
                'floor': self._floor,
            }
        )

    def __eq__(self, obj: "Post_c") -> bool:
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
    def contents(self) -> Contents_cp:
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
    def user(self) -> UserInfo_cp:
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
    def floor(self) -> int:
        """
        楼层数
        """

        return self._floor

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._create_time


class Comments(Containers[Comment]):
    """
    楼中楼列表

    Attributes:
        _objs (list[Comment]): 楼中楼列表

        page (Page_c): 页信息
        has_more (bool): 是否还有下一页

        forum (Forum_c): 所在吧信息
        thread (Thread_c): 所在主题帖信息
        post (Post_c): 所在回复信息
    """

    __slots__ = [
        '_page',
        '_forum',
        '_thread',
        '_post',
    ]

    def _init(self, data_proto: TypeMessage) -> "Comments":
        self._page = Page_c()._init(data_proto.page)
        self._forum = Forum_c()._init(data_proto.forum)
        self._thread = Thread_c()._init(data_proto.thread)
        self._thread._fid = self._forum._fid
        self._thread._fname = self._forum._fname
        self._post = Post_c()._init(data_proto.post)
        self._post._fid = self._thread._fid
        self._post._fname = self._thread._fname
        self._post._tid = self._thread._tid

        self._objs = [Comment()._init(p) for p in data_proto.subpost_list]
        for comment in self._objs:
            comment._fid = self.forum._fid
            comment._fname = self.forum._fname
            comment._tid = self.thread._tid
            comment._ppid = self._post._pid
            comment._floor = self._post._floor

        return self

    def _init_null(self) -> "Comments":
        self._objs = []
        self._page = Page_c()._init_null()
        self._forum = Forum_c()._init_null()
        self._thread = Thread_c()._init_null()
        self._post = Post_c()._init_null()
        return self

    @property
    def page(self) -> Page_c:
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
    def forum(self) -> Forum_c:
        """
        所在吧信息
        """

        return self._forum

    @property
    def thread(self) -> Thread_c:
        """
        所在主题帖信息
        """

        return self._thread

    @property
    def post(self) -> Post_c:
        """
        所在回复信息
        """

        return self._post
