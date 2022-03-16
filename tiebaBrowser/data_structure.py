# -*- coding:utf-8 -*-
__all__ = ('BasicUserInfo', 'UserInfo',
           'Thread', 'Post', 'Comment', 'At',
           'Threads', 'Posts', 'Comments', 'Ats'
           )

import re
from typing import (Any, Callable, Generic, Iterator, Literal, NoReturn,
                    Optional, TypeVar, Union, final)

from .logger import log


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

    _id: 用于快速构造UserInfo的自适应参数 输入用户名或portrait或user_id

    user_name: 发帖用户名
    nick_name: 发帖人昵称
    portrait: 用户头像portrait值
    user_id: 贴吧旧版uid
    """

    __slots__ = ['user_name', '_nick_name', '_portrait', '_user_id']

    def __init__(self, _id: Union[str, int, None] = None, user_name: str = '', nick_name: str = '', portrait: str = '', user_id: int = 0) -> NoReturn:
        if _id:
            if type(_id) == int:
                self.user_id = _id
                self.portrait = portrait
                self.user_name = user_name
            else:
                self.portrait = _id
                if not self.portrait:
                    self.user_name = _id
                else:
                    self.user_name = user_name
                self.user_id = user_id
        else:
            self.portrait = portrait
            self.user_name = user_name
            self.user_id = user_id

        self.nick_name = nick_name

    def __str__(self) -> str:
        return f"user_name:{self.user_name} / nick_name:{self._nick_name} / portrait:{self._portrait} / user_id:{self._user_id}"

    def __hash__(self) -> int:
        return self._user_id.__hash__()

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

    _id: 用于快速构造UserInfo的自适应参数 输入用户名或portrait或user_id

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

    def __init__(self, _id: Union[str, int, None] = None, user_name: str = '', nick_name: str = '', portrait: str = '', user_id: int = 0, level: int = 1, gender: int = 0, priv_like: int = 3, priv_reply: int = 1) -> NoReturn:
        super().__init__(_id, user_name, nick_name, portrait, user_id)
        self.level = level
        self.gender = gender
        self.priv_like = priv_like
        self.priv_reply = priv_reply

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    @_int_prop_check_ignore_none(0)
    def level(self, new_level: int) -> NoReturn:
        self._level = new_level

    @property
    def gender(self) -> int:
        return self._gender

    @gender.setter
    @_int_prop_check_ignore_none(0)
    def gender(self, new_gender: Literal[0, 1, 2]) -> NoReturn:
        self._gender = new_gender

    @property
    def priv_like(self) -> int:
        return self._priv_like

    @priv_like.setter
    @_int_prop_check_ignore_none(3)
    def priv_like(self, new_priv_like: Literal[1, 2, 3]) -> NoReturn:
        self._priv_like = new_priv_like

    @property
    def priv_reply(self) -> int:
        return self._priv_reply

    @priv_reply.setter
    @_int_prop_check_ignore_none(1)
    def priv_reply(self, new_priv_reply: Literal[1, 5, 6]) -> NoReturn:
        self._priv_reply = new_priv_reply


class _Container(object):
    """
    基本的内容信息

    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo类 发布者信息
    text: 文本内容
    """

    __slots__ = ['fid', 'tid', 'pid', 'user', '_text']

    def __init__(self, fid: int = 0, tid: int = 0, pid: int = 0, user: UserInfo = UserInfo(), text: str = '') -> NoReturn:
        self.fid = fid
        self.tid = tid
        self.pid = pid
        self.user = user
        self._text = text

    @property
    def text(self) -> str:
        return self._text


T = TypeVar('T')


class _Containers(Generic[T]):
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

    def __iter__(self) -> Iterator[T]:
        return iter(self._objs)

    def __getitem__(self, idx: int) -> T:
        return self._objs[idx]

    @final
    def __setitem__(self, idx, val):
        raise NotImplementedError

    @final
    def __delitem__(self, idx):
        raise NotImplementedError

    def __len__(self) -> int:
        return len(self._objs)

    def __bool__(self) -> bool:
        return len(self._objs) > 0

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

    __slots__ = ['title', 'first_floor_text', 'imgs', 'emojis',
                 'view_num', 'reply_num', 'like', 'dislike', 'create_time', 'last_time']

    def __init__(self, fid: int = 0, tid: int = 0, pid: int = 0, user: UserInfo = UserInfo(), title: str = '', first_floor_text: str = '', imgs: list[str] = [], emojis: list[str] = [], view_num: int = 0, reply_num: int = 0, like: int = 0, dislike: int = 0, create_time: int = 0, last_time: int = 0) -> NoReturn:
        super().__init__(fid=fid, tid=tid, pid=pid, user=user)
        self.title = title
        self.first_floor_text = first_floor_text
        self.imgs = imgs
        self.emojis = emojis
        self.view_num = view_num
        self.reply_num = reply_num
        self.like = like
        self.dislike = dislike
        self.create_time = create_time
        self.last_time = last_time

    @property
    def text(self) -> str:
        if not self._text:
            self._text = f'{self.title}\n{self.first_floor_text}'
        return self._text


class Threads(_Containers[Thread]):
    """
    Thread列表

    current_pn: 当前页数
    total_pn: 总页数
    has_next: 是否有下一页
    """

    __slots__ = []

    def __init__(self, main_proto=None) -> NoReturn:

        def _init_userinfo(user_proto) -> UserInfo:
            try:
                user_id = user_proto.id
                if 0 >= user_id:
                    return UserInfo()
                priv_proto = user_proto.priv_sets
                user = UserInfo(user_name=user_proto.name,
                                nick_name=user_proto.name_show,
                                portrait=user_proto.portrait,
                                user_id=user_id,
                                gender=user_proto.gender,
                                priv_like=priv_proto.like,
                                priv_reply=priv_proto.reply
                                )
                return user

            except Exception as err:
                log.error(
                    f"Failed to init UserInfo of {user_id} in {fid}. reason:line {err.__traceback__.tb_lineno} {err}")
                return UserInfo()

        def _init_obj(obj_proto) -> Thread:
            try:
                texts = []
                imgs = []
                emojis = []
                for fragment in obj_proto.first_post_content:
                    ftype = fragment.type
                    if ftype in [0, 4, 9, 18]:  # 0纯文本 4手机号 9@ 18话题
                        texts.append(fragment.text)
                    elif ftype == 1:
                        texts.append(
                            f"{fragment.link} {fragment.text}")
                    elif ftype == 2:
                        emojis.append(fragment.text)
                    elif ftype == 3:
                        imgs.append(fragment.cdn_src)
                first_floor_text = ''.join(texts)

                author_id = obj_proto.author_id
                thread = Thread(fid=fid,
                                tid=obj_proto.id,
                                pid=obj_proto.first_post_id,
                                user=users.get(author_id, UserInfo()),
                                title=obj_proto.title,
                                first_floor_text=first_floor_text,
                                imgs=imgs,
                                emojis=emojis,
                                view_num=obj_proto.view_num,
                                reply_num=obj_proto.reply_num,
                                like=obj_proto.agree.agree_num,
                                dislike=obj_proto.agree.disagree_num,
                                create_time=obj_proto.create_time,
                                last_time=obj_proto.last_time_int
                                )
                return thread

            except Exception as err:
                log.error(
                    f"Failed to init Thread in {fid}. reason:line {err.__traceback__.tb_lineno} {err}")
                return Thread()

        if main_proto:
            data_proto = main_proto.data
            try:
                self.current_pn = data_proto.page.current_page
                self.total_pn = data_proto.page.total_page
                fid = data_proto.forum.id
            except Exception as err:
                raise ValueError(f"line {err.__traceback__.tb_lineno} {err}")

            users = {user_proto.id: _init_userinfo(user_proto)
                     for user_proto in data_proto.user_list}
            self._objs = [_init_obj(obj_proto)
                          for obj_proto in data_proto.thread_list]

        else:
            self._objs = []
            self.current_pn = 0
            self.total_pn = 0


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

    __slots__ = ['content', 'sign', 'imgs', 'emojis', 'has_audio', 'floor',
                 'reply_num', 'like', 'dislike', 'create_time', 'is_thread_owner']

    def __init__(self, fid: int = 0, tid: int = 0, pid: int = 0, user: UserInfo = UserInfo(), content: str = '', sign: str = '', imgs: list[str] = [], emojis: list[str] = [], has_audio: bool = False, floor: int = 0, reply_num: int = 0, like: int = 0, dislike: int = 0, create_time: int = 0, is_thread_owner: bool = False) -> NoReturn:
        super().__init__(fid=fid, tid=tid, pid=pid, user=user)
        self.content = content
        self.sign = sign
        self.imgs = imgs
        self.emojis = emojis
        self.has_audio = has_audio
        self.floor = floor
        self.reply_num = reply_num
        self.like = like
        self.dislike = dislike
        self.create_time = create_time
        self.is_thread_owner = is_thread_owner

    @property
    def text(self) -> str:
        if not self._text:
            self._text = f'{self.content}\n{self.sign}'
        return self._text


class Posts(_Containers[Post]):
    """
    Post列表

    current_pn: 当前页数
    total_pn: 总页数
    has_next: 是否有下一页
    """

    __slots__ = []

    def __init__(self, main_proto=None) -> NoReturn:

        def _init_userinfo(user_proto) -> UserInfo:
            try:
                user_id = user_proto.id
                if 0 >= user_id:
                    return UserInfo()
                priv_proto = user_proto.priv_sets
                user = UserInfo(user_name=user_proto.name,
                                nick_name=user_proto.name_show,
                                portrait=user_proto.portrait,
                                user_id=user_id,
                                gender=user_proto.gender,
                                priv_like=priv_proto.like,
                                priv_reply=priv_proto.reply
                                )
                return user

            except Exception as err:
                log.error(
                    f"Failed to init UserInfo of {user_id} in {tid}. reason:line {err.__traceback__.tb_lineno} {err}")
                return UserInfo()

        def _init_obj(obj_proto) -> Post:
            try:
                texts = []
                imgs = []
                emojis = []
                has_audio = False
                for fragment in obj_proto.content:
                    ftype = fragment.type
                    if ftype in [0, 4, 9, 18]:  # 0纯文本 4手机号 9@ 18话题
                        texts.append(fragment.text)
                    elif ftype == 1:
                        texts.append(
                            f"{fragment.link} {fragment.text}")
                    elif ftype == 2:
                        emojis.append(fragment.text)
                    elif ftype == 3:
                        imgs.append(fragment.cdn_src)
                    elif ftype == 10:
                        has_audio = True
                content = ''.join(texts)

                author_id = obj_proto.author_id
                post = Post(fid=fid,
                            tid=tid,
                            pid=obj_proto.id,
                            user=users.get(author_id, UserInfo()),
                            content=content,
                            sign=''.join(
                                [sign.text for sign in obj_proto.signature.content if sign.type == 0]),
                            imgs=imgs,
                            emojis=emojis,
                            has_audio=has_audio,
                            floor=obj_proto.floor,
                            reply_num=obj_proto.sub_post_number,
                            like=obj_proto.agree.agree_num,
                            dislike=obj_proto.agree.disagree_num,
                            create_time=obj_proto.time,
                            is_thread_owner=author_id == thread_owner_id,
                            )

                return post

            except Exception as err:
                log.error(
                    f"Failed to init Post in {tid}. reason:line {err.__traceback__.tb_lineno} {err}")
                return Post()

        if main_proto:
            data_proto = main_proto.data
            try:
                self.current_pn = data_proto.page.current_page
                self.total_pn = data_proto.page.total_page
                thread_owner_id = data_proto.thread.author_id
                fid = data_proto.forum.id
                tid = data_proto.thread.id
            except Exception as err:
                raise ValueError(f"line {err.__traceback__.tb_lineno}: {err}")

            users = {user_proto.id: _init_userinfo(user_proto)
                     for user_proto in data_proto.user_list}
            self._objs = [_init_obj(obj_proto)
                          for obj_proto in data_proto.post_list]

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

    __slots__ = ['emojis', 'has_audio', 'like', 'dislike', 'create_time']

    def __init__(self, fid: int = 0, tid: int = 0, pid: int = 0, user: UserInfo = UserInfo(), text: str = '', emojis: list[str] = [], has_audio: bool = False, like: int = 0, dislike: int = 0, create_time: int = 0) -> NoReturn:
        super().__init__(fid=fid, tid=tid, pid=pid, user=user, text=text)
        self.emojis = emojis
        self.has_audio = has_audio
        self.like = like
        self.dislike = dislike
        self.create_time = create_time


class Comments(_Containers[Comment]):
    """
    Comment列表

    current_pn: 当前页数
    total_pn: 总页数
    has_next: 是否有下一页
    """

    __slots__ = []

    def __init__(self, main_proto=None) -> NoReturn:

        def _init_obj(obj_proto) -> Comment:
            try:
                texts = []
                emojis = []
                has_audio = False
                for fragment in obj_proto.content:
                    ftype = fragment.type
                    if ftype in [0, 4, 9, 18]:  # 0纯文本 4手机号 9@ 18话题
                        texts.append(fragment.text)
                    elif ftype == 1:
                        texts.append(
                            f"{fragment.link} {fragment.text}")
                    elif ftype == 2:
                        emojis.append(fragment.text)
                    elif ftype == 10:
                        has_audio = True
                text = ''.join(texts)

                user_proto = obj_proto.author
                priv_proto = user_proto.priv_sets
                user = UserInfo(user_name=user_proto.name,
                                nick_name=user_proto.name_show,
                                portrait=user_proto.portrait,
                                user_id=user_proto.id,
                                gender=user_proto.gender,
                                priv_like=priv_proto.like,
                                priv_reply=priv_proto.reply
                                )

                comment = Comment(fid=fid,
                                  tid=tid,
                                  pid=obj_proto.id,
                                  user=user,
                                  text=text,
                                  emojis=emojis,
                                  has_audio=has_audio,
                                  like=obj_proto.agree.agree_num,
                                  dislike=obj_proto.agree.disagree_num,
                                  create_time=obj_proto.time
                                  )
                return comment

            except Exception as err:
                log.error(
                    f"Failed to init Comment in {tid}. reason:line {err.__traceback__.tb_lineno} {err}")
                return Comment()

        if main_proto:
            data_proto = main_proto.data
            try:
                self.current_pn = data_proto.page.current_page
                self.total_pn = data_proto.page.total_page
                fid = data_proto.forum.id
                tid = data_proto.thread.id
            except Exception as err:
                raise ValueError(f"line {err.__traceback__.tb_lineno}: {err}")

            self._objs = [_init_obj(obj_proto)
                          for obj_proto in data_proto.subpost_list]

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
                user = UserInfo(user_name=user_dict['name'],
                                nick_name=user_dict['name_show'],
                                portrait=user_dict['portrait'],
                                user_id=user_dict['id'],
                                priv_like=priv_sets.get('like', None),
                                priv_reply=priv_sets.get('reply', None)
                                )
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
