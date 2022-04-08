# -*- coding:utf-8 -*-
__all__ = ['BasicUserInfo', 'UserInfo',
           'Thread', 'Post', 'Comment', 'At', 'Reply', 'Search',
           'Threads', 'Posts', 'Comments', 'Ats', 'Replys', 'Searches',
           'Fragments'
           ]

from collections.abc import Callable, Iterable
from typing import Generic, Literal, Optional, TypeVar, Union, final

from google.protobuf.json_format import ParseDict

from ._logger import log
from .tieba_proto import *


def _int_prop_check_ignore_none(default_val: int) -> Callable:
    """
    装饰器实现对int类型属性的赋值前检查。忽略传入None的异常

    Args:
        default_val (int): 传入None时采用的默认值
    """

    def wrapper(func) -> Callable:
        def foo(self, new_val):
            if new_val:
                try:
                    new_val = int(new_val)
                except ValueError as err:
                    log.warning(f"{err} happens in {func.__name__}")
                    new_val = default_val
            else:
                new_val = default_val
            return func(self, new_val)
        return foo

    return wrapper


class BasicUserInfo(object):
    """
    基本用户属性

    Args:
        _id (Union[str, int, None]): 用于快速构造UserInfo的自适应参数 输入用户名/portrait/user_id
        user_proto (User_pb2.User)

    Fields:
        user_id (int): 贴吧旧版user_id
        user_name (str): 发帖用户名
        portrait (str): 用户头像portrait值
        nick_name (str): 发帖人昵称
    """

    __slots__ = ['_raw_data', '_user_id',
                 'user_name', '_portrait', '_nick_name']

    def __init__(self, _id: Union[str, int, None] = None, user_proto: Optional[User_pb2.User] = None) -> None:

        self._init_null()

        if _id:
            self._init_by_id(_id)

        elif user_proto:
            self._init_by_data(user_proto)

    def _init_by_id(self, _id: Union[str, int]) -> None:

        if isinstance(_id, int):
            self.user_id = _id

        else:
            self.portrait = _id
            if not self.portrait:
                self.user_name = _id

    def _init_by_data(self, user_proto: User_pb2.User) -> None:

        self._raw_data = user_proto

        self._user_id = user_proto.id
        self.user_name = user_proto.name
        self.portrait = user_proto.portrait
        self.nick_name = user_proto.name_show

    def _init_null(self) -> None:

        self._raw_data = None

        self.user_name = ''
        self._nick_name = ''
        self._portrait = ''
        self._user_id = 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [user_id:{self._user_id} / user_name:{self.user_name} / portrait:{self._portrait} / nick_name:{self._nick_name}]"

    def __eq__(self, obj) -> int:
        return self._user_id == obj.user_id and self.user_name == obj.user_name and self._portrait == obj.portrait

    def __hash__(self) -> int:
        return self._user_id

    def __int__(self) -> int:
        return self._user_id

    def __bool__(self) -> bool:
        return bool(self._user_id)

    @staticmethod
    def is_portrait(portrait: str) -> bool:
        return portrait.startswith('tb.')

    @staticmethod
    def is_user_id(user_id: int) -> bool:
        return isinstance(user_id, int)

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    @_int_prop_check_ignore_none(0)
    def user_id(self, new_user_id: int) -> None:
        self._user_id = int(new_user_id)

    @property
    def portrait(self) -> str:
        return self._portrait

    @portrait.setter
    def portrait(self, new_portrait: str) -> None:

        if new_portrait and self.is_portrait(new_portrait):

            beg_start = 33
            q_index = new_portrait.find('?', beg_start)
            and_index = new_portrait.find('&', beg_start)

            if q_index != -1:
                self._portrait = new_portrait[:q_index]
            elif and_index != -1:
                self._portrait = new_portrait[:and_index]
            else:
                self._portrait = new_portrait

        else:
            self._portrait = ''

    @property
    def nick_name(self) -> str:
        return self._nick_name

    @nick_name.setter
    def nick_name(self, new_nick_name: str) -> None:

        if self.user_name != new_nick_name:
            self._nick_name = new_nick_name
        else:
            self._nick_name = ''

    @property
    def show_name(self) -> str:
        return self.nick_name if self.nick_name else self.user_name

    @property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        else:
            return f"{self._nick_name} / {self._portrait}"


class UserInfo(BasicUserInfo):
    """
    用户属性

    Args:
        _id (Union[str, int, None]): 用于快速构造UserInfo的自适应参数 输入用户名或portrait或user_id
        proto (Optional[User_pb2.User])

    Fields:
        user_id (int): 贴吧旧版user_id
        user_name (str): 发帖用户名
        portrait (str): 用户头像portrait值
        nick_name (str): 发帖人昵称

        level (int): 等级
        gender (int): 性别 (1男2女0未知)
        is_vip (bool): 是否vip
        is_god (bool): 是否大神
        priv_like (int): 是否公开关注贴吧 (1完全可见2好友可见3完全隐藏)
        priv_reply (int): 帖子评论权限 (1所有人5我的粉丝6我的关注)
    """

    __slots__ = ['_level', '_gender', '_is_vip',
                 '_is_god', '_priv_like', '_priv_reply']

    def _init_by_data(self, user_proto: User_pb2.User) -> None:
        super()._init_by_data(user_proto)

        self._level = user_proto.level_id
        self._gender = user_proto.gender
        self.is_vip = True if user_proto.new_tshow_icon else user_proto.vipInfo.v_status
        self.is_god = user_proto.new_god_data.status
        priv_proto = user_proto.priv_sets
        self.priv_like = priv_proto.like
        self.priv_reply = priv_proto.reply

    def _init_null(self) -> None:
        super()._init_null()

        self._level = 0
        self._gender = 0
        self._is_vip = False
        self._is_god = False
        self._priv_like = 3
        self._priv_reply = 1

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    @_int_prop_check_ignore_none(0)
    def level(self, new_level: int) -> None:
        self._level = int(new_level)

    @property
    def gender(self) -> int:
        return self._gender

    @gender.setter
    @_int_prop_check_ignore_none(0)
    def gender(self, new_gender: Literal[0, 1, 2]) -> None:
        self._gender = int(new_gender)

    @property
    def is_vip(self) -> bool:
        return self._is_vip

    @is_vip.setter
    def is_vip(self, new_is_vip: bool) -> None:
        self._is_vip = bool(new_is_vip)

    @property
    def is_god(self) -> bool:
        return self._is_god

    @is_god.setter
    def is_god(self, new_is_god: bool) -> None:
        self._is_god = bool(new_is_god)

    @property
    def priv_like(self) -> int:
        return self._priv_like

    @priv_like.setter
    @_int_prop_check_ignore_none(3)
    def priv_like(self, new_priv_like: Literal[1, 2, 3]) -> None:
        self._priv_like = int(new_priv_like)

    @property
    def priv_reply(self) -> int:
        return self._priv_reply

    @priv_reply.setter
    @_int_prop_check_ignore_none(1)
    def priv_reply(self, new_priv_reply: Literal[1, 5, 6]) -> None:
        self._priv_reply = int(new_priv_reply)


