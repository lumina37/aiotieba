# -*- coding:utf-8 -*-
__all__ = ('UserInfo',
           'Thread', 'Post', 'Comment',
           'Threads', 'Posts', 'Comments',
           'At')

import re
import traceback
from typing import Dict, List, Union

from .logger import log


class UserInfo(object):
    """
    UserInfo()
    用户属性，一般包括下列五项

    user_name: 发帖用户名
    nick_name: 发帖人昵称
    portrait: 用户头像portrait值
    level: 等级
    gender: 性别（1男2女0未知）
    """

    __slots__ = ['user_name',
                 '_nick_name',
                 '_portrait',
                 '_user_id',
                 '_level',
                 '_gender',
                 'is_vip',
                 'is_god']

    def __init__(self, _id: Union[str, None] = None, user_name: str = '', nick_name: str = '', portrait: str = '', user_id: int = 0, level: int = 0, gender: int = 0, is_vip: bool = False, is_god: bool = False):
        if _id:
            if isinstance(_id, int):
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
        self.level = level
        self.gender = gender
        self.is_vip = is_vip
        self.is_god = is_god

    def __str__(self) -> str:
        return f"user_name:{self.user_name} / nick_name:{self._nick_name} / portrait:{self._portrait} / user_id:{self._user_id}"

    @property
    def nick_name(self) -> str:
        return self._nick_name

    @nick_name.setter
    def nick_name(self, new_nick_name: str):
        if self.user_name != new_nick_name:
            self._nick_name = new_nick_name
        else:
            self._nick_name = ''

    @property
    def portrait(self) -> str:
        return self._portrait

    @portrait.setter
    def portrait(self, new_portrait: str):
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
    def user_id(self, new_user_id):
        if new_user_id:
            self._user_id = int(new_user_id)
        else:
            self._user_id = 0

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, new_level):
        if new_level:
            self._level = int(new_level)
        else:
            self._level = 0

    @property
    def gender(self) -> int:
        return self._gender

    @gender.setter
    def gender(self, new_gender):
        if new_gender:
            self._gender = int(new_gender)
        else:
            self._gender = 0

    @property
    def name(self) -> str:
        return self.user_name if self.user_name else self.nick_name

    @property
    def logname(self) -> str:
        if self.user_name:
            return self.user_name
        else:
            return f'{self.nick_name}/{self.portrait}'


class _BaseContent(object):
    """
    基本的内容信息

    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    text: 文本内容
    user: UserInfo类 发布者信息
    """

    __slots__ = ['fid', 'tid', 'pid', '_text', 'user']

    def __init__(self, fid: int = 0, tid: int = 0, pid: int = 0, text: str = '', user: UserInfo = UserInfo()):
        self.fid = fid
        self.tid = tid
        self.pid = pid
        self._text = text
        self.user = user

    @property
    def text(self) -> str:
        return self._text


class Thread(_BaseContent):
    """
    主题帖信息

    text: 所有文本
    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo类 发布者信息
    title: 标题内容
    first_floor_text: 首楼内容
    has_audio: 是否含有音频
    has_video: 是否含有视频
    reply_able: 是否可以回复
    view_num: 浏览量
    reply_num: 回复数
    like: 点赞数
    dislike: 点踩数
    create_time: 10位时间戳 创建时间
    last_time: 10位时间戳 最后回复时间
    """

    __slots__ = ['title', 'first_floor_text', 'has_audio', 'has_video', 'reply_able',
                 'view_num', 'reply_num', 'like', 'dislike', 'create_time', 'last_time']

    def __init__(self, fid: int = 0, tid: int = 0, pid: int = 0, user: UserInfo = UserInfo(), title: str = '', first_floor_text: str = '', has_audio: bool = False, has_video: bool = False, reply_able: bool = True, view_num: int = 0, reply_num: int = 0, like: int = 0, dislike: int = 0, create_time: int = 0, last_time: int = 0):
        super().__init__(fid=fid, tid=tid, pid=pid, user=user)
        self.title = title
        self.first_floor_text = first_floor_text
        self.has_audio = has_audio
        self.has_video = has_video
        self.reply_able = reply_able
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


