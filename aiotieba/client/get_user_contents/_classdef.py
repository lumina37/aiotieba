from typing import Iterable, List

from .._classdef import Containers, TypeMessage, VoteInfo
from .._classdef.contents import FragAt, FragEmoji, FragLink, FragmentUnknown, FragText, TypeFragment, TypeFragText

FragText_up = FragText_ut = FragText
FragAt_ut = FragAt
FragEmoji_ut = FragEmoji
FragLink_up = FragLink_ut = FragLink
FragmentUnknown_up = FragmentUnknown_ut = FragmentUnknown


class Contents_up(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        _objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        links (list[FragLink_up]): 链接碎片列表

        has_voice (bool): 是否包含音频
    """

    __slots__ = [
        '_text',
        '_texts',
        '_links',
        '_has_voice',
    ]

    def _init(self, protos: Iterable[TypeMessage]) -> "Contents_up":
        def _init_by_type(proto):
            _type = proto.type
            if _type in [0, 4]:
                fragment = FragText_up(proto)
                self._texts.append(fragment)
            elif _type == 1:
                fragment = FragLink_up(proto)
                self._links.append(fragment)
                self._texts.append(fragment)
            elif _type == 10:
                fragment = FragmentUnknown_up()
                self._has_voice = True
            else:
                fragment = FragmentUnknown_up(proto)
                from ..._logging import get_logger as LOG

                LOG().warning(f"Unknown fragment type. type={_type} frag={fragment}")

            return fragment

        self._text = None
        self._texts = []
        self._links = []
        self._has_voice = False

        self._objs = [_init_by_type(p) for p in protos]

        return self

    def _init_null(self) -> "Contents_up":
        self._objs = []
        self._text = ""
        self._texts = []
        self._links = []
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
    def links(self) -> List[FragLink_up]:
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


class UserInfo_u(object):
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

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
        '_nick_name_new',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_u":
        self._user_id = data_proto.user_id
        if '?' in (portrait := data_proto.user_portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.user_name
        self._nick_name_new = data_proto.name_show
        return self

    def _init_null(self) -> "UserInfo_u":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
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
            }
        )

    def __eq__(self, obj: "UserInfo_u") -> bool:
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


class UserPost(object):
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

        is_floor (bool): 是否为楼中楼

        create_time (int): 创建时间
    """

    __slots__ = [
        '_contents',
        '_fid',
        '_tid',
        '_pid',
        '_user',
        '_author_id',
        '_is_floor',
        '_create_time',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserPost":
        self._contents = Contents_up()._init(data_proto.post_content)
        self._pid = data_proto.post_id
        self._is_floor = bool(data_proto.post_type)
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

    def __eq__(self, obj: "UserPost") -> bool:
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
    def contents(self) -> Contents_up:
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
    def user(self) -> UserInfo_u:
        """
        发布者的用户信息
        """

        return self._user

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._create_time


class UserPosts(Containers[UserPost]):
    """
    用户历史回复信息列表

    Attributes:
        _objs (list[UserPost]): 用户历史回复信息列表

        fid (int): 所在吧id
        tid (int): 所在主题帖id
    """

    __slots__ = [
        '_fid',
        '_tid',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserPosts":
        self._fid = data_proto.forum_id
        self._tid = data_proto.thread_id
        self._objs = [UserPost()._init(p) for p in data_proto.content]
        for upost in self._objs:
            upost._fid = self._fid
            upost._tid = self._tid
        return self

    @property
    def fid(self) -> int:
        """
        所在吧id
        """

        return self._fid

    @property
    def tid(self) -> int:
        """
        所在主题帖id
        """

        return self._tid


class FragImage_ut(object):
    """
    图像碎片

    Attributes:
        src (str): 小图链接
        big_src (str): 大图链接
        origin_src (str): 原图链接
        width (int): 图像宽度
        height (int): 图像高度
        hash (str): 百度图床hash
    """

    __slots__ = [
        '_src',
        '_big_src',
        '_origin_src',
        '_origin_size',
        '_width',
        '_height',
        '_hash',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._src = data_proto.small_pic
        self._big_src = data_proto.big_pic
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
        小图链接

        Note:
            宽980px
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


class Contents_ut(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        _objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_ut]): 表情碎片列表
        imgs (list[FragImage_ut]): 图像碎片列表
        ats (list[FragAt_ut]): @碎片列表
        links (list[FragLink_ut]): 链接碎片列表

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

    def _init(self, protos: Iterable[TypeMessage]) -> "Contents_ut":
        def _init_by_type(proto):
            _type = proto.type
            # 0纯文本 9电话号 18话题 27百科词条
            if _type in [0, 9, 18, 27]:
                fragment = FragText_ut(proto)
                self._texts.append(fragment)
            # 11:tid=5047676428
            elif _type in [2, 11]:
                fragment = FragEmoji_ut(proto)
                self._emojis.append(fragment)
            # 20:tid=5470214675
            elif _type in [3, 20]:
                fragment = FragmentUnknown_ut()
            elif _type == 4:
                fragment = FragAt_ut(proto)
                self._ats.append(fragment)
                self._texts.append(fragment)
            elif _type == 1:
                fragment = FragLink_ut(proto)
                self._links.append(fragment)
                self._texts.append(fragment)
            elif _type == 5:  # video
                fragment = FragmentUnknown_ut()
                self._has_video = True
            elif _type == 10:
                fragment = FragmentUnknown_ut()
                self._has_voice = True
            else:
                fragment = FragmentUnknown_ut(proto)
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

    def _init_null(self) -> "Contents_ut":
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
    def emojis(self) -> List[FragEmoji_ut]:
        """
        表情碎片列表
        """

        return self._emojis

    @property
    def imgs(self) -> List[FragImage_ut]:
        """
        图像碎片列表
        """

        return self._imgs

    @property
    def ats(self) -> List[FragAt_ut]:
        """
        @碎片列表
        """

        return self._ats

    @property
    def links(self) -> List[FragLink_ut]:
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


class UserThread(object):
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
        '_vote_info',
        '_view_num',
        '_reply_num',
        '_share_num',
        '_agree',
        '_disagree',
        '_create_time',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserThread":
        self._text = None
        self._contents = Contents_ut()._init(data_proto.first_post_content)
        img_frags = [FragImage_ut(p) for p in data_proto.media]
        self._contents._objs += img_frags
        self._contents._imgs = img_frags
        self._title = data_proto.title
        self._fid = data_proto.forum_id
        self._fname = data_proto.forum_name
        self._tid = data_proto.thread_id
        self._pid = data_proto.post_id
        self._type = data_proto.thread_type
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

    def __eq__(self, obj: "UserThread") -> bool:
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
    def contents(self) -> Contents_ut:
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
    def user(self) -> UserInfo_u:
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