class _Fragment(object):
    """
    内容碎片基类
    """

    __slots__ = ['_raw_data']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> None:
        self._raw_data = content_proto

    def __bool__(self) -> bool:
        return bool(self._raw_data)


_TFrag = TypeVar('_TFrag', bound=_Fragment)


class FragText(_Fragment):
    """
    纯文本碎片

    Methods:
        text (str): 文本内容
    """

    __slots__ = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [text:{self.text}]"

    @property
    def text(self) -> str:
        return self._raw_data.text


class FragEmoji(_Fragment):
    """
    表情碎片

    Fields:
        desc (str): 表情描述
    """

    __slots__ = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [desc:{self.desc}]"

    @property
    def desc(self):
        return self._raw_data.c


class FragImage(_Fragment):
    """
    图像碎片

    Fields:
        src (str): 压缩图像cdn_url
        big_src (str): 大图cdn_url
        origin_src (str): 图像源url
    """

    __slots__ = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [src:{self.src}]"

    @property
    def src(self):
        return self._raw_data.cdn_src

    @property
    def big_src(self) -> str:
        return self._raw_data.big_cdn_src

    @property
    def origin_src(self) -> str:
        return self._raw_data.origin_src


class FragAt(_Fragment):
    """
    @碎片

    Fields:
        text (str): 被@用户的昵称
        user_id (int): 被@用户的user_id
    """

    __slots__ = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [text:{self.text} / user_id:{self.user_id}]"

    @property
    def text(self) -> str:
        return self._raw_data.text

    @property
    def user_id(self) -> int:
        return self._raw_data.uid


class FragLink(_Fragment):
    """
    链接碎片

    Fields:
        text (str): 链接标题+链接url
        title (str): 链接标题
        link (str): 链接url
    """

    __slots__ = ['_text']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> None:
        super().__init__(content_proto)
        self._text = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [text:{self.text} / link:{self.link}]"

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = f"{self._raw_data.text} {self._raw_data.link}"
        return self._text

    @property
    def title(self) -> int:
        return self._raw_data.text

    @property
    def link(self) -> int:
        return self._raw_data.link


class FragVoice(_Fragment):
    """
    音频碎片

    Fields:
        voice_md5 (str): 声音md5
    """

    __slots__ = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [voice_md5:{self.voice_md5}]"

    @property
    def voice_md5(self) -> str:
        return self._raw_data.voice_md5


class FragTiebaPlus(_Fragment):
    """
    贴吧+碎片

    Fields:
        text (str): 描述
        jump_url (str): 跳转链接
    """

    __slots__ = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [desc:{self.desc} / url:{self.url}]"

    @property
    def text(self) -> str:
        return self._raw_data.desc

    @property
    def url(self) -> str:
        return self._raw_data.jump_url


class FragItem(_Fragment):
    """
    item碎片

    Fields:
        text (str): item名称
        item_name (str): item名称
    """

    __slots__ = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [item_name:{self.item_name}]"

    @property
    def text(self) -> str:
        return self._raw_data.item.item_name

    @property
    def item_name(self) -> str:
        return self._raw_data.item.item_name


class Fragments(Generic[_TFrag]):
    """
    内容碎片列表

    Fields:
        _frags (list[_Fragment]): 所有碎片的混合列表

        text (str): 文本内容

        texts (list[FragText]): 纯文本碎片列表
        emojis (list[FragEmoji]): 表情碎片列表
        imgs (list[FragImage]): 图像碎片列表
        ats (list[FragAt]): @碎片列表
        links (list[FragLink]): 链接碎片列表
        voice (FragVoice): 音频碎片
        tiebapluses (list[FragTiebaPlus]): 贴吧+碎片列表
    """

    __slots__ = ['_frags', '_text', '_texts', '_emojis',
                 '_imgs', '_ats', '_links', '_voice', '_tiebapluses']

    def __init__(self, content_protos: Optional[Iterable] = None) -> None:

        def _init_by_type(content_proto) -> _TFrag:
            _type = content_proto.type
            # 0纯文本 9电话号 18话题 27百科词条
            if _type in [0, 9, 18, 27]:
                fragment = FragText(content_proto)
                self._texts.append(fragment)
            elif _type == 2:
                fragment = FragEmoji(content_proto)
                self._emojis.append(fragment)
            elif _type == 3:
                fragment = FragImage(content_proto)
                self._imgs.append(fragment)
            elif _type == 4:
                fragment = FragAt(content_proto)
                self._ats.append(fragment)
                self._texts.append(fragment)
            elif _type == 1:
                fragment = FragLink(content_proto)
                self._links.append(fragment)
                self._texts.append(fragment)
            elif _type == 5:  # video
                fragment = _Fragment(content_proto)
            elif _type == 10:
                fragment = FragVoice(content_proto)
                self._voice = fragment
            elif _type == 20:  # e.g. tid=5470214675
                fragment = FragImage(content_proto)
                self._imgs.append(fragment)
            elif _type in [35, 36]:  # e.g. tid=7769728331
                fragment = FragTiebaPlus(content_proto)
                self._tiebapluses.append(fragment)
                self._texts.append(fragment)
            elif _type == 37:  # e.g. tid=7760184147
                fragment = FragTiebaPlus(content_proto)
                self._tiebapluses.append(fragment)
                self._texts.append(fragment)
            elif _type == 11:  # e.g. tid=5047676428
                fragment = FragEmoji(content_proto)
                self._emojis.append(fragment)
            else:
                fragment = _Fragment(content_proto)
                log.warning(f"Unknown fragment type:{_type}")

            return fragment

        self._text = None
        self._texts = []
        self._links = []
        self._imgs = []
        self._emojis = []
        self._ats = []
        self._voice = None
        self._tiebapluses = []

        if content_protos:
            self._frags = [_init_by_type(content_proto)
                           for content_proto in content_protos]
        else:
            self._frags = []

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = ''.join([frag.text for frag in self.texts])
        return self._text

    @property
    def texts(self) -> list[_TFrag]:
        return self._texts

    @property
    def emojis(self) -> list[FragEmoji]:
        return self._emojis

    @property
    def imgs(self) -> list[FragImage]:
        return self._imgs

    @property
    def ats(self) -> list[FragAt]:
        return self._ats

    @property
    def voice(self) -> FragVoice:
        if self._voice is None:
            self._voice = FragVoice()
        return self._voice

    @property
    def links(self) -> list[FragLink]:
        return self._links

    @property
    def tiebapluses(self) -> list[FragTiebaPlus]:
        return self._tiebapluses

    @final
    def __iter__(self) -> Iterable[_TFrag]:
        return iter(self._frags)

    @final
    def __getitem__(self, idx: int) -> _TFrag:
        return self._frags[idx]

    @final
    def __setitem__(self, idx, val) -> None:
        raise NotImplementedError

    @final
    def __delitem__(self, idx) -> None:
        raise NotImplementedError

    @final
    def __len__(self) -> int:
        return len(self._frags)

    @final
    def __bool__(self) -> bool:
        return bool(self._frags)