class Threads(list):
    """
    thread列表
    """

    __slots__ = ['current_pn', 'total_pn']

    def __init__(self, main_json: Union[Dict, None] = None):

        if main_json:
            try:
                self.current_pn = int(main_json['page']['current_page'])
                self.total_pn = int(main_json['page']['total_page'])
                fid = int(main_json['forum']['id'])
            except Exception as err:
                raise ValueError(
                    f"Null value at line {err.__traceback__.tb_lineno}")

            users = {}
            reply_access = {}
            for user_dict in main_json['user_list']:
                try:
                    user_id = int(user_dict['id'])
                    users[user_id] = UserInfo(user_name=user_dict['name'],
                                              nick_name=user_dict['name_show'],
                                              portrait=user_dict['portrait'],
                                              user_id=user_id,
                                              gender=user_dict['gender'],
                                              is_vip=bool(
                                                  user_dict['new_tshow_icon']),
                                              is_god=user_dict.__contains__(
                                                  'new_god_data')
                                              )
                    if user_dict['priv_sets']:
                        reply_access[user_id] = int(
                            user_dict['priv_sets'].get('reply', 1)) == 1
                    else:
                        reply_access[user_id] = True
                except Exception as err:
                    log.error(
                        f"Failed to init UserInfo of {user_dict['portrait']} in fid:{fid}. reason:{traceback.format_tb(err.__traceback__)[-1]}")
                    continue

            for thread_raw in main_json['thread_list']:
                try:
                    if thread_raw['task_info']:
                        continue

                    texts = []
                    for fragment in thread_raw['first_post_content']:
                        ftype = int(fragment['type'])
                        if ftype in [0, 4, 9, 18]:
                            texts.append(fragment['text'])
                        elif ftype == 1:
                            texts.append(
                                f"{fragment['link']} {fragment['text']}")
                    first_floor_text = ''.join(texts)

                    if isinstance(thread_raw['agree'], dict):
                        like = int(thread_raw['agree']['agree_num'])
                        dislike = int(thread_raw['agree']['disagree_num'])
                    else:
                        like = 0
                        dislike = 0

                    author_id = int(thread_raw['author_id'])
                    thread = Thread(fid=fid,
                                    tid=int(thread_raw['tid']),
                                    pid=int(thread_raw['first_post_id']),
                                    user=users.get(author_id, UserInfo()),
                                    title=thread_raw['title'],
                                    first_floor_text=first_floor_text,
                                    has_audio=True if thread_raw.get(
                                        'voice_info', None) else False,
                                    has_video=True if thread_raw.get(
                                        'video_info', None) else False,
                                    reply_able=reply_access.get(
                                        author_id, True),
                                    view_num=int(thread_raw['view_num']),
                                    reply_num=int(thread_raw['reply_num']),
                                    like=like,
                                    dislike=dislike,
                                    create_time=int(thread_raw['create_time']),
                                    last_time=int(thread_raw['last_time_int'])
                                    )

                    self.append(thread)

                except Exception as err:
                    log.error(
                        f"Failed to init Thread in {fid}. reason:{traceback.format_tb(err.__traceback__)[-1]}")
                    continue

        else:
            self.current_pn = 0
            self.total_pn = 0

    @property
    def has_next(self) -> bool:
        return self.current_pn < self.total_pn


