# -*- coding:utf-8 -*-
__all__ = ('BasicUserInfo', 'UserInfo',
           'Thread', 'Post', 'Comment', 'At',
           'Threads', 'Posts', 'Comments', 'Ats'
           )

import re
from typing import (Any, Callable, Generic, Iterator, Literal, NoReturn,
                    Optional, TypeVar, Union, final)

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
        priv_like: 是否公开关注贴吧（1完全可见2好友可见3完全隐藏）
        priv_reply: 帖子评论权限（1所有人5我的粉丝6我的关注）
    """

    __slots__ = ['_level', '_gender', '_priv_like', '_priv_reply']

    def __init__(self, _id: Union[str, int, None] = None, user_proto: Optional[User_pb2.User] = None) -> NoReturn:
        super().__init__(_id, user_proto)
        if user_proto:
            priv_proto = user_proto.priv_sets
            self.level = user_proto.level_id
            self.gender = user_proto.gender
            self.priv_like = priv_proto.like
            self.priv_reply = priv_proto.reply

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, new_level: int) -> NoReturn:
        self._level = new_level

    @property
    def gender(self) -> int:
        return self._gender

    @gender.setter
    def gender(self, new_gender: Literal[0, 1, 2]) -> NoReturn:
        self._gender = new_gender

    @property
    def priv_like(self) -> int:
        return self._priv_like

    @priv_like.setter
    def priv_like(self, new_priv_like: Literal[1, 2, 3]) -> NoReturn:
        self._priv_like = new_priv_like

    @property
    def priv_reply(self) -> int:
        return self._priv_reply

    @priv_reply.setter
    def priv_reply(self, new_priv_reply: Literal[1, 5, 6]) -> NoReturn:
        self._priv_reply = new_priv_reply


class Forum(object):
    """
    吧信息

    fid: 吧id
    name: 吧名
    """

    __slots__ = ['fid', 'name']

    def __init__(self, obj_proto) -> NoReturn:
        self.fid = obj_proto.id
        self.name = obj_proto.name


class _Fragment(Generic[TContent]):
    """
    基本的内容碎片信息

    _str: 文本内容
    """

    __slots__ = ['_str']

    def __init__(self) -> NoReturn:
        pass

    def __str__(self) -> str:
        return self._str


class FragText(_Fragment):
    """
    纯文本碎片
    """

    __slots__ = []

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        self._str = content_proto.text


class FragLink(_Fragment):
    """
    链接碎片

    title: 链接标题
    link: 链接url
    """

    __slots__ = ['title', 'link']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        self.title = content_proto.text
        self.link = content_proto.link
        self._str = f"{self.link} {self.title}"


class FragEmoji(_Fragment):
    """
    表情碎片

    emoji_id: 表情id
    """

    __slots__ = ['emoji_id']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        self._str = content_proto.text
        self.emoji_id = content_proto.text


class FragImage(_Fragment):
    """
    音频碎片

    src: 图像源url
    cdn_src: cdn压缩图像url
    big_cdn_src: cdn大图url
    """

    __slots__ = ['src', 'cdn_src', 'big_cdn_src']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        self._str = content_proto.src
        self.src = content_proto.src
        self.cdn_src = content_proto.cdn_src
        self.big_cdn_src = content_proto.big_cdn_src


class FragVoice(_Fragment):
    """
    音频碎片

    voice_md5: 声音md5
    """

    __slots__ = ['voice_md5']

    def __init__(self, content_proto: PbContent_pb2.PbContent) -> NoReturn:
        self._str = content_proto.voice_md5
        self.voice_md5 = content_proto.voice_md5


class Fragments(object):
    """
    碎片列表

    texts: 纯文本碎片列表
    imgs: 图像碎片列表
    emojis: 表情碎片列表
    """

    __slots__ = ['_frags', '_text', 'texts', 'imgs', 'emojis']

    def __init__(self, content_protos) -> NoReturn:

        def _init_by_type(content_proto) -> _Fragment:
            _type = content_proto.type
            fragment = _Fragment()
            if _type in [0, 4, 9, 18]:
                fragment = FragText(content_proto)
                self.texts.append(fragment)
            elif _type == 1:
                fragment = FragLink(content_proto)
                self.texts.append(fragment)
            elif _type == 2:
                fragment = FragEmoji(content_proto)
                self.emojis.append(fragment)
            elif _type == 3:
                fragment = FragImage(content_proto)
                self.imgs.append(fragment)
            elif _type == 10:
                fragment = FragVoice(content_proto)
            return fragment

        self._text = ''
        self.texts = []
        self.imgs = []
        self.emojis = []
        self._frags = [_init_by_type(content_proto)
                       for content_proto in content_protos]

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

    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo类 发布者信息
    text: 文本内容
    """

    __slots__ = ['_text', 'contents', 'fid', 'tid', 'pid', 'user']

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

    text: 所有文本
    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    tab_id: 分区编号
    user: UserInfo类 发布者信息
    title: 标题内容
    first_floor_text: 首楼文本
    imgs: 图片列表
    emojis: 表情列表
    view_num: 浏览量
    reply_num: 回复数
    like: 点赞数
    dislike: 点踩数
    create_time: 10位时间戳 创建时间
    last_time: 10位时间戳 最后回复时间
    """

    __slots__ = ['tab_id', 'title', 'view_num', 'reply_num',
                 'like', 'dislike', 'create_time', 'last_time']

    def __init__(self, obj_proto: ThreadInfo_pb2.ThreadInfo) -> NoReturn:
        super().__init__()
        self.contents = Fragments(obj_proto.first_post_content)
        self.fid = obj_proto.fid
        self.tid = obj_proto.id
        self.pid = obj_proto.first_post_id
        self.tab_id = obj_proto.tab_id
        self.user = obj_proto.author_id
        self.title = obj_proto.title
        self.view_num = obj_proto.view_num
        self.reply_num = obj_proto.reply_num
        self.like = obj_proto.agree.agree_num
        self.dislike = obj_proto.agree.disagree_num
        self.create_time = obj_proto.create_time
        self.last_time = obj_proto.last_time_int

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

    def __init__(self, main_proto: Optional[FrsPageResIdl_pb2.FrsPageResIdl] = None) -> NoReturn:

        if main_proto:
            data_proto = main_proto.data
            self.current_pn = data_proto.page.current_page
            self.total_pn = data_proto.page.total_page
            self.forum = Forum(data_proto.forum)
            self.tab_map = {
                tab_proto.tab_name: tab_proto.tab_id for tab_proto in data_proto.nav_tab_info.tab}

            users = {user_proto.id: UserInfo(
                user_proto=user_proto) for user_proto in data_proto.user_list}
            self._objs = [Thread(obj_proto)
                          for obj_proto in data_proto.thread_list]
            for obj in self._objs:
                obj.user = users.get(obj.user, UserInfo())

        else:
            self._objs = []
            self.current_pn = 0
            self.total_pn = 0
            self.tab_map = {}


class Post(_Container):
    """
    楼层信息

    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo类 发布者信息
    text: 所有文本
    content: 正文
    sign: 小尾巴
    imgs: 图片列表
    emojis: 表情列表
    has_audio: 是否含有音频
    floor: 楼层数
    reply_num: 楼中楼回复数
    like: 点赞数
    dislike: 点踩数
    create_time: 10位时间戳，创建时间
    is_thread_owner: 是否楼主
    """

    __slots__ = ['content', 'sign', 'has_audio', 'floor', 'reply_num',
                 'like', 'dislike', 'create_time', 'is_thread_owner']

    def __init__(self, obj_proto: Post_pb2.Post) -> NoReturn:
        super().__init__()
        self.contents = Fragments(obj_proto.content)
        self.has_audio = False
        self.pid = obj_proto.id
        self.user = obj_proto.author_id
        self.sign = ''.join(
            [sign.text for sign in obj_proto.signature.content if sign.type == 0])
        self.floor = obj_proto.floor
        self.reply_num = obj_proto.sub_post_number
        self.like = obj_proto.agree.agree_num
        self.dislike = obj_proto.agree.disagree_num
        self.create_time = obj_proto.time

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

    def __init__(self, main_proto: Optional[PbPageResIdl_pb2.PbPageResIdl] = None) -> NoReturn:

        if main_proto:
            data_proto = main_proto.data
            self.current_pn = data_proto.page.current_page
            self.total_pn = data_proto.page.total_page
            self.forum = Forum(data_proto.forum)
            self.thread = Thread(data_proto.thread)
            thread_owner_id = self.thread.user

            users = {user_proto.id: UserInfo(
                user_proto=user_proto) for user_proto in data_proto.user_list}
            self._objs = [Post(obj_proto)
                          for obj_proto in data_proto.post_list]
            for obj in self._objs:
                obj.is_thread_owner = thread_owner_id == obj.user
                obj.fid = self.forum.fid
                obj.tid = self.thread.tid
                obj.user = users.get(obj.user, UserInfo())

        else:
            self._objs = []
            self.current_pn = 0
            self.total_pn = 0


class Comment(_Container):
    """
    楼中楼信息

    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo类 发布者信息
    text: 文本
    emojis: 表情列表
    has_audio: 是否含有音频
    like: 点赞数
    dislike: 点踩数
    create_time: 10位时间戳，创建时间
    """

    __slots__ = ['has_audio', 'like', 'dislike', 'create_time']

    def __init__(self, obj_proto: SubPostList_pb2.SubPostList) -> NoReturn:
        super().__init__()
        self.contents = Fragments(obj_proto.content)
        self.pid = obj_proto.id
        self.user = UserInfo(user_proto=obj_proto.author)
        self.like = obj_proto.agree.agree_num
        self.dislike = obj_proto.agree.disagree_num
        self.create_time = obj_proto.time


class Comments(_Containers[Comment]):
    """
    Comment列表

    current_pn: 当前页数
    total_pn: 总页数
    has_next: 是否有下一页
    """

    __slots__ = ['forum', 'thread', 'post']

    def __init__(self, main_proto: Optional[PbFloorResIdl_pb2.PbFloorResIdl] = None) -> NoReturn:

        if main_proto:
            data_proto = main_proto.data
            self.current_pn = data_proto.page.current_page
            self.total_pn = data_proto.page.total_page
            self.forum = Forum(data_proto.forum)
            self.thread = Thread(data_proto.thread)
            self.post = Post(data_proto.post)

            self._objs = [Comment(obj_proto)
                          for obj_proto in data_proto.subpost_list]
            for obj in self._objs:
                obj.fid = self.forum.fid
                obj.tid = self.thread.tid

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

    tieba_name: 所在贴吧名
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo类 发布者信息
    text: 文本
    create_time: 10位时间戳，创建时间
    """

    __slots__ = ['tieba_name', 'tid', 'pid', 'user', 'text', 'create_time']

    def __init__(self, tieba_name: str = '', tid: int = 0, pid: int = 0, user: UserInfo = UserInfo(), text: str = '', create_time: int = 0) -> NoReturn:
        self.tieba_name = tieba_name
        self.tid = tid
        self.pid = pid
        self.user = user
        self.text = text
        self.create_time = create_time