class Forum(object):
    """
    吧信息

    Fields:
        fid (int): 吧id
        name (str): 吧名
    """

    __slots__ = ['_raw_data', 'fid', 'name']

    def __init__(self, forum_proto: Union[SimpleForum_pb2.SimpleForum, FrsPageResIdl_pb2.FrsPageResIdl.DataRes.ForumInfo, None] = None) -> None:

        if forum_proto:
            self._init_by_data(forum_proto)

        else:
            self._init_null()

    def _init_by_data(self, forum_proto: Union[SimpleForum_pb2.SimpleForum, FrsPageResIdl_pb2.FrsPageResIdl.DataRes.ForumInfo]) -> None:

        self._raw_data = forum_proto

        self.fid = forum_proto.id
        self.name = forum_proto.name

    def _init_null(self) -> None:

        self._raw_data = None

        self.fid = 0
        self.name = ''

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [fid:{self.fid} / name:{self.name}]"


class Page(object):
    """
    页信息

    Fields:
        page_size (int): 页大小
        current_page (int): 当前页码
        total_page (int): 总页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = ['_raw_data', 'page_size', 'current_page',
                 'total_page', 'total_count', 'has_more', 'has_prev']

    def __init__(self, page_proto: Optional[Page_pb2.Page] = None) -> None:

        if page_proto:
            self._init_by_data(page_proto)

        else:
            self._init_null()

    def _init_by_data(self, page_proto: Page_pb2.Page):

        self._raw_data = page_proto

        self.page_size = page_proto.page_size
        self.current_page = page_proto.current_page
        self.total_page = page_proto.total_page

        if self.current_page and self.total_page:
            self.has_more = self.current_page < self.total_page
            self.has_prev = self.current_page > self.total_page
        else:
            self.has_more = bool(page_proto.has_more)
            self.has_prev = bool(page_proto.has_prev)

        self.total_count = page_proto.total_count

    def _init_null(self):

        self._raw_data = None

        self.page_size = 0
        self.current_page = 0
        self.total_page = 0

        self.has_more = False
        self.has_prev = False

        self.total_count = 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [current_page:{self.current_page} / total_page:{self.total_page} / has_more:{self.has_more} / has_prev:{self.has_prev}]"


class _Container(object):
    """
    基本的内容信息

    Fields:
        text (str): 文本内容

        fid (int): 所在吧id
        tid (int): 主题帖tid
        pid (int): 回复pid
        user (UserInfo): 发布者信息
        author_id (int): int 发布者user_id
    """

    __slots__ = ['_raw_data', '_text', '_tid', '_pid', '_user', '_author_id']

    def __init__(self) -> None:
        self._init_null()

    def _init_null(self) -> None:
        self._raw_data = None

        self._tid = 0
        self._pid = 0
        self._user = None
        self._author_id = None

        self._text = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [tid:{self.tid} / pid:{self.pid} / user:{self.user.log_name} / text:{self.text}]"

    @property
    def text(self) -> str:
        raise NotImplementedError

    @property
    def tid(self) -> int:
        return self._tid

    @tid.setter
    @_int_prop_check_ignore_none(0)
    def tid(self, new_tid: int) -> None:
        self._tid = int(new_tid)

    @property
    def pid(self) -> int:
        return self._pid

    @pid.setter
    @_int_prop_check_ignore_none(0)
    def pid(self, new_pid: int) -> None:
        self._pid = int(new_pid)

    @property
    def user(self) -> UserInfo:

        if self._user is None:

            if self._raw_data:
                self._user = UserInfo(user_proto=user_proto) if (
                    user_proto := self._raw_data.author).id else UserInfo()

            else:
                self._user = UserInfo()

        return self._user

    @user.setter
    def user(self, new_user: UserInfo) -> None:
        self._user = new_user

    @property
    def author_id(self) -> int:

        if self._author_id is None:

            if self._raw_data:
                self._author_id = author_id if (
                    author_id := self.user.user_id) else self._raw_data.author_id

            else:
                self._author_id = 0

        return self._author_id

    @author_id.setter
    @_int_prop_check_ignore_none(0)
    def author_id(self, new_author_id: int) -> None:
        self._author_id = int(new_author_id)


_TContainer = TypeVar('_TContainer', bound=_Container)


class _Containers(Generic[_TContainer]):
    """
    Threads/Posts/Comments/Ats的泛型基类
    约定取内容的通用接口

    Fields:
        _objs (list[TContainer]): 内容列表
        page (Page): 页码信息
        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = ['_objs', '_page']

    def __init__(self) -> None:
        raise NotImplementedError

    @property
    def objs(self) -> list[_TContainer]:
        raise NotImplementedError

    def __getitem__(self, idx: int) -> _TContainer:
        return self.objs[idx]

    @final
    def __setitem__(self, idx, val):
        raise NotImplementedError

    @final
    def __delitem__(self, idx):
        raise NotImplementedError

    @final
    def __len__(self) -> int:
        return len(self.objs)

    @final
    def __bool__(self) -> bool:
        return bool(self.objs)

    @property
    def page(self) -> Page:

        if self._page is None:

            if self._raw_data:
                self._page = Page(self._raw_data.page)

            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        return self.page.has_more

    @property
    def has_prev(self) -> bool:
        return self.page.has_prev