class Post(_BaseContent):
    """
    楼层信息

    text: 所有文本
    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo类 发布者信息
    content: 正文
    sign: 小尾巴
    imgs: 图片列表
    smileys: 表情列表
    has_audio: 是否含有音频
    floor: 楼层数
    reply_num: 楼中楼回复数
    like: 点赞数
    dislike: 点踩数
    create_time: 10位时间戳，创建时间
    is_thread_owner: 是否楼主
    """

    __slots__ = ['content', 'sign', 'imgs', 'smileys', 'has_audio', 'floor',
                 'reply_num', 'like', 'dislike', 'create_time', 'is_thread_owner']

    def __init__(self, fid: int = 0, tid: int = 0, pid: int = 0, user: UserInfo = UserInfo(), content: str = '', sign: str = '', imgs: List[str] = [], smileys: List[str] = [], has_audio: bool = False, floor: int = 0, reply_num: int = 0, like: int = 0, dislike: int = 0, create_time: int = 0, is_thread_owner: bool = False):
        super().__init__(fid=fid, tid=tid, pid=pid, user=user)
        self.content = content
        self.sign = sign
        self.imgs = imgs
        self.smileys = smileys
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


class Posts(list):
    """
    post列表

    current_pn: 当前页数
    total_pn: 总页数
    """

    __slots__ = ['current_pn', 'total_pn']

    def __init__(self, main_json: Union[Dict, None] = None):

        if main_json:
            try:
                self.current_pn = int(main_json['page']['current_page'])
                self.total_pn = int(main_json['page']['total_page'])
                thread_owner_id = int(main_json['thread']['author']['id'])
                fid = int(main_json['forum']['id'])
                tid = int(main_json['thread']['id'])
            except Exception as err:
                raise ValueError(
                    f"Null value at line {err.__traceback__.tb_lineno}")

            users = {}
            for user_dict in main_json['user_list']:
                try:
                    user_id = int(user_dict['id'])
                    users[user_id] = UserInfo(user_name=user_dict['name'],
                                              nick_name=user_dict['name_show'],
                                              portrait=user_dict['portrait'],
                                              user_id=user_id,
                                              level=user_dict['level_id'],
                                              gender=user_dict['gender'],
                                              is_vip=bool(
                                                  user_dict['new_tshow_icon']),
                                              is_god=user_dict['new_god_data']['field_id'] != '')
                except Exception as err:
                    log.error(
                        f"Failed to init UserInfo of {user_dict['portrait']} in tid:{tid}. reason:{traceback.format_tb(err.__traceback__)[-1]}")
                    continue

            for post_raw in main_json['post_list']:
                try:
                    texts = []
                    imgs = []
                    smileys = []
                    has_audio = False
                    for fragment in post_raw['content']:
                        ftype = int(fragment.get('type', 0))
                        if ftype in [0, 4, 9, 18]:
                            texts.append(fragment['text'])
                        elif ftype == 1:
                            texts.append(fragment['link'])
                            texts.append(' ' + fragment['text'])
                        elif ftype == 2:
                            smileys.append(fragment['text'])
                        elif ftype == 3:
                            imgs.append(fragment['origin_src'])
                        elif ftype == 10:
                            has_audio = True
                    content = ''.join(texts)

                    author_id = int(post_raw['author_id'])
                    post = Post(fid=fid,
                                tid=tid,
                                pid=int(post_raw['id']),
                                user=users.get(author_id, UserInfo()),
                                content=content,
                                sign=''.join([sign['text'] for sign in post_raw['signature']['content']
                                              if sign['type'] == '0']) if post_raw.get('signature', None) else '',
                                imgs=imgs,
                                smileys=smileys,
                                has_audio=has_audio,
                                floor=int(post_raw['floor']),
                                reply_num=int(post_raw['sub_post_number']),
                                like=int(post_raw['agree']['agree_num']),
                                dislike=int(post_raw['agree']['disagree_num']),
                                create_time=int(post_raw['time']),
                                is_thread_owner=author_id == thread_owner_id,
                                )

                    self.append(post)

                except Exception as err:
                    log.error(
                        f"Failed to init Post in {tid}. reason:{traceback.format_tb(err.__traceback__)[-1]}")
                    continue

        else:
            self.current_pn = 0
            self.total_pn = 0

    @property
    def has_next(self) -> bool:
        return self.current_pn < self.total_pn


