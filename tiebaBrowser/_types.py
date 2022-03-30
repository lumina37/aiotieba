# -*- coding:utf-8 -*-
__all__ = ['BasicUserInfo', 'UserInfo',
           'Thread', 'Post', 'Comment', 'At', 'Reply',
           'Threads', 'Posts', 'Comments', 'Ats', 'Replys',
           'Fragments'
           ]

import re
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
        user_name (str): 发帖用户名
        nick_name (str): 发帖人昵称
        portrait (str): 用户头像portrait值
        user_id (int): 贴吧旧版uid
    """

    __slots__ = ['user_name', '_nick_name', '_portrait', '_user_id']

    def __init__(self, _id: Union[str, int, None] = None, user_proto: Optional[User_pb2.User] = None) -> None:
        self.user_name = ''
        self._nick_name = ''
        self._portrait = ''
        self._user_id = 0

        if _id:
            if isinstance(_id, int):
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

    def __repr__(self) -> str:
        return f"{{'user_name': '{self.user_name}', 'nick_name': '{self._nick_name}', 'portrait': '{self._portrait}', 'user_id': {self._user_id}}}"

    def __hash__(self) -> int:
        return self._user_id.__hash__()

    def __int__(self) -> int:
        return self._user_id

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
    def portrait(self) -> str:
        return self._portrait

    @portrait.setter
    def portrait(self, new_portrait: str) -> None:
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
    def user_id(self, new_user_id: int) -> None:
        self._user_id = int(new_user_id)

    @property
    def show_name(self) -> str:
        return self.nick_name if self.nick_name else self.user_name

    @property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        else:
            return f"{self.nick_name}/{self.portrait}"


class UserInfo(BasicUserInfo):
    """
    用户属性

    Args:
        _id (Union[str, int, None]): 用于快速构造UserInfo的自适应参数 输入用户名或portrait或user_id
        proto (Optional[User_pb2.User])

    Fields:
        user_name (str): 发帖用户名
        nick_name (str): 发帖人昵称
        portrait (str): 用户头像portrait值
        user_id (int): 贴吧旧版uid

        level (int): 等级
        gender (int): 性别 (1男2女0未知)
        is_vip (bool): 是否vip
        is_god (bool): 是否大神
        priv_like (int): 是否公开关注贴吧 (1完全可见2好友可见3完全隐藏)
        priv_reply (int): 帖子评论权限 (1所有人5我的粉丝6我的关注)
    """

    __slots__ = ['_level', '_gender', 'is_vip',
                 'is_god', '_priv_like', '_priv_reply']

    def __init__(self, _id: Union[str, int, None] = None, user_proto: Optional[User_pb2.User] = None) -> None:
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

    Fields:
        _str (str): 文本内容
    """

    __slots__ = ['_str']

    def __init__(self, content_proto: Optional[PbContent_pb2.PbContent] = None) -> None:
        self._str = ''

    def __str__(self) -> str:
        return self._str

    def __bool__(self) -> bool:
        return bool(self._str)


_TFrag = TypeVar('_TFrag', bound=_Fragment)


class FragText(_Fragment):
    """
    纯文本碎片

    Fields:
        _str (str): 文本内容
    """

    __slots__ = []

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> None:
        self._str = content_proto.text


class FragEmoji(_Fragment):
    """
    表情碎片

    Fields:
        _str (str): 表情注释
    """

    __slots__ = []

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> None:
        self._str = content_proto.c


class FragImage(_Fragment):
    """
    图像碎片

    Fields:
        src (str): 图像源url
        cdn_src (str): cdn压缩图像url
        big_cdn_src (str): cdn大图url
    """

    __slots__ = ['src', 'cdn_src', 'big_cdn_src']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> None:
        self._str = ''
        self.src = content_proto.src
        self.cdn_src = content_proto.cdn_src
        self.big_cdn_src = content_proto.big_cdn_src


class FragLink(_Fragment):
    """
    链接碎片

    Fields:
        _str (str): 链接标题
        link (str): 链接url
    """

    __slots__ = ['title', 'link']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> None:
        self._str = content_proto.text
        self.link = content_proto.link


class FragAt(_Fragment):
    """
    @碎片

    Fields:
        user_id (int): 被@用户的user_id
    """

    __slots__ = ['user_id']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> None:
        self._str = content_proto.text
        self.user_id = content_proto.uid


class FragVoice(_Fragment):
    """
    音频碎片

    Fields:
        voice_md5 (str): 声音md5
    """

    __slots__ = ['voice_md5']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> None:
        self._str = content_proto.voice_md5
        self.voice_md5 = content_proto.voice_md5


class FragTiebaPlus(_Fragment):
    """
    贴吧+碎片

    Fields:
        _str (str): 描述文本
        jump_url (str): 跳转链接
    """

    __slots__ = ['jump_url']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> None:
        tiebaplus_proto = content_proto.tiebaplus_info
        self._str = tiebaplus_proto.desc
        self.jump_url = tiebaplus_proto.jump_url


class FragItem(_Fragment):
    """
    item碎片

    Fields:
        _str (str): item名称
    """

    __slots__ = []

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> None:
        item_proto = content_proto.item
        self._str = item_proto.item_name