class Thread(_Container):
    """
    主题帖信息

    Fields:
        text (str): 文本内容
        contents (Fragments): 内容碎片列表

        fid (int): 所在吧id
        tid (int): 主题帖tid
        pid (int): 首楼的回复pid
        user (UserInfo): 发布者信息
        author_id (int): int 发布者user_id

        tab_id (int): 分区编号
        is_good (bool): 是否精品帖
        is_top (bool): 是否置顶帖
        is_share (bool): 是否分享帖
        is_hide (bool): 是否被屏蔽
        is_livepost (bool): 是否为置顶话题

        title (str): 标题内容
        vote_info (VoteInfo): 投票内容
        share_origin (Union[Thread, None]): 转发来的原帖内容
        view_num (int): 浏览量
        reply_num (int): 回复数
        share_num (int): 分享数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 10位时间戳 创建时间
        last_time (int): 10位时间戳 最后回复时间
    """

    __slots__ = ['_raw_data', '_contents', '_fid', '_tab_id', '_is_good', '_is_top', '_is_share', '_is_hide', '_is_livepost', 'title',
                 '_vote_info', '_share_origin', '_view_num', '_reply_num', '_share_num', '_agree', '_disagree', '_create_time', '_last_time']

    class VoteInfo(object):

        __slots__ = ['title', 'options',
                     'is_multi', 'total_vote', 'total_user']

        class VoteOption(object):

            __slots__ = ['vote_num', 'text', 'image']

            def __init__(self, option_proto: Optional[ThreadInfo_pb2.PollInfo.PollOption] = None) -> None:

                if option_proto:
                    self.vote_num = option_proto.num
                    self.text = option_proto.text
                    self.image = option_proto.image

                else:
                    self.vote_num = 0
                    self.text = ''
                    self.image = ''

        def __init__(self, vote_proto: Optional[ThreadInfo_pb2.PollInfo] = None) -> None:

            if vote_proto:
                self.title = vote_proto.title
                self.options = [self.VoteOption(
                    option_proto) for option_proto in vote_proto.options]
                self.is_multi = bool(vote_proto.is_multi)
                self.total_vote = vote_proto.total_poll
                self.total_user = vote_proto.total_num

            else:
                self.title = ''
                self.options = []
                self.is_multi = False
                self.total_vote = 0
                self.total_user = 0

    def __init__(self, thread_proto: Optional[ThreadInfo_pb2.ThreadInfo] = None) -> None:

        if thread_proto:
            self._init_by_data(thread_proto)

        else:
            self._init_null()

    def _init_by_data(self, thread_proto: ThreadInfo_pb2.ThreadInfo) -> None:

        self._raw_data = thread_proto
        self._text = None

        self._contents = None

        self._fid = thread_proto.fid
        self._tid = thread_proto.id
        self._pid = thread_proto.first_post_id
        self._user = None
        self._author_id = None

        self._tab_id = thread_proto.tab_id
        self.is_good = thread_proto.is_good
        self.is_top = thread_proto.is_top
        self.is_share = thread_proto.is_share_thread
        self.is_hide = thread_proto.is_frs_mask
        self.is_livepost = thread_proto.is_livepost

        self.title = thread_proto.title
        self._vote_info = None
        self._share_origin = None
        self._view_num = thread_proto.view_num
        self._reply_num = thread_proto.reply_num
        self._share_num = thread_proto.share_num
        self._agree = thread_proto.agree.agree_num
        self._disagree = thread_proto.agree.disagree_num
        self._create_time = thread_proto.create_time
        self._last_time = thread_proto.last_time_int

    def _init_null(self) -> None:

        self._raw_data = None
        self._text = None

        self._contents = None

        self._fid = 0
        self._tid = 0
        self._pid = 0
        self._user = None
        self._author_id = 0

        self._tab_id = 0
        self._is_good = False
        self._is_top = False
        self._is_share = False
        self._is_hide = False
        self._is_livepost = False

        self.title = ''
        self._vote_info = None
        self._share_origin = None
        self._view_num = 0
        self._reply_num = 0
        self._share_num = 0
        self._agree = 0
        self._disagree = 0
        self._create_time = 0
        self._last_time = 0

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = f"{self.title}\n{self.contents.text}"
        return self._text

    @property
    def contents(self) -> Fragments:

        if self._contents is None:

            if self._raw_data:
                self._contents = Fragments(self._raw_data.first_post_content)

            else:
                self._contents = Fragments()

        return self._contents

    @property
    def fid(self) -> int:
        return self._fid

    @fid.setter
    @_int_prop_check_ignore_none(0)
    def fid(self, new_fid: int) -> None:
        self._fid = int(new_fid)

    @property
    def is_good(self) -> bool:
        return self._is_good

    @is_good.setter
    def is_good(self, new_is_good: bool) -> None:
        self._is_good = bool(new_is_good)

    @property
    def is_top(self) -> bool:
        return self._is_top

    @is_top.setter
    def is_top(self, new_is_top: bool) -> None:
        self._is_top = bool(new_is_top)

    @property
    def is_share(self) -> bool:
        return self._is_share

    @is_share.setter
    def is_share(self, new_is_share: bool) -> None:
        self._is_share = bool(new_is_share)

    @property
    def is_hide(self) -> bool:
        return self._is_hide

    @is_hide.setter
    def is_hide(self, new_is_hide: bool) -> None:
        self._is_hide = bool(new_is_hide)

    @property
    def is_livepost(self) -> bool:
        return self._is_livepost

    @is_livepost.setter
    def is_livepost(self, new_is_livepost: bool) -> None:
        self._is_livepost = bool(new_is_livepost)

    @property
    def tab_id(self) -> int:
        return self._tab_id

    @tab_id.setter
    @_int_prop_check_ignore_none(0)
    def tab_id(self, new_tab_id: int) -> None:
        self._tab_id = int(new_tab_id)

    @property
    def vote_info(self) -> "Thread.VoteInfo":

        if self._vote_info is None:

            if self._raw_data:
                self._vote_info = self.VoteInfo(poll_info_proto) if (
                    poll_info_proto := self._raw_data.poll_info).options else self.VoteInfo()

            else:
                self._vote_info = self.VoteInfo()

        return self._vote_info

    @property
    def share_origin(self) -> "Thread":

        if self._share_origin is None:

            self._share_origin = Thread()
            if self._raw_data:
                if self._raw_data.is_share_thread:

                    share_proto = self._raw_data.origin_thread_info

                    self._share_origin.fid = share_proto.fid
                    self._share_origin.tid = share_proto.tid
                    self._share_origin.pid = share_proto.pid

                    self._share_origin._contents = Fragments(
                        share_proto.content)
                    self._share_origin.title = share_proto.title
                    self._share_origin._vote_info = self.VoteInfo(poll_info_proto) if (
                        poll_info_proto := share_proto.poll_info).options else self.VoteInfo()

        return self._share_origin

    @property
    def view_num(self) -> int:
        return self._view_num

    @view_num.setter
    @_int_prop_check_ignore_none(0)
    def view_num(self, new_view_num: int) -> None:
        self._view_num = int(new_view_num)

    @property
    def reply_num(self) -> int:
        return self._reply_num

    @reply_num.setter
    @_int_prop_check_ignore_none(0)
    def reply_num(self, new_reply_num: int) -> None:
        self._reply_num = int(new_reply_num)

    @property
    def share_num(self) -> int:
        return self._share_num

    @share_num.setter
    @_int_prop_check_ignore_none(0)
    def share_num(self, new_share_num: int) -> None:
        self._share_num = int(new_share_num)

    @property
    def agree(self) -> int:
        return self._agree

    @agree.setter
    @_int_prop_check_ignore_none(0)
    def agree(self, new_agree: int) -> None:
        self._agree = int(new_agree)

    @property
    def disagree(self) -> int:
        return self._disagree

    @disagree.setter
    @_int_prop_check_ignore_none(0)
    def disagree(self, new_disagree: int) -> None:
        self._disagree = int(new_disagree)

    @property
    def create_time(self) -> int:
        return self._create_time

    @create_time.setter
    @_int_prop_check_ignore_none(0)
    def create_time(self, new_create_time: int) -> None:
        self._create_time = int(new_create_time)

    @property
    def last_time(self) -> int:
        return self._last_time

    @last_time.setter
    @_int_prop_check_ignore_none(0)
    def last_time(self, new_last_time: int) -> None:
        self._last_time = int(new_last_time)


