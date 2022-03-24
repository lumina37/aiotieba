# -*- coding:utf-8 -*-
__all__ = ['BasicUserInfo', 'UserInfo',
           'Thread', 'Post', 'Comment', 'At',
           'Threads', 'Posts', 'Comments', 'Ats',
           'Fragments'
           ]

import re
from typing import (Any, Callable, Generic, Iterable, Iterator, Literal,
                    NoReturn, Optional, TypeVar, Union, final)

from google.protobuf.json_format import ParseDict

from .logger import log
from .tieba_proto import *

TContent = TypeVar('TContent')
TContainer = TypeVar('TContainer')


def _int_prop_check_ignore_none(default_val: int):
    """
    装饰器实现对int类型属性的赋值前检查。忽略传入None的异常

    参数:
        default_val: 传入None时采用的默认值
    """

    def wrapper(func) -> Callable[[Any, Any], NoReturn]:
        def foo(self: Any, new_val: Any) -> NoReturn:
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
    BasicUserInfo()
    基本用户属性

    参数:
        _id: 用于快速构造UserInfo的自适应参数 输入用户名或portrait或user_id
        user_proto: User_pb2.User

    字段:
        user_name: 发帖用户名
        nick_name: 发帖人昵称
        portrait: 用户头像portrait值
        user_id: 贴吧旧版uid
    """

    __slots__ = ['user_name', '_nick_name', '_portrait', '_user_id']

    def __init__(self, _id: Union[str, int, None] = None, user_proto: Optional[User_pb2.User] = None) -> NoReturn:
        self.user_name = ''
        self._nick_name = ''
        self._portrait = ''
        self._user_id = 0

        if _id:
            if type(_id) == int:
                self.user_id = _id
            else:
                self.portrait = _id
                if not self.portrait:
                    self.user_name = _id

        elif user_proto:
            self.user_name = user_proto.name
            self.nick_name = user_proto.name_show
            self.portrait = user_proto.portrait
            self.user_id = user_proto.id

    def __str__(self) -> str:
        return f"user_name:{self.user_name} / nick_name:{self._nick_name} / portrait:{self._portrait} / user_id:{self._user_id}"

    def __hash__(self) -> int:
        return self._user_id.__hash__()

    def __int__(self) -> int:
        return self._user_id

    @property
    def nick_name(self) -> str:
        return self._nick_name

    @nick_name.setter
    def nick_name(self, new_nick_name: str) -> NoReturn:
        if self.user_name != new_nick_name:
            self._nick_name = new_nick_name
        else:
            self._nick_name = ''

    @property
    def portrait(self) -> str:
        return self._portrait

    @portrait.setter
    def portrait(self, new_portrait: str) -> NoReturn:
        if new_portrait and new_portrait.startswith('tb.'):
            try:
                self._portrait = re.match('[\w\-_.]+', new_portrait).group(0)
            except Exception:
                self._portrait = ''
        else:
            self._portrait = ''

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    @_int_prop_check_ignore_none(0)
    def user_id(self, new_user_id: int) -> NoReturn:
        self._user_id = int(new_user_id)

    @property
    def show_name(self) -> str:
        return self.nick_name if self.nick_name else self.user_name

    @property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        else:
            return f'{self.nick_name}/{self.portrait}'


class UserInfo(BasicUserInfo):
    """
    UserInfo()
    用户属性

    参数:
        _id: Union[str, int, None] 用于快速构造UserInfo的自适应参数 输入用户名或portrait或user_id
        proto: Optional[User_pb2.User]

    字段:
        user_name: 发帖用户名
        nick_name: 发帖人昵称
        portrait: 用户头像portrait值
        user_id: 贴吧旧版uid
        level: 等级
        gender: 性别（1男2女0未知）
        is_vip: 是否vip
        is_god: 是否大神
        priv_like: 是否公开关注贴吧（1完全可见2好友可见3完全隐藏）
        priv_reply: 帖子评论权限（1所有人5我的粉丝6我的关注）
    """

    __slots__ = ['_level', '_gender', 'is_vip',
                 'is_god', '_priv_like', '_priv_reply']

    def __init__(self, _id: Union[str, int, None] = None, user_proto: Optional[User_pb2.User] = None) -> NoReturn:
        super().__init__(_id, user_proto)

        if user_proto:
            priv_proto = user_proto.priv_sets
            self.level = user_proto.level_id
            self.gender = user_proto.gender
            self.is_vip = bool(user_proto.vipInfo.v_status)
            self.is_god = bool(user_proto.new_god_data.status)
            self.priv_like = priv_proto.like
            self.priv_reply = priv_proto.reply

        else:
            self.level = 0
            self.gender = 0
            self.is_vip = False
            self.is_god = False
            self.priv_like = 3
            self.priv_reply = 1

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    @_int_prop_check_ignore_none(0)
    def level(self, new_level: int) -> NoReturn:
        self._level = int(new_level)

    @property
    def gender(self) -> int:
        return self._gender

    @gender.setter
    @_int_prop_check_ignore_none(0)
    def gender(self, new_gender: Literal[0, 1, 2]) -> NoReturn:
        self._gender = int(new_gender)

    @property
    def priv_like(self) -> int:
        return self._priv_like

    @priv_like.setter
    @_int_prop_check_ignore_none(3)
    def priv_like(self, new_priv_like: Literal[1, 2, 3]) -> NoReturn:
        self._priv_like = int(new_priv_like)

    @property
    def priv_reply(self) -> int:
        return self._priv_reply

    @priv_reply.setter
    @_int_prop_check_ignore_none(1)
    def priv_reply(self, new_priv_reply: Literal[1, 5, 6]) -> NoReturn:
        self._priv_reply = int(new_priv_reply)


class Forum(object):
    """
    吧信息

    fid: 吧id
    name: 吧名
    """

    __slots__ = ['fid', 'name']

    def __init__(self, forum_proto) -> NoReturn:
        self.fid = forum_proto.id
        self.name = forum_proto.name


class _Fragment(Generic[TContent]):
    """
    内容碎片基类

    _str: 文本内容
    """

    __slots__ = ['_str']

    def __init__(self, content_proto: Optional[PbContent_pb2.PbContent] = None) -> NoReturn:
        self._str = ''

    def __str__(self) -> str:
        return self._str

    def __bool__(self) -> bool:
        return bool(self._str)


class FragText(_Fragment):
    """
    纯文本碎片

    _str: 文本内容
    """

    __slots__ = []

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        self._str = content_proto.text


class FragLink(_Fragment):
    """
    链接碎片

    _str: 链接标题
    link: 链接url
    """

    __slots__ = ['title', 'link']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        self._str = content_proto.text
        self.link = content_proto.link


class FragEmoji(_Fragment):
    """
    表情碎片
    """

    __slots__ = []

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        self._str = content_proto.c


class FragImage(_Fragment):
    """
    音频碎片

    src: 图像源url
    cdn_src: cdn压缩图像url
    big_cdn_src: cdn大图url
    """

    __slots__ = ['src', 'cdn_src', 'big_cdn_src']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        self._str = ''
        self.src = content_proto.src
        self.cdn_src = content_proto.cdn_src
        self.big_cdn_src = content_proto.big_cdn_src


class FragAt(_Fragment):
    """
    @碎片

    user_id: 被@用户的user_id
    """

    __slots__ = ['user_id']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        self._str = content_proto.text
        self.user_id = content_proto.uid


class FragVoice(_Fragment):
    """
    音频碎片

    voice_md5: 声音md5
    """

    __slots__ = ['voice_md5']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        self._str = content_proto.voice_md5
        self.voice_md5 = content_proto.voice_md5


class FragTiebaPlus(_Fragment):
    """
    贴吧+碎片

    _str: 描述文本
    jump_url: 跳转链接
    """

    __slots__ = ['jump_url']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        tiebaplus_proto = content_proto.tiebaplus_info
        self._str = tiebaplus_proto.desc
        self.jump_url = tiebaplus_proto.jump_url


class FragItem(_Fragment):
    """
    item碎片

    _str: item名称
    """

    __slots__ = []

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        item_proto = content_proto.item
        self._str = item_proto.item_name


class Fragments(object):
    """
    内容碎片列表

    texts: 纯文本碎片列表
    imgs: 图像碎片列表
    emojis: 表情碎片列表
    ats: @碎片列表
    voice: 音频碎片
    tiebapluses: 贴吧+碎片列表
    """

    __slots__ = ['_frags', '_text', 'texts', 'imgs',
                 'emojis', 'ats', 'voice', 'tiebapluses']

    def __init__(self, content_protos: Optional[Iterable] = None) -> NoReturn:

        def _init_by_type(content_proto) -> _Fragment:
            _type = content_proto.type
            # 0纯文本 9电话号 18话题 27百科词条
            if _type in [0, 9, 18, 27]:
                fragment = FragText(content_proto)
                self.texts.append(fragment)
            elif _type == 2:
                fragment = FragEmoji(content_proto)
                self.emojis.append(fragment)
            elif _type == 3:
                fragment = FragImage(content_proto)
                self.imgs.append(fragment)
            elif _type == 4:
                fragment = FragAt(content_proto)
                self.texts.append(fragment)
                self.ats.append(fragment)
            elif _type == 1:
                fragment = FragLink(content_proto)
                self.texts.append(fragment)
            elif _type == 5:
                fragment = _Fragment()
            elif _type == 10:
                fragment = FragVoice(content_proto)
                self.voice = fragment
            elif _type == 20:  # e.g. tid=5470214675
                fragment = FragImage(content_proto)
                self.imgs.append(fragment)
            elif _type in [35, 36]:  # e.g. tid=7769728331
                fragment = FragTiebaPlus(content_proto)
                self.texts.append(fragment)
                self.tiebapluses.append(fragment)
            elif _type == 37:  # e.g. tid=7760184147
                fragment = FragTiebaPlus(content_proto)
                self.texts.append(fragment)
                self.tiebapluses.append(fragment)
            elif _type == 11:  # e.g. tid=5047676428
                fragment = FragEmoji(content_proto)
                self.emojis.append(fragment)
            else:
                fragment = _Fragment()
                log.warning(f"Unknown fragment type:{_type}")

            return fragment

        self._text = ''
        self.texts = []
        self.imgs = []
        self.emojis = []
        self.ats = []
        self.voice = None
        self.tiebapluses = []

        if content_protos:
            self._frags = [_init_by_type(content_proto)
                           for content_proto in content_protos]
        else:
            self._frags = []

    @property
    def text(self) -> str:
        if not self._text:
            self._text = ''.join([str(text) for text in self.texts])
        return self._text

    @final
    def __iter__(self) -> Iterator[TContent]:
        return iter(self._frags)

    @final
    def __getitem__(self, idx: int) -> TContent:
        return self._frags[idx]

    @final
    def __setitem__(self, idx, val):
        raise NotImplementedError

    @final
    def __delitem__(self, idx):
        raise NotImplementedError

    @final
    def __len__(self) -> int:
        return len(self._frags)

    @final
    def __bool__(self) -> bool:
        return bool(self._frags)


class _Container(object):
    """
    基本的内容信息

    text: 文本内容
    contents: 内容碎片列表

    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo 发布者信息
    author_id: int 发布者user_id
    """

    __slots__ = ['_text', 'contents', 'fid', 'tid', 'pid', 'user', 'author_id']

    def __init__(self) -> NoReturn:
        self._text = ''

    @property
    def text(self) -> str:
        return self.contents.text


class _Containers(Generic[TContainer]):
    """
    Threads/Posts/Comments/Ats的泛型基类
    约定取内容的通用接口

    current_pn: 当前页数
    total_pn: 总页数

    has_next: 是否有下一页
    """

    __slots__ = ['current_pn', 'total_pn', '_objs']

    def __init__(self) -> NoReturn:
        pass

    @final
    def __iter__(self) -> Iterator[TContainer]:
        return iter(self._objs)

    @final
    def __getitem__(self, idx: int) -> TContainer:
        return self._objs[idx]

    @final
    def __setitem__(self, idx, val):
        raise NotImplementedError

    @final
    def __delitem__(self, idx):
        raise NotImplementedError

    @final
    def __len__(self) -> int:
        return len(self._objs)

    @final
    def __bool__(self) -> bool:
        return bool(self._objs)

    @property
    def has_next(self) -> bool:
        return self.current_pn < self.total_pn


class Thread(_Container):
    """
    主题帖信息

    text: 文本内容
    contents: 内容碎片列表

    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo 发布者信息
    author_id: int 发布者user_id

    tab_id: 分区编号
    title: 标题内容
    vote_info: 投票内容
    share_origin: 转发来的原帖内容
    view_num: 浏览量
    reply_num: 回复数
    agree: 点赞数
    disagree: 点踩数
    create_time: 10位时间戳 创建时间
    last_time: 10位时间戳 最后回复时间
    """

    __slots__ = ['tab_id', 'title', 'view_num', 'reply_num',
                 'agree', 'disagree', 'create_time', 'last_time', 'vote_info', 'share_origin']

    class VoteInfo(object):

        __slots__ = ['title', 'options',
                     'is_multi', 'total_vote', 'total_user']

        class VoteOption(object):

            __slots__ = ['vote_num', 'text', 'image']

            def __init__(self, option_proto: Optional[ThreadInfo_pb2.PollInfo.PollOption] = None) -> NoReturn:

                if option_proto:
                    self.vote_num = option_proto.num
                    self.text = option_proto.text
                    self.image = option_proto.image

                else:
                    self.vote_num = 0
                    self.text = ''
                    self.image = ''

        def __init__(self, vote_proto: Optional[ThreadInfo_pb2.PollInfo] = None) -> NoReturn:

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

    def __init__(self, thread_proto: Optional[ThreadInfo_pb2.ThreadInfo] = None) -> NoReturn:
        super().__init__()

        if thread_proto:
            self.contents = Fragments(thread_proto.first_post_content)

            self.fid = thread_proto.fid
            self.tid = thread_proto.id
            self.pid = thread_proto.first_post_id
            self.user = UserInfo(
                user_proto=thread_proto.author) if thread_proto.author.id else UserInfo()
            self.author_id = thread_proto.author_id

            self.tab_id = thread_proto.tab_id
            self.title = thread_proto.title
            self.vote_info = self.VoteInfo(thread_proto.poll_info)
            self.share_origin = None
            self.view_num = thread_proto.view_num
            self.reply_num = thread_proto.reply_num
            self.agree = thread_proto.agree.agree_num
            self.disagree = thread_proto.agree.disagree_num
            self.create_time = thread_proto.create_time
            self.last_time = thread_proto.last_time_int

        else:
            self.contents = Fragments()

            self.fid = 0
            self.tid = 0
            self.pid = 0
            self.user = UserInfo()
            self.author_id = 0

            self.tab_id = 0
            self.title = ''
            self.vote_info = self.VoteInfo()
            self.share_origin = None
            self.view_num = 0
            self.reply_num = 0
            self.agree = 0
            self.disagree = 0
            self.create_time = 0
            self.last_time = 0

    @property
    def text(self) -> str:
        if not self._text:
            self._text = f'{self.title}\n{self.contents.text}'
        return self._text


class Threads(_Containers[Thread]):
    """
    Thread列表

    current_pn: 当前页数
    total_pn: 总页数

    has_next: 是否有下一页
    """

    __slots__ = ['forum', 'tab_map']

    def __init__(self, threads_proto: Optional[FrsPageResIdl_pb2.FrsPageResIdl] = None) -> NoReturn:

        if threads_proto:

            def _init_thread(thread_proto):
                thread = Thread(thread_proto)
                if thread_proto.is_share_thread:
                    share_proto = thread_proto.origin_thread_info
                    share_origin = Thread()
                    share_origin.fid = share_proto.fid
                    share_origin.tid = int(share_proto.tid)
                    share_origin.pid = share_proto.pid
                    share_origin.contents = Fragments(share_proto.content)
                    share_origin.title = share_proto.title
                    share_origin.vote_info = Thread.VoteInfo(
                        share_proto.poll_info)
                    thread.share_origin = share_origin
                return thread

            data_proto = threads_proto.data
            self.current_pn = data_proto.page.current_page
            self.total_pn = data_proto.page.total_page
            self.forum = Forum(data_proto.forum)
            self.tab_map = {
                tab_proto.tab_name: tab_proto.tab_id for tab_proto in data_proto.nav_tab_info.tab}

            users = {user_proto.id: UserInfo(
                user_proto=user_proto) for user_proto in data_proto.user_list}
            self._objs = [_init_thread(thread_proto)
                          for thread_proto in data_proto.thread_list]
            for thread in self._objs:
                thread.user = users.get(thread.author_id, UserInfo())

        else:
            self._objs = []
            self.current_pn = 0
            self.total_pn = 0
            self.tab_map = {}


class Post(_Container):
    """
    楼层信息

    text: 文本内容
    contents: 内容碎片列表
    sign: 小尾巴
    comments: 高赞楼中楼

    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo 发布者信息
    author_id: int 发布者user_id

    floor: 楼层数
    reply_num: 楼中楼回复数
    agree: 点赞数
    disagree: 点踩数
    create_time: 10位时间戳，创建时间
    is_thread_owner: 是否楼主
    """

    __slots__ = ['sign', 'comments', 'floor', 'reply_num',
                 'agree', 'disagree', 'create_time', 'is_thread_owner']

    def __init__(self, post_proto: Optional[Post_pb2.Post] = None) -> NoReturn:
        super().__init__()

        if post_proto:
            self.contents = Fragments(post_proto.content)
            self.sign = ''.join(
                [sign.text for sign in post_proto.signature.content if sign.type == 0])
            self.comments = [Comment(comment_proto)
                             for comment_proto in post_proto.sub_post_list.sub_post_list]

            self.pid = post_proto.id
            self.author_id = post_proto.author_id

            self.floor = post_proto.floor
            self.reply_num = post_proto.sub_post_number
            self.agree = post_proto.agree.agree_num
            self.disagree = post_proto.agree.disagree_num
            self.create_time = post_proto.time

        else:
            self.contents = Fragments()
            self.sign = ''
            self.comments = []

            self.fid = 0
            self.tid = 0
            self.pid = 0
            self.user = UserInfo()
            self.floor = 0
            self.reply_num = 0
            self.agree = 0
            self.disagree = 0
            self.create_time = 0
            self.is_thread_owner = False

    @property
    def text(self) -> str:
        if not self._text:
            self._text = f'{self.contents.text}\n{self.sign}'
        return self._text


class Posts(_Containers[Post]):
    """
    Post列表

    current_pn: 当前页数
    total_pn: 总页数

    has_next: 是否有下一页
    """

    __slots__ = ['forum', 'thread']

    def __init__(self, posts_proto: Optional[PbPageResIdl_pb2.PbPageResIdl] = None) -> NoReturn:

        if posts_proto:
            data_proto = posts_proto.data
            self.current_pn = data_proto.page.current_page
            self.total_pn = data_proto.page.total_page
            self.forum = Forum(data_proto.forum)
            self.thread = Thread(data_proto.thread)
            thread_owner_id = self.thread.user

            users = {user_proto.id: UserInfo(
                user_proto=user_proto) for user_proto in data_proto.user_list}
            self._objs = [Post(post_proto)
                          for post_proto in data_proto.post_list]
            for comment in self._objs:
                comment.is_thread_owner = thread_owner_id == comment.author_id
                comment.fid = self.forum.fid
                comment.tid = self.thread.tid
                comment.user = users.get(comment.author_id, UserInfo())
                for comment in comment.comments:
                    comment.user = users.get(comment.author_id, UserInfo())

        else:
            self._objs = []
            self.current_pn = 0
            self.total_pn = 0


class Comment(_Container):
    """
    楼中楼信息

    text: 文本内容
    contents: 内容碎片列表

    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo 发布者信息
    author_id: int 发布者user_id

    agree: 点赞数
    disagree: 点踩数
    create_time: 10位时间戳，创建时间
    """

    __slots__ = ['agree', 'disagree', 'create_time']

    def __init__(self, comment_proto: Optional[SubPostList_pb2.SubPostList] = None) -> NoReturn:
        super().__init__()

        if comment_proto:
            self.contents = Fragments(comment_proto.content)

            self.pid = comment_proto.id
            self.user = UserInfo(user_proto=comment_proto.author)
            self.author_id = comment_proto.author_id

            self.agree = comment_proto.agree.agree_num
            self.disagree = comment_proto.agree.disagree_num
            self.create_time = comment_proto.time

        else:
            self.contents = Fragments()

            self.fid = 0
            self.tid = 0
            self.pid = 0
            self.user = UserInfo()

            self.agree = 0
            self.disagree = 0
            self.create_time = 0


class Comments(_Containers[Comment]):
    """
    Comment列表

    current_pn: 当前页数
    total_pn: 总页数
    has_next: 是否有下一页
    """

    __slots__ = ['forum', 'thread', 'post']

    def __init__(self, comments_proto: Optional[PbFloorResIdl_pb2.PbFloorResIdl] = None) -> NoReturn:

        if comments_proto:
            data_proto = comments_proto.data
            self.current_pn = data_proto.page.current_page
            self.total_pn = data_proto.page.total_page
            self.forum = Forum(data_proto.forum)
            self.thread = Thread(data_proto.thread)
            self.post = Post(data_proto.post)

            self._objs = [Comment(comment_proto)
                          for comment_proto in data_proto.subpost_list]
            for comment in self._objs:
                comment.fid = self.forum.fid
                comment.tid = self.thread.tid

        else:
            self._objs = []
            self.current_pn = 0
            self.total_pn = 0

    @property
    def has_next(self) -> bool:
        return self.current_pn < self.total_pn


class At(object):
    """
    @信息

    text: 文本

    tieba_name: 所在贴吧名
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo 发布者信息

    create_time: 10位时间戳，创建时间
    """

    __slots__ = ['tieba_name', 'tid', 'pid', 'user', 'text', 'create_time']

    def __init__(self, tieba_name: str = '', tid: int = 0, pid: int = 0, user: UserInfo = UserInfo(), text: str = '', create_time: int = 0) -> NoReturn:
        self.text = text

        self.tieba_name = tieba_name
        self.tid = tid
        self.pid = pid
        self.user = user

        self.create_time = create_time


class Ats(_Containers[At]):
    """
    At列表

    current_pn: 当前页数
    has_next: 是否有下一页
    """

    def __init__(self, ats_dict: Optional[dict] = None) -> NoReturn:

        def _init_obj(at_dict: dict) -> At:
            try:
                user_dict = at_dict['replyer']
                user_proto = ParseDict(
                    user_dict, User_pb2.User(), ignore_unknown_fields=True)
                user = UserInfo(user_proto=user_proto)

                at = At(tieba_name=at_dict['fname'],
                        tid=int(at_dict['thread_id']),
                        pid=int(at_dict['post_id']),
                        text=at_dict['content'].lstrip(),
                        user=user,
                        create_time=int(at_dict['time'])
                        )
                return at

            except Exception as err:
                log.warning(
                    f"Failed to init At. reason:line {err.__traceback__.tb_lineno} {err}")
                return At()

        if ats_dict:
            try:
                self.current_pn = int(ats_dict['page']['current_page'])
                if int(ats_dict['page']['has_more']) == 1:
                    self.total_pn = self.current_pn+1
                else:
                    self.total_pn = self.current_pn
            except Exception as err:
                raise ValueError(f"line {err.__traceback__.tb_lineno}: {err}")

            self._objs = [_init_obj(at_dict)
                          for at_dict in ats_dict['at_list']]

        else:
            self._objs = []
            self.current_pn = 0
            self.total_pn = 0
