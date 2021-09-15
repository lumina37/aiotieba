# -*- coding:utf-8 -*-
__all__ = ('UserInfo',
           'Thread', 'Post', 'Comment',
           'Threads', 'Posts', 'Comments',
           'At')


import os
import sys
import traceback

import re

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
                 '_gender']

    def __init__(self, user_name='', nick_name='', portrait='', user_id=0, level=0, gender=0):
        self.user_name = user_name
        self.nick_name = nick_name
        self.portrait = portrait
        self.user_id = user_id
        self.level = level
        self.gender = gender

    @property
    def nick_name(self):
        return self._nick_name

    @nick_name.setter
    def nick_name(self, new_nick_name: str):
        if self.user_name != new_nick_name:
            self._nick_name = new_nick_name
        else:
            self._nick_name = ''

    @property
    def portrait(self):
        return self._portrait

    @portrait.setter
    def portrait(self, new_portrait: str):
        try:
            assert new_portrait.startswith(
                'tb.'), f"portrait:{new_portrait} do not start with tb."
            new_portrait = new_portrait[:36]
            self._portrait = new_portrait[:-
                                          1] if new_portrait.endswith('?') else new_portrait
        except Exception:
            self._portrait = ''

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, new_user_id):
        try:
            self._user_id = int(new_user_id)
        except Exception:
            self._user_id = 0

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, new_level):
        try:
            self._level = int(new_level)
        except Exception:
            self._level = 0

    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, new_gender):
        try:
            self._gender = int(new_gender)
        except Exception:
            self._gender = 0

    @property
    def name(self):
        return self.user_name if self.user_name else self.nick_name

    @property
    def logname(self):
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

    __slots__ = ['_fid', '_tid', '_pid', '_text', 'user']

    def __init__(self, fid=0, tid=0, pid=0, text='', user=UserInfo()):
        self._fid = fid
        self._tid = tid
        self._pid = pid
        self._text = text
        self.user = user

    @property
    def fid(self):
        return self._fid

    @fid.setter
    def fid(self, new_fid):
        self._fid = int(new_fid)

    @property
    def tid(self):
        return self._tid

    @tid.setter
    def tid(self, new_tid):
        self._tid = int(new_tid)

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, new_pid):
        self._pid = int(new_pid)

    @property
    def text(self):
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
    view_num: 浏览量
    reply_num: 回复数
    like: 点赞数
    dislike: 点踩数
    create_time: 10位时间戳 创建时间
    last_time: 10位时间戳 最后回复时间
    """

    __slots__ = ['title', 'first_floor_text', 'has_audio', 'has_video',
                 '_view_num', '_reply_num', '_like', '_dislike', '_create_time', '_last_time']

    def __init__(self, fid=0, tid=0, pid=0, user=UserInfo(), title='', first_floor_text='', has_audio=False, has_video=False, view_num=0, reply_num=0, like=0, dislike=0, create_time=0, last_time=0):
        super().__init__(fid=fid, tid=tid, pid=pid, user=user)
        self.title = title
        self.first_floor_text = first_floor_text
        self.has_audio = has_audio
        self.has_video = has_video
        self.view_num = view_num
        self.reply_num = reply_num
        self.like = like
        self.dislike = dislike
        self.create_time = create_time
        self.last_time = last_time

    @property
    def text(self):
        if not self._text:
            self._text = f'{self.title}\n{self.first_floor_text}'
        return self._text

    @property
    def reply_num(self):
        return self._reply_num

    @reply_num.setter
    def reply_num(self, new_reply_num):
        self._reply_num = int(new_reply_num)

    @property
    def view_num(self):
        return self._view_num

    @view_num.setter
    def view_num(self, new_view_num):
        self._view_num = int(new_view_num)

    @property
    def like(self):
        return self._like

    @like.setter
    def like(self, new_like):
        self._like = int(new_like)

    @property
    def dislike(self):
        return self._dislike

    @dislike.setter
    def dislike(self, new_dislike):
        self._dislike = int(new_dislike)

    @property
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, new_create_time):
        self._create_time = int(new_create_time)

    @property
    def last_time(self):
        return self._last_time

    @last_time.setter
    def last_time(self, new_last_time):
        self._last_time = int(new_last_time)


class Threads(list):
    """
    thread列表
    """

    __slots__ = ['_current_pn', '_total_pn']

    def __init__(self, main_json=None):

        if main_json:
            users = {}
            for user_dict in main_json['user_list']:
                users[user_dict['id']] = UserInfo(user_name=user_dict['name'],
                                                  nick_name=user_dict['name_show'],
                                                  portrait=user_dict['portrait'],
                                                  user_id=user_dict['id'],
                                                  gender=user_dict['gender'])
            fid = main_json['forum']['id']

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
                        like = thread_raw['agree']['agree_num']
                        dislike = thread_raw['agree']['disagree_num']
                    else:
                        like = thread_raw['agree_num']
                        dislike = 0

                    thread = Thread(fid=fid,
                                    tid=thread_raw['tid'],
                                    pid=thread_raw['first_post_id'],
                                    user=users.get(
                                        thread_raw['author_id'], UserInfo()),
                                    title=thread_raw['title'],
                                    first_floor_text=first_floor_text,
                                    has_audio=True if thread_raw.get(
                                        'voice_info', None) else False,
                                    has_video=True if thread_raw.get(
                                        'video_info', None) else False,
                                    view_num=thread_raw['view_num'],
                                    reply_num=thread_raw['reply_num'],
                                    like=like,
                                    dislike=dislike,
                                    create_time=thread_raw['create_time'],
                                    last_time=thread_raw['last_time_int']
                                    )

                    self.append(thread)

                except:
                    log.warning(traceback.format_exc())
                    continue

            self.current_pn = main_json['page']['current_page']
            self.total_pn = main_json['page']['total_page']

        else:
            self._current_pn = 0
            self._total_pn = 0

    @property
    def current_pn(self):
        return self._current_pn

    @current_pn.setter
    def current_pn(self, new_current_pn):
        self._current_pn = int(new_current_pn)

    @property
    def total_pn(self):
        return self._total_pn

    @total_pn.setter
    def total_pn(self, new_total_pn):
        self._total_pn = int(new_total_pn)

    @property
    def has_next(self):
        return self._current_pn < self._total_pn


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

    __slots__ = ['content', 'sign', 'imgs', 'smileys', 'has_audio', '_floor',
                 '_reply_num', '_like', '_dislike', '_create_time', 'is_thread_owner']

    def __init__(self, fid=0, tid=0, pid=0, user=UserInfo(), content='', sign='', imgs=[], smileys=[], has_audio=False, floor=0, reply_num=0, like=0, dislike=0, create_time=0, is_thread_owner=False):
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
    def text(self):
        if not self._text:
            self._text = f'{self.content}\n{self.sign}'
        return self._text

    @property
    def reply_num(self):
        return self._reply_num

    @reply_num.setter
    def reply_num(self, new_reply_num):
        self._reply_num = int(new_reply_num)

    @property
    def like(self):
        return self._like

    @like.setter
    def like(self, new_like):
        self._like = int(new_like)

    @property
    def dislike(self):
        return self._dislike

    @dislike.setter
    def dislike(self, new_dislike):
        self._dislike = int(new_dislike)

    @property
    def floor(self):
        return self._floor

    @floor.setter
    def floor(self, new_floor):
        self._floor = int(new_floor)

    @property
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, new_create_time):
        self._create_time = int(new_create_time)


class Posts(list):
    """
    post列表

    current_pn: 当前页数
    total_pn: 总页数
    """

    __slots__ = ['_current_pn', '_total_pn']

    def __init__(self, main_json=None):

        if main_json:
            users = {}
            for user_dict in main_json['user_list']:
                if not user_dict.get('portrait', None):
                    continue
                users[user_dict['id']] = UserInfo(user_name=user_dict['name'],
                                                  nick_name=user_dict['name_show'],
                                                  portrait=user_dict['portrait'],
                                                  user_id=user_dict['id'],
                                                  level=user_dict.get(
                                                      'level_id', 0),
                                                  gender=user_dict['gender'])

            thread_owner_id = main_json["thread"]['author']['id']
            fid = main_json['forum']['id']
            tid = main_json['thread']['id']

            for post_raw in main_json['post_list']:
                try:

                    texts = []
                    imgs = []
                    smileys = []
                    has_audio = False
                    for fragment in post_raw['content']:
                        ftype = int(fragment.get('type',0))
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

                    post = Post(fid=fid,
                                tid=tid,
                                pid=post_raw['id'],
                                user=users.get(
                                    post_raw['author_id'], UserInfo()),
                                content=content,
                                sign=''.join([sign['text'] for sign in post_raw['signature']['content']
                                              if sign['type'] == '0']) if post_raw.get('signature', None) else '',
                                imgs=imgs,
                                smileys=smileys,
                                has_audio=has_audio,
                                floor=post_raw['floor'],
                                reply_num=post_raw['sub_post_number'],
                                like=post_raw['agree']['agree_num'],
                                dislike=post_raw['agree']['disagree_num'],
                                is_thread_owner=post_raw['author_id'] == thread_owner_id,
                                )

                    self.append(post)

                except Exception:
                    log.warning(traceback.format_exc())
                    continue

            self.current_pn = main_json['page']['current_page']
            self.total_pn = main_json['page']['total_page']

        else:
            self._current_pn = 0
            self._total_pn = 0

    @property
    def current_pn(self):
        return self._current_pn

    @current_pn.setter
    def current_pn(self, new_current_pn):
        self._current_pn = int(new_current_pn)

    @property
    def total_pn(self):
        return self._total_pn

    @total_pn.setter
    def total_pn(self, new_total_pn):
        self._total_pn = int(new_total_pn)

    @property
    def has_next(self):
        return self._current_pn < self._total_pn


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

    __slots__ = ['smileys', 'has_audio', '_like', '_dislike', '_create_time']

    def __init__(self, fid=0, tid=0, pid=0, user=UserInfo(), text='', smileys=[], has_audio=False, like=0, dislike=0, create_time=0):
        super().__init__(fid=fid, tid=tid, pid=pid, user=user)
        self._text = text
        self.smileys = smileys
        self.has_audio = has_audio
        self.like = like
        self.dislike = dislike
        self.create_time = create_time

    @property
    def like(self):
        return self._like

    @like.setter
    def like(self, new_like):
        self._like = int(new_like)

    @property
    def dislike(self):
        return self._dislike

    @dislike.setter
    def dislike(self, new_dislike):
        self._dislike = int(new_dislike)

    @property
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, new_create_time):
        self._create_time = int(new_create_time)


class Comments(list):
    """
    comment列表

    current_pn: 当前页数
    total_pn: 总页数
    """

    __slots__ = ['_current_pn', '_total_pn']

    def __init__(self, main_json=None):

        if main_json:
            fid = main_json['forum']['id']
            tid = main_json['thread']['id']

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
                                    gender=user_dict['gender'])

                    comment = Comment(fid=fid,
                                      tid=tid,
                                      pid=comment_raw['id'],
                                      user=user,
                                      text=text,
                                      smileys=smileys,
                                      has_audio=has_audio,
                                      like=comment_raw['agree']['agree_num'],
                                      dislike=comment_raw['agree']['disagree_num'],
                                      create_time=comment_raw['time']
                                      )

                    self.append(comment)

                except:
                    log.warning(traceback.format_exc())
                    continue

            self.current_pn = main_json['page']['current_page']
            self.total_pn = main_json['page']['total_page']

        else:
            self._current_pn = 0
            self._total_pn = 0

    @property
    def current_pn(self):
        return self._current_pn

    @current_pn.setter
    def current_pn(self, new_current_pn):
        self._current_pn = int(new_current_pn)

    @property
    def total_pn(self):
        return self._total_pn

    @total_pn.setter
    def total_pn(self, new_total_pn):
        self._total_pn = int(new_total_pn)

    @property
    def has_next(self):
        return self._current_pn < self._total_pn


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

    __slots__ = ['tieba_name', '_tid', '_pid', 'user', 'text', '_create_time']

    def __init__(self, tieba_name='', tid=0, pid=0, user=UserInfo(), text='', create_time=0):
        self.tieba_name = tieba_name
        self.tid = tid
        self.pid = pid
        self.user = user
        self.text = text
        self.create_time = create_time

    @property
    def tid(self):
        return self._tid

    @tid.setter
    def tid(self, new_tid):
        self._tid = int(new_tid)

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, new_pid):
        self._pid = int(new_pid)

    @property
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, new_create_time):
        self._create_time = int(new_create_time)