class Threads(_Containers[Thread]):
    """
    Thread列表

    Fields:
        _objs (list[Thread])
        page (Page): 页码信息
        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页

        forum (Forum): 所在吧信息
        tab_map (dict[str, int]): {分区名:分区id}
    """

    __slots__ = ['_raw_data', '_users', '_forum', '_tab_map']

    def __init__(self, threads_proto: Optional[FrsPageResIdl_pb2.FrsPageResIdl] = None) -> None:

        if threads_proto:
            self._init_by_data(threads_proto.data)

        else:
            self._init_null()

    def _init_by_data(self, data_proto: FrsPageResIdl_pb2.FrsPageResIdl.DataRes) -> None:

        self._raw_data = data_proto

        self._objs = None
        self._page = None
        self._forum = None
        self._tab_map = None

    def _init_null(self) -> None:

        self._raw_data = None

        self._objs = None
        self._page = None
        self._forum = None
        self._tab_map = None

    def __getitem__(self, idx: int) -> Thread:

        thread = self.objs[idx]

        if thread._user is None:
            thread._user = self._users.get(thread.author_id, None)

        return thread

    @property
    def objs(self) -> list[Thread]:

        if self._objs is None:
            if self._raw_data:

                self._users = {user.user_id: user for user_proto in self._raw_data.user_list if (
                    user := UserInfo(user_proto=user_proto)).user_id}
                self._objs = [Thread(thread_proto)
                              for thread_proto in self._raw_data.thread_list]
            else:
                self._users = {}
                self._objs = []

        return self._objs

    @property
    def forum(self) -> Forum:

        if self._forum is None:

            if self._raw_data:
                self._forum = Forum(self._raw_data.forum)

            else:
                self._forum = Forum()

        return self._forum

    @property
    def tab_map(self) -> Forum:

        if self._tab_map is None:

            if self._raw_data:
                self._tab_map = {
                    tab_proto.tab_name: tab_proto.tab_id for tab_proto in self._raw_data.nav_tab_info.tab}
            else:
                self._tab_map = {}

        return self._tab_map


class Post(_Container):
    """
    楼层信息

    Fields:
        text (str): 文本内容
        contents (Fragments): 内容碎片列表
        sign (Fragments): 小尾巴
        comments (list[Comment]): 高赞楼中楼

        fid (int): 所在吧id
        tid (int): 所在主题帖tid
        pid (int): 回复pid
        user (UserInfo): 发布者信息
        author_id (int): int 发布者user_id

        floor (int): 楼层数
        reply_num (int): 楼中楼数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 10位时间戳，创建时间
        is_thread_author (bool): 是否楼主
    """

    __slots__ = ['_fid', '_contents', '_sign', '_comments', '_floor', '_reply_num',
                 '_agree', '_disagree', '_create_time', 'is_thread_author']

    def __init__(self, post_proto: Optional[Post_pb2.Post] = None) -> None:

        if post_proto:
            self._init_by_data(post_proto)

        else:
            self._init_null()

    def _init_by_data(self, post_proto: Post_pb2.Post) -> None:

        self._raw_data = post_proto
        self._text = None

        self._contents = None
        self._sign = None
        self._comments = None

        self._fid = 0
        self._tid = 0
        self._pid = post_proto.id
        self._user = None
        self._author_id = None

        self._floor = post_proto.floor
        self._reply_num = post_proto.sub_post_number
        self._agree = post_proto.agree.agree_num
        self._disagree = post_proto.agree.disagree_num
        self._create_time = post_proto.time
        self.is_thread_author = False

    def _init_null(self) -> None:

        self._raw_data = None
        self._text = None

        self._contents = None
        self._sign = None
        self._comments = None

        self._fid = 0
        self._tid = 0
        self._pid = 0
        self._user = None
        self._author_id = 0

        self._floor = 0
        self._reply_num = 0
        self._agree = 0
        self._disagree = 0
        self._create_time = 0
        self.is_thread_author = False

    @property
    def text(self) -> str:
        if self._text is None:

            if self.sign:
                self._text = f'{self.contents.text}\n{self.sign}'

            else:
                self._text = self.contents.text

        return self._text

    @property
    def contents(self) -> Fragments:
        if self._contents is None:

            if self._raw_data:
                self._contents = Fragments(self._raw_data.content)

            else:
                self._contents = Fragments()

        return self._contents

    @property
    def sign(self) -> Fragments:
        if self._sign is None:

            if self._raw_data:
                self._sign = ''.join(
                    [sign.text for sign in self._raw_data.signature.content if sign.type == 0])
            else:
                self._sign = ''

        return self._sign

    @property
    def comments(self) -> Fragments:
        if self._comments is None:

            if self._raw_data:
                self._comments = [Comment(
                    comment_proto) for comment_proto in self._raw_data.sub_post_list.sub_post_list]
            else:
                self._comments = []

        return self._comments

    @property
    def fid(self) -> int:
        return self._fid

    @fid.setter
    @_int_prop_check_ignore_none(0)
    def fid(self, new_fid: int) -> None:
        self._fid = int(new_fid)

    @property
    def floor(self) -> int:
        return self._floor

    @floor.setter
    @_int_prop_check_ignore_none(0)
    def floor(self, new_floor: int) -> None:
        self._floor = int(new_floor)

    @property
    def reply_num(self) -> int:
        return self._reply_num

    @reply_num.setter
    @_int_prop_check_ignore_none(0)
    def reply_num(self, new_reply_num: int) -> None:
        self._reply_num = int(new_reply_num)

    @property
    def agree(self) -> int:
        return self._agree

    @agree.setter
    @_int_prop_check_ignore_none(0)
    def agree(self, new_agree: int) -> None:
        self._agree = int(new_agree)

    @property
    def disagree(self) -> int:
        return self._disagree

    @disagree.setter
    @_int_prop_check_ignore_none(0)
    def disagree(self, new_disagree: int) -> None:
        self._disagree = int(new_disagree)

    @property
    def create_time(self) -> int:
        return self._create_time

    @create_time.setter
    @_int_prop_check_ignore_none(0)
    def create_time(self, new_create_time: int) -> None:
        self._create_time = int(new_create_time)