class Fragments(Generic[_TFrag]):
    """
    内容碎片列表

    Fields:
        _frags (list[_Fragment]): 所有碎片的混合列表

        texts (list[FragText]): 纯文本碎片列表
        links (list[FragLink]): 链接碎片列表
        emojis (list[FragEmoji]): 表情碎片列表
        imgs (list[FragImage]): 图像碎片列表
        ats (list[FragAt]): @碎片列表
        voice (FragVoice): 音频碎片
        tiebapluses (list[FragTiebaPlus]): 贴吧+碎片列表
    """

    __slots__ = ['_frags', '_text', 'texts', 'links', 'imgs',
                 'emojis', 'ats', 'voice', 'tiebapluses']

    def __init__(self, content_protos: Optional[Iterable] = None) -> None:

        def _init_by_type(content_proto) -> _TFrag:
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
                self.ats.append(fragment)
                self.texts.append(fragment)
            elif _type == 1:
                fragment = FragLink(content_proto)
                self.links.append(fragment)
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
        self.links = []
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

    __slots__ = ['fid', 'name']

    def __init__(self, forum_proto: Union[SimpleForum_pb2.SimpleForum, FrsPageResIdl_pb2.FrsPageResIdl.DataRes.ForumInfo, None] = None) -> None:
        if forum_proto:
            self.fid = forum_proto.id
            self.name = forum_proto.name

        else:
            self.fid = 0
            self.name = ''


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

    __slots__ = ['page_size', 'current_page', 'total_page',
                 'total_count', '_has_more', '_has_prev']

    def __init__(self, page_proto: Optional[Page_pb2.Page] = None) -> None:
        if page_proto:
            self.page_size = page_proto.page_size
            self.current_page = page_proto.current_page
            self.total_page = page_proto.total_page
            self._has_more = bool(page_proto.has_more)
            self._has_prev = bool(page_proto.has_prev)
            self.total_count = page_proto.total_count

        else:
            self.page_size = 0
            self.current_page = 0
            self.total_page = 0
            self._has_more = None
            self._has_prev = None
            self.total_count = 0

    @property
    def has_more(self):
        if self._has_more is None:
            return self.current_page < self.total_page
        else:
            return self._has_more

    @property
    def has_prev(self):
        if self._has_prev is None:
            return self.current_page > self.total_page
        else:
            return self._has_prev


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

    __slots__ = ['_text', 'fid', 'tid', 'pid', 'user', 'author_id']

    def __init__(self) -> None:
        self._text = ''

    @property
    def text(self) -> str:
        raise NotImplementedError