class Comment(_BaseContent):
    """
    楼中楼信息

    text: 正文
    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo类 发布者信息
    like: 点赞数
    dislike: 点踩数
    has_audio: 是否含有音频
    create_time: 10位时间戳，创建时间
    smileys: 表情列表
    """

    __slots__ = ['smileys', 'has_audio', 'like', 'dislike', 'create_time']

    def __init__(self, fid: int = 0, tid: int = 0, pid: int = 0, user: UserInfo = UserInfo(), text: str = '', smileys: List[str] = [], has_audio: bool = False, like: int = 0, dislike: int = 0, create_time: int = 0):
        super().__init__(fid=fid, tid=tid, pid=pid, user=user)
        self._text = text
        self.smileys = smileys
        self.has_audio = has_audio
        self.like = like
        self.dislike = dislike
        self.create_time = create_time


class Comments(list):
    """
    comment列表

    current_pn: 当前页数
    total_pn: 总页数
    """

    __slots__ = ['current_pn', 'total_pn']

    def __init__(self, main_json: Union[Dict, None] = None):

        if main_json:
            try:
                self.current_pn = int(main_json['page']['current_page'])
                self.total_pn = int(main_json['page']['total_page'])
                fid = int(main_json['forum']['id'])
                tid = int(main_json['thread']['id'])
            except Exception as err:
                raise ValueError(
                    f"Null value at line {err.__traceback__.tb_lineno}")

            for comment_raw in main_json['subpost_list']:
                try:
                    texts = []
                    smileys = []
                    has_audio = False
                    for fragment in comment_raw['content']:
                        ftype = int(fragment['type'])
                        if ftype in [0, 4, 9]:
                            texts.append(fragment['text'])
                        elif ftype == 1:
                            texts.append(fragment['link'])
                            texts.append(' ' + fragment['text'])
                        elif ftype == 2:
                            smileys.append(fragment['text'])
                        elif ftype == 10:
                            has_audio = True
                    text = ''.join(texts)

                    user_dict = comment_raw['author']
                    user = UserInfo(user_name=user_dict['name'],
                                    nick_name=user_dict['name_show'],
                                    portrait=user_dict['portrait'],
                                    user_id=user_dict['id'],
                                    level=user_dict['level_id'],
                                    gender=user_dict['gender'],
                                    is_vip=bool(user_dict['new_tshow_icon']),
                                    is_god=user_dict['new_god_data']['field_id'] != ''
                                    )

                    comment = Comment(fid=fid,
                                      tid=tid,
                                      pid=int(comment_raw['id']),
                                      user=user,
                                      text=text,
                                      smileys=smileys,
                                      has_audio=has_audio,
                                      like=int(
                                          comment_raw['agree']['agree_num']),
                                      dislike=int(
                                          comment_raw['agree']['disagree_num']),
                                      create_time=int(comment_raw['time'])
                                      )

                    self.append(comment)

                except Exception as err:
                    log.error(
                        f"Failed to init Comment in {tid}. reason:{traceback.format_tb(err.__traceback__)[-1]}")
                    continue

        else:
            self.current_pn = 0
            self.total_pn = 0

    @property
    def has_next(self) -> bool:
        return self.current_pn < self.total_pn


class At(object):
    """
    @信息

    text: 标题文本
    tieba_name: 帖子所在吧
    tid: 帖子编号
    pid: 回复编号
    user: UserInfo类 发布者信息
    create_time: 10位时间戳，创建时间
    """

    __slots__ = ['tieba_name', 'tid', 'pid', 'user', 'text', 'create_time']

    def __init__(self, tieba_name: str = '', tid: int = 0, pid: int = 0, user: UserInfo = UserInfo(), text: str = '', create_time: int = 0):
        self.tieba_name = tieba_name
        self.tid = tid
        self.pid = pid
        self.user = user
        self.text = text
        self.create_time = create_time