class Posts(_Containers[Post]):
    """
    Post列表

    Fields:
        _objs (list[Post])
        page (Page): 页码信息
        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页

        forum (Forum): 所在吧信息
        thread (Thread): 所在主题帖信息
    """

    __slots__ = ['_raw_data', '_users', '_forum', '_thread']

    def __init__(self, posts_proto: Optional[PbPageResIdl_pb2.PbPageResIdl] = None) -> None:

        if posts_proto:
            self._init_by_data(posts_proto.data)

        else:
            self._init_null()

    def _init_by_data(self, data_proto: PbPageResIdl_pb2.PbPageResIdl.DataRes) -> None:
        self._raw_data = data_proto

        self._objs = None
        self._page = None
        self._forum = None
        self._thread = None

    def _init_null(self) -> None:
        self._raw_data = None

        self._objs = None
        self._page = None
        self._forum = None
        self._thread = None

    def __getitem__(self, idx: int) -> Post:

        post = self.objs[idx]

        if post._user is None:
            post._fid = self.forum.fid
            post._tid = self.thread.tid
            post._user = self._users.get(post.author_id, None)
            post.is_thread_author = self.thread.author_id == post.author_id

            for comment in post.comments:
                comment._fid = post.fid
                comment._tid = post.tid
                comment._user = self._users.get(comment.author_id, None)

        return post

    @property
    def objs(self) -> list[Post]:

        if self._objs is None:

            if self._raw_data:
                self._users = {user.user_id: user for user_proto in self._raw_data.user_list if (
                    user := UserInfo(user_proto=user_proto)).user_id}
                self._objs = [Post(post_proto)
                              for post_proto in self._raw_data.post_list]
            else:
                self._users = {}
                self._objs = []

        return self._objs

    @property
    def forum(self) -> Forum:
        if self._forum is None:

            if self._raw_data:
                self._forum = Forum(self._raw_data.forum)

            else:
                self._forum = Forum()

        return self._forum

    @property
    def thread(self) -> Thread:
        if self._thread is None:

            if self._raw_data:
                self._thread = Thread(self._raw_data.thread)
                self._thread._fid = self.forum.fid

            else:
                self._thread = Thread()

        return self._thread


class Comment(_Container):
    """
    楼中楼信息
    Fields:
        text (str): 文本内容
        contents (Fragments): 内容碎片列表

        fid (int): 所在吧id
        tid (int): 所在主题帖tid
        pid (int): 回复pid
        user (UserInfo): 发布者信息
        author_id (int): int 发布者user_id

        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 10位时间戳，创建时间
    """

    __slots__ = ['_fid', '_contents', '_agree', '_disagree', '_create_time']

    def __init__(self, comment_proto: Optional[SubPostList_pb2.SubPostList] = None) -> None:

        if comment_proto:
            self._init_by_data(comment_proto)

        else:
            self._init_null()

    def _init_by_data(self, comment_proto: SubPostList_pb2.SubPostList) -> None:

        self._raw_data = comment_proto
        self._text = None

        self._contents = None

        self._fid = 0
        self._tid = 0
        self._pid = comment_proto.id
        self._user = None
        self._author_id = None

        self._agree = comment_proto.agree.agree_num
        self._disagree = comment_proto.agree.disagree_num
        self._create_time = comment_proto.time

    def _init_null(self) -> None:

        self._raw_data = None
        self._text = None

        self._contents = None

        self._fid = 0
        self._tid = 0
        self._pid = 0
        self._user = None
        self._author_id = 0

        self._agree = 0
        self._disagree = 0
        self._create_time = 0

    @property
    def text(self) -> str:
        if not self._text:
            self._text = self.contents.text
        return self._text

    @property
    def contents(self) -> Fragments:
        if self._contents is None:

            if self._raw_data:
                self._contents = Fragments(self._raw_data.content)

            else:
                self._contents = Fragments()

        return self._contents

    @property
    def fid(self) -> int:
        return self._fid

    @fid.setter
    @_int_prop_check_ignore_none(0)
    def fid(self, new_fid: int) -> None:
        self._fid = int(new_fid)

    @property
    def create_time(self) -> int:
        return self._create_time

    @create_time.setter
    @_int_prop_check_ignore_none(0)
    def create_time(self, new_create_time: int) -> None:
        self._create_time = int(new_create_time)


class Comments(_Containers[Comment]):
    """
    Comment列表

    Fields:
        _objs (list[Comment])
        page (Page): 页码信息
        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页

        forum (Forum): 所在吧信息
        thread (Thread): 所在主题帖信息
        post (Post): 所在回复信息
    """

    __slots__ = ['_raw_data', '_forum', '_thread', '_post']

    def __init__(self, comments_proto: Optional[PbFloorResIdl_pb2.PbFloorResIdl] = None) -> None:

        if comments_proto:
            self._init_by_data(comments_proto.data)

        else:
            self._init_null()

    def _init_by_data(self, data_proto: PbFloorResIdl_pb2.PbFloorResIdl.DataRes) -> None:

        self._raw_data = data_proto

        self._objs = None
        self._page = None
        self._forum = None
        self._thread = None
        self._post = None

    def _init_null(self) -> None:

        self._raw_data = None

        self._objs = None
        self._page = None
        self._forum = None
        self._thread = None
        self._post = None

    def __getitem__(self, idx: int) -> Comment:

        comment = self.objs[idx]

        if comment._fid == 0:
            comment._fid = self.forum.fid
            comment._tid = self.thread.tid

        return comment

    @property
    def objs(self) -> list[Comment]:

        if self._objs is None:

            if self._raw_data:
                self._objs = [Comment(comment_proto)
                              for comment_proto in self._raw_data.subpost_list]
            else:
                self._objs = []

        return self._objs

    @property
    def forum(self) -> Forum:
        if self._forum is None:

            if self._raw_data:
                self._forum = Forum(self._raw_data.forum)

            else:
                self._forum = Forum()

        return self._forum

    @property
    def thread(self) -> Thread:
        if self._thread is None:

            if self._raw_data:
                self._thread = Thread(self._raw_data.thread)
                self._thread._fid = self.forum.fid

            else:
                self._thread = Thread()

        return self._thread

    @property
    def post(self) -> Post:
        if self._post is None:

            if self._raw_data:
                self._post = Post(self._raw_data.post)
                self._post._fid = self.forum.fid
                self._post._tid = self.thread.tid

            else:
                self._post = Post()

        return self._post