_TContainer = TypeVar('_TContainer')


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

    __slots__ = ['_objs', 'page']

    def __init__(self) -> None:
        pass

    @final
    def __iter__(self) -> Iterable[_TContainer]:
        return iter(self._objs)

    @final
    def __getitem__(self, idx: int) -> _TContainer:
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
        title (str): 标题内容
        vote_info (VoteInfo): 投票内容
        share_origin (Union[Thread, None]): 转发来的原帖内容
        view_num (int): 浏览量
        reply_num (int): 回复数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 10位时间戳 创建时间
        last_time (int): 10位时间戳 最后回复时间
    """

    __slots__ = ['contents', 'tab_id', 'title', 'view_num', 'reply_num',
                 'agree', 'disagree', 'create_time', 'last_time', 'vote_info', 'share_origin']

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

    Fields:
        _objs (list[Thread])
        page (Page): 页码信息
        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页

        forum (Forum): 所在吧信息
        tab_map (dict[str, int]): {分区名:分区id}
    """

    __slots__ = ['forum', 'tab_map']

    def __init__(self, threads_proto: Optional[FrsPageResIdl_pb2.FrsPageResIdl] = None) -> None:

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
            self.page = Page(data_proto.page)
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
            self.page = Page()
            self.forum = Forum()
            self.tab_map = {}


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

    __slots__ = ['contents', 'sign', 'comments', 'floor', 'reply_num',
                 'agree', 'disagree', 'create_time', 'is_thread_author']

    def __init__(self, post_proto: Optional[Post_pb2.Post] = None) -> None:
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
            self.is_thread_author = False

    @property
    def text(self) -> str:
        if not self._text:
            if self.sign:
                self._text = f'{self.contents.text}\n{self.sign}'
            else:
                self._text = self.contents.text
        return self._text


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

    __slots__ = ['forum', 'thread']

    def __init__(self, posts_proto: Optional[PbPageResIdl_pb2.PbPageResIdl] = None) -> None:

        if posts_proto:
            data_proto = posts_proto.data
            self.page = Page(data_proto.page)
            self.forum = Forum(data_proto.forum)
            self.thread = Thread(data_proto.thread)
            thread_author_id = self.thread.user.user_id

            users = {user_proto.id: UserInfo(
                user_proto=user_proto) for user_proto in data_proto.user_list}
            self._objs = [Post(post_proto)
                          for post_proto in data_proto.post_list]
            for post in self._objs:
                post.is_thread_author = thread_author_id == post.author_id
                post.fid = self.forum.fid
                post.tid = self.thread.tid
                post.user = users.get(post.author_id, UserInfo())
                for comment in post.comments:
                    comment.fid = post.fid
                    comment.tid = post.tid
                    comment.user = users.get(comment.author_id, UserInfo())

        else:
            self._objs = []
            self.page = Page()
            self.forum = Forum()
            self.thread = Thread()


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

    __slots__ = ['contents', 'agree', 'disagree', 'create_time']

    def __init__(self, comment_proto: Optional[SubPostList_pb2.SubPostList] = None) -> None:
        super().__init__()

        if comment_proto:
            self.contents = Fragments(comment_proto.content)

            self.fid = 0
            self.tid = 0
            self.pid = comment_proto.id
            self.user = UserInfo(user_proto=comment_proto.author)
            self.author_id = author_id if (
                author_id := comment_proto.author_id) else self.user.user_id

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

    @property
    def text(self) -> str:
        return self.contents.text


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

    __slots__ = ['forum', 'thread', 'post']

    def __init__(self, comments_proto: Optional[PbFloorResIdl_pb2.PbFloorResIdl] = None) -> None:

        if comments_proto:
            data_proto = comments_proto.data
            self.page = Page(data_proto.page)
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
            self.page = Page()
            self.forum = Forum()
            self.thread = Thread()
            self.post = Post()


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

    __slots__ = ['tieba_name', 'post_pid', 'post_user',
                 'thread_user', 'is_floor', 'create_time']

    def __init__(self, reply_proto: Optional[ReplyMeResIdl_pb2.ReplyMeResIdl.DataRes.ReplyList] = None) -> None:
        super().__init__()

        if reply_proto:
            self._text = reply_proto.content

            self.tieba_name = reply_proto.fname
            self.fid = 0
            self.tid = reply_proto.thread_id
            self.pid = reply_proto.post_id
            self.user = UserInfo(user_proto=reply_proto.replyer)
            self.author_id = self.user.user_id
            self.post_pid = reply_proto.quote_pid
            self.post_user = BasicUserInfo(user_proto=reply_proto.quote_user)
            self.thread_user = BasicUserInfo(
                user_proto=reply_proto.thread_author_user)

            self.is_floor = bool(reply_proto.is_floor)
            self.create_time = reply_proto.time

        else:
            self.text = ''

            self.tieba_name = ''
            self.fid = 0
            self.tid = 0
            self.pid = 0
            self.user = UserInfo()
            self.post_pid = 0
            self.post_user = BasicUserInfo()
            self.thread_user = BasicUserInfo()

            self.is_floor = False
            self.create_time = reply_proto.time

    @property
    def text(self) -> str:
        return self._text


class Replys(_Containers[Reply]):
    """
    Reply列表

    Fields:
        _objs (list[Comment])
        page (Page): 页码信息
        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = []

    def __init__(self, replys_proto: Optional[ReplyMeResIdl_pb2.ReplyMeResIdl] = None) -> None:

        if replys_proto:
            data_proto = replys_proto.data
            self.page = Page(data_proto.page)

            self._objs = [Reply(reply_proto)
                          for reply_proto in data_proto.reply_list]

        else:
            self._objs = []
            self.page = Page()


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

    __slots__ = ['tieba_name', 'is_floor', 'is_thread', 'create_time']

    def __init__(self, at_dict: Optional[dict]) -> None:
        super().__init__()

        if at_dict:
            try:
                self._text = at_dict['content'].lstrip()

                self.tieba_name = at_dict['fname']
                self.fid = 0
                self.tid = int(at_dict['thread_id'])
                self.pid = int(at_dict['post_id'])
                user_proto = ParseDict(
                    at_dict['replyer'], User_pb2.User(), ignore_unknown_fields=True)
                self.user = UserInfo(user_proto=user_proto)
                self.author_id = self.user.user_id

                self.is_floor = bool(int(at_dict['is_floor']))
                self.is_thread = bool(int(at_dict['is_first_post']))
                self.create_time = int(at_dict['time'])

            except Exception as err:
                raise ValueError(f"line {err.__traceback__.tb_lineno}: {err}")

        else:
            self._text = ''

            self.tieba_name = ''
            self.fid = 0
            self.tid = 0
            self.pid = 0
            self.user = UserInfo()
            self.author_id = 0

            self.is_floor = False
            self.is_thread = False
            self.create_time = 0

    @property
    def text(self) -> str:
        return self._text


class Ats(_Containers[At]):
    """
    At列表

    Fields:
        _objs (list[At])
        page (Page): 页码信息
        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    def __init__(self, ats_dict: Optional[dict] = None) -> None:

        if ats_dict:
            try:
                page_proto = ParseDict(
                    ats_dict['page'], Page_pb2.Page(), ignore_unknown_fields=True)
                self.page = Page(page_proto)

            except Exception as err:
                raise ValueError(f"line {err.__traceback__.tb_lineno}: {err}")

            self._objs = [At(at_dict=at_dict)
                          for at_dict in ats_dict['at_list']]

        else:
            self._objs = []
            self.page = Page()