class Ats(_Containers[At]):
    """
    At列表

    current_pn: 当前页数
    has_next: 是否有下一页
    """

    def __init__(self, main_json: Optional[dict] = None) -> NoReturn:

        def _init_obj(obj_dict: dict) -> At:
            try:
                user_dict = obj_dict['replyer']
                priv_sets = user_dict['priv_sets']
                if not priv_sets:
                    priv_sets = {}
                user = UserInfo()
                user.user_name = user_dict['name']
                user.nick_name = user_dict['name_show']
                user.portrait = user_dict['portrait']
                user.user_id = user_dict['id']
                user.priv_like = priv_sets.get('like', None)
                user.priv_reply = priv_sets.get('reply', None)
                at = At(tieba_name=obj_dict['fname'],
                        tid=int(obj_dict['thread_id']),
                        pid=int(obj_dict['post_id']),
                        text=obj_dict['content'].lstrip(),
                        user=user,
                        create_time=int(obj_dict['time'])
                        )
                return at

            except Exception as err:
                log.error(
                    f"Failed to init At. reason:line {err.__traceback__.tb_lineno} {err}")
                return At()

        if main_json:
            try:
                self.current_pn = int(main_json['page']['current_page'])
                if int(main_json['page']['has_more']) == 1:
                    self.total_pn = self.current_pn+1
                else:
                    self.total_pn = self.current_pn
            except Exception as err:
                raise ValueError(f"line {err.__traceback__.tb_lineno}: {err}")

            self._objs = [_init_obj(obj_dict)
                          for obj_dict in main_json['at_list']]

        else:
            self._objs = []
            self.current_pn = 0
            self.total_pn = 0