class Reply(_Container):
    """
    回复信息
    Fields:
        text (str): 文本内容

        tieba_name (str): 所在贴吧名
        tid (int): 所在主题帖tid
        pid (int): 回复pid
        user (UserInfo): 发布者信息
        author_id (int): int 发布者user_id
        post_pid (int): 楼层pid
        post_user (BasicUserInfo): 楼层用户信息
        thread_user (BasicUserInfo): 楼主用户信息

        is_floor (bool): 是否楼中楼
        create_time (int): 10位时间戳，创建时间
    """

    __slots__ = ['tieba_name', '_post_pid', '_post_user',
                 '_thread_user', '_is_floor', '_create_time']

    def __init__(self, reply_proto: Optional[ReplyMeResIdl_pb2.ReplyMeResIdl.DataRes.ReplyList] = None) -> None:

        if reply_proto:
            self._init_by_data(reply_proto)

        else:
            self._init_null()

    def _init_by_data(self, reply_proto: ReplyMeResIdl_pb2.ReplyMeResIdl.DataRes.ReplyList) -> None:

        self._raw_data = reply_proto
        self._text = reply_proto.content

        self._tid = reply_proto.thread_id
        self._pid = reply_proto.post_id
        self._user = None
        self._author_id = None
        self._post_pid = reply_proto.quote_pid
        self._post_user = None
        self._thread_user = None

        self.is_floor = reply_proto.is_floor
        self._create_time = reply_proto.time

    def _init_null(self) -> None:

        self._raw_data = None
        self._text = ''

        self.tieba_name = ''
        self._tid = 0
        self._pid = 0
        self._user = None
        self._post_pid = 0
        self._post_user = None
        self._thread_user = None

        self._is_floor = False
        self._create_time = 0

    @property
    def text(self) -> str:
        return self._text

    @property
    def user(self) -> UserInfo:
        if self._user is None:

            if self._raw_data:
                self._user = UserInfo(user_proto=user_proto) if (
                    user_proto := self._raw_data.replyer).id else UserInfo()
            else:
                self._user = UserInfo()

        return self._user

    @property
    def post_pid(self) -> int:
        return self._post_pid

    @post_pid.setter
    @_int_prop_check_ignore_none(0)
    def post_pid(self, new_post_pid: int) -> None:
        self._post_pid = int(new_post_pid)

    @property
    def post_user(self) -> BasicUserInfo:
        if self._post_user is None:

            if self._raw_data:
                self._post_user = BasicUserInfo(user_proto=user_proto) if (
                    user_proto := self._raw_data.quote_user).id else BasicUserInfo()
            else:
                self._post_user = BasicUserInfo()

        return self._post_user

    @property
    def thread_user(self) -> BasicUserInfo:
        if self._thread_user is None:

            if self._raw_data:
                self._thread_user = BasicUserInfo(user_proto=user_proto) if (
                    user_proto := self._raw_data.thread_author_user).id else BasicUserInfo()
            else:
                self._thread_user = BasicUserInfo()

        return self._thread_user

    @property
    def is_floor(self) -> bool:
        return self._is_floor

    @is_floor.setter
    def is_floor(self, new_is_floor: bool) -> None:
        self._is_floor = bool(new_is_floor)

    @property
    def create_time(self) -> int:
        return self._create_time

    @create_time.setter
    @_int_prop_check_ignore_none(0)
    def create_time(self, new_create_time: int) -> None:
        self._create_time = int(new_create_time)


class Replys(_Containers[Reply]):
    """
    Reply列表

    Fields:
        _objs (list[Comment])
        page (Page): 页码信息
        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = ['_raw_data']

    def __init__(self, replys_proto: Optional[ReplyMeResIdl_pb2.ReplyMeResIdl] = None) -> None:

        if replys_proto:
            self._init_by_data(replys_proto.data)

        else:
            self._init_null()

    def _init_by_data(self, data_proto: ReplyMeResIdl_pb2.ReplyMeResIdl.DataRes) -> None:

        self._raw_data = data_proto

        self._objs = None
        self._page = None

    def _init_null(self) -> None:

        self._raw_data = None

        self._objs = None
        self._page = None

    def __getitem__(self, idx: int) -> Reply:
        return self.objs[idx]

    @property
    def objs(self) -> list[Reply]:

        if self._objs is None:

            if self._raw_data:
                self._objs = [Reply(reply_proto)
                              for reply_proto in self._raw_data.reply_list]
            else:
                self._objs = []

        return self._objs


class At(_Container):
    """
    @信息

    Fields:
        text (str): 文本内容

        tieba_name (str): 所在贴吧名
        tid (int): 所在主题帖tid
        pid (int): 回复pid
        user (UserInfo): 发布者信息
        author_id (int): 发布者user_id

        is_floor (bool): 是否楼中楼
        is_thread (bool): 是否主题帖

        create_time (int): 10位时间戳，创建时间
    """

    __slots__ = ['tieba_name', '_is_floor', '_is_thread', '_create_time']

    def __init__(self, at_dict: Optional[dict]) -> None:

        if at_dict:
            self._init_by_data(at_dict)

        else:
            self._init_null()

    def _init_by_data(self, at_dict: dict) -> None:
        try:
            self._raw_data = at_dict
            self._text = at_dict['content']

            self.tieba_name = at_dict['fname']
            self.tid = at_dict['thread_id']
            self.pid = at_dict['post_id']
            self._user = None
            self._author_id = None

            self.is_floor = int(at_dict['is_floor'])
            self.is_thread = int(at_dict['is_first_post'])
            self.create_time = at_dict['time']

        except Exception as err:
            log.warning(
                f"Failed to init At. reason:line {err.__traceback__.tb_lineno}: {err}")
            self._init_null()

    def _init_null(self) -> None:

        self._raw_data = None
        self._text = ''

        self.tieba_name = ''
        self._tid = 0
        self._pid = 0
        self._user = None
        self._author_id = 0

        self._is_floor = False
        self._is_thread = False
        self._create_time = 0

    @property
    def text(self) -> str:
        return self._text

    @property
    def user(self) -> UserInfo:
        if self._user is None:

            if self._raw_data:
                user_proto = ParseDict(
                    self._raw_data['replyer'], User_pb2.User(), ignore_unknown_fields=True)
                self._user = UserInfo(
                    user_proto=user_proto) if user_proto.id else UserInfo()
            else:
                self._user = UserInfo()

        return self._user

    @property
    def author_id(self) -> int:
        if self._author_id is None:
            self._author_id = self.user.user_id
        return self._author_id

    @property
    def is_floor(self) -> bool:
        return self._is_floor

    @is_floor.setter
    def is_floor(self, new_is_floor: bool) -> None:
        self._is_floor = bool(new_is_floor)

    @property
    def is_thread(self) -> bool:
        return self._is_thread

    @is_thread.setter
    def is_thread(self, new_is_thread: bool) -> None:
        self._is_thread = bool(new_is_thread)

    @property
    def create_time(self) -> int:
        return self._create_time

    @create_time.setter
    @_int_prop_check_ignore_none(0)
    def create_time(self, new_create_time: int) -> None:
        self._create_time = int(new_create_time)


class Ats(_Containers[At]):
    """
    At列表

    Fields:
        _objs (list[At])
        page (Page): 页码信息
        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = ['_raw_data']

    def __init__(self, ats_dict: Optional[dict] = None) -> None:

        if ats_dict:
            self._init_by_data(ats_dict)

        else:
            self._init_null()

    def _init_by_data(self, data_dict: dict) -> None:

        self._raw_data = data_dict

        self._objs = None
        self._page = None

    def _init_null(self) -> None:

        self._raw_data = None

        self._objs = None
        self._page = None

    def __getitem__(self, idx: int) -> At:
        return self.objs[idx]

    @property
    def objs(self) -> list[At]:

        if self._objs is None:

            if self._raw_data:
                self._objs = [At(at_dict=at_dict)
                              for at_dict in self._raw_data['at_list']]
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        if self._page is None:

            if self._raw_data:
                page_dict = self._raw_data['page']
                if not page_dict['has_more']:
                    page_dict['has_more'] = 0

                try:
                    page_proto = ParseDict(
                        page_dict, Page_pb2.Page(), ignore_unknown_fields=True)
                    self._page = Page(page_proto)

                except Exception as err:
                    log.warning(
                        f"Failed to init Page of Ats. reason:line {err.__traceback__.tb_lineno}: {err}")
                    self._page = Page()

            else:
                self._page = Page()

        return self._page


class Search(_Container):
    """
    搜索结果

    Fields:
        text (str): 文本内容
        title (str): 标题

        tieba_name (str): 所在贴吧名
        tid (int): 所在主题帖tid
        pid (int): 回复pid

        is_floor (bool): 是否楼中楼

        create_time (int): 10位时间戳，创建时间
    """

    __slots__ = ['tieba_name', 'title', '_is_floor', '_create_time']

    def __init__(self, search_dict: Optional[dict]) -> None:

        if search_dict:
            self._init_by_data(search_dict)

        else:
            self._init_null()

    def _init_by_data(self, search_dict: dict) -> None:
        try:
            self._raw_data = search_dict
            self._text = search_dict['content']
            self.title = search_dict['title']

            self.tieba_name = search_dict['fname']
            self.tid = search_dict['tid']
            self.pid = search_dict['pid']
            self._user = None
            self._author_id = None

            self.is_floor = int(search_dict['is_floor'])
            self.create_time = search_dict['time']

        except Exception as err:
            log.warning(
                f"Failed to init Search. reason:line {err.__traceback__.tb_lineno}: {err}")
            self._init_null()

    def _init_null(self) -> None:

        self._raw_data = None
        self._text = ''
        self.title = ''

        self.tieba_name = ''
        self._tid = 0
        self._pid = 0
        self._user = None
        self._author_id = 0

        self._is_floor = False
        self._create_time = 0

    @property
    def text(self) -> str:
        return self._text

    @property
    def user(self) -> UserInfo:
        if self._user is None:

            if self._raw_data:
                user_proto = ParseDict(
                    self._raw_data['author'], User_pb2.User(), ignore_unknown_fields=True)
                self._user = UserInfo(
                    user_proto=user_proto) if user_proto.id else UserInfo()
            else:
                self._user = UserInfo()

        return self._user

    @property
    def author_id(self) -> int:
        if self._author_id is None:
            self._author_id = self.user.user_id
        return self._author_id

    @property
    def is_floor(self) -> bool:
        return self._is_floor

    @is_floor.setter
    def is_floor(self, new_is_floor: bool) -> None:
        self._is_floor = bool(new_is_floor)

    @property
    def create_time(self) -> int:
        return self._create_time

    @create_time.setter
    @_int_prop_check_ignore_none(0)
    def create_time(self, new_create_time: int) -> None:
        self._create_time = int(new_create_time)


class Searches(_Containers[Search]):
    """
    搜索结果列表

    Fields:
        _objs (list[At])
        page (Page): 页码信息
        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = ['_raw_data']

    def __init__(self, searches_dict: Optional[dict] = None) -> None:

        if searches_dict:
            self._init_by_data(searches_dict)

        else:
            self._init_null()

    def _init_by_data(self, data_dict: dict) -> None:

        self._raw_data = data_dict

        self._objs = None
        self._page = None

    def _init_null(self) -> None:

        self._raw_data = None

        self._objs = None
        self._page = None

    def __getitem__(self, idx: int) -> Search:
        return self.objs[idx]

    @property
    def objs(self) -> list[Search]:

        if self._objs is None:

            if self._raw_data:
                self._objs = [Search(search_dict=search_dict)
                              for search_dict in self._raw_data['post_list']]
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        if self._page is None:

            if self._raw_data:
                page_dict = self._raw_data['page']
                if not page_dict['has_more']:
                    page_dict['has_more'] = 0

                try:
                    page_proto = ParseDict(
                        page_dict, Page_pb2.Page(), ignore_unknown_fields=True)
                    self._page = Page(page_proto)

                except Exception as err:
                    log.warning(
                        f"Failed to init Page of Searches. reason:line {err.__traceback__.tb_lineno}: {err}")
                    self._page = Page()

            else:
                self._page = Page()

        return self._page
