# -*- coding:utf-8 -*-
__all__ = ('MODULE_DIR', 'SCRIPT_DIR',
           'UserInfo', 'UserInfo_Dict',
           'Thread', 'Post', 'Comment',
           'Threads', 'Posts', 'Comments',
           'At')


import os
import sys
from pathlib import Path
import traceback

import re

from .logger import log

import signal


def terminate(signalNumber, frame):
    sys.exit()


signal.signal(signal.SIGTERM, terminate)


MODULE_DIR = Path(__file__).parent
SCRIPT_DIR = Path(sys.argv[0]).parent


class UserInfo(object):
    """
    用户属性，一般包括下列五项

    user_name: 发帖用户名
    nick_name: 发帖人昵称
    portrait: 用户头像portrait值
    level: 等级
    gender: 性别（1男2女0未知）
    """

    __slots__ = ('user_name',
                 '_nick_name',
                 '_portrait',
                 '_user_id',
                 '_level',
                 '_gender')

    def __init__(self, _dict=None):
        if isinstance(_dict, dict):
            try:
                self.user_name = _dict.get('name', '')
                self.nick_name = _dict.get('name_show', '')
                self.portrait = _dict['portrait']
                self.user_id = _dict.get('id', None)
                self.level = _dict.get('level_id', None)
                self.gender = _dict.get('gender', None)
            except:
                log.warning(traceback.format_exc())
                self.set_null()
        else:
            self.set_null()

    def set_null(self):
        self.user_name = ''
        self.nick_name = ''
        self._portrait = ''
        self._user_id = 0
        self._level = 0
        self._gender = 0

    @property
    def nick_name(self):
        return self._nick_name

    @nick_name.setter
    def nick_name(self, new_nick_name):
        try:
            if type(new_nick_name) is str and new_nick_name != self.user_name:
                self._nick_name = new_nick_name
            else:
                self._nick_name = ''
        except:
            self._nick_name = ''

    @property
    def portrait(self):
        return self._portrait

    @portrait.setter
    def portrait(self, new_portrait):
        try:
            if not new_portrait.startswith('tb.'):
                raise
            self._portrait = new_portrait[:36]
        except:
            self._portrait = ''

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, new_user_id):
        if new_user_id:
            self._user_id = int(new_user_id)
        else:
            self._user_id = 0

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, new_level):
        if new_level:
            self._level = int(new_level)
        else:
            self._level = 0

    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, new_gender):
        if new_gender:
            self._gender = int(new_gender)
        else:
            self._gender = 0

    @property
    def name(self):
        return self.user_name if self.user_name else self.nick_name

    @property
    def logname(self):
        if self.user_name:
            return self.user_name
        else:
            return '/'.join([self.nick_name, self.portrait])


class UserInfo_Dict(dict):
    """
    可按id检索用户的字典
    UserInfo_Dict(user_list:list)

    参数:
        user_list: list 必须是从app接口获取的用户信息列表！
    """

    def __init__(self, user_list: list):
        for user_dict in user_list:
            self[user_dict['id']] = UserInfo(user_dict)


class _BaseContent(object):
    """
    基本的内容信息

    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    text: 文本内容
    user: UserInfo类 发布者信息
    """

    __slots__ = ('_fid', '_tid', '_pid',
                 '_text',
                 'user')

    def __init__(self):
        self._fid = 0
        self._tid = 0
        self._pid = 0
        self._text = ''
        self.user = UserInfo()

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
    title: 标题内容
    first_floor_text: 首楼内容
    reply_num: 回复数
    has_audio: 是否含有音频
    has_video: 是否含有视频
    like: 点赞数
    dislike: 点踩数
    create_time: 10位时间戳 创建时间
    last_time: 10位时间戳 最后回复时间
    user: UserInfo类 发布者信息
    """

    __slots__ = ('first_floor_text', 'title',
                 '_reply_num',
                 'has_audio', 'has_video',
                 '_like', '_dislike',
                 '_create_time', '_last_time')

    def __init__(self):
        self._text = ''
        pass

    @property
    def text(self):
        if not self._text:
            self._text = '{}\n{}'.format(self.title, self.first_floor_text)
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
        if new_like:
            self._like = int(new_like)
        else:
            self._like = 0

    @property
    def dislike(self):
        return self._dislike

    @dislike.setter
    def dislike(self, new_dislike):
        if new_dislike:
            self._dislike = int(new_dislike)
        else:
            self._dislike = 0

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

    def _init_content(self, content_fragments: list):
        """
        从回复内容的碎片列表中提取有用信息
        _init_content(content_fragments:list)
        """

        texts = []

        for fragment in content_fragments:
            if fragment['type'] in ['0', '4', '9', '18']:
                texts.append(fragment['text'])
            elif fragment['type'] == '1':
                texts.append(fragment['link'])
                texts.append(' ' + fragment['text'])

        self.first_floor_text = ''.join(texts)


class Threads(list):
    """
    thread列表
    """

    __slots__ = ('_current_pn', '_total_pn')

    def __init__(self, main_json=None):

        if main_json:
            users = UserInfo_Dict(main_json['user_list'])
            try:
                fid = main_json['forum']['id']
            except Exception:
                log.warning(traceback.format_exc())
                raise

            for thread_raw in main_json['thread_list']:
                try:
                    thread = Thread()
                    thread.user = users.get(
                        thread_raw['author_id'], UserInfo())
                    thread.title = thread_raw['title']
                    thread.fid = fid
                    thread.tid = thread_raw['tid']
                    thread.pid = thread_raw['first_post_id']
                    thread._init_content(
                        thread_raw.get('first_post_content', []))
                    thread.reply_num = thread_raw['reply_num']
                    thread.create_time = thread_raw['create_time']
                    thread.has_audio = True if thread_raw.get(
                        'voice_info', None) else False
                    thread.has_video = True if thread_raw.get(
                        'video_info', None) else False
                    thread.like = thread_raw.get('agree_num', 0)
                    thread.dislike = thread_raw.get('disagree_num', 0)
                    thread.last_time = thread_raw['last_time_int']
                    self.append(thread)
                except:
                    log.warning(traceback.format_exc())
                    raise

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
    content: 正文
    fid: 所在吧id
    tid: 帖子编号
    pid: 回复编号
    reply_num: 楼中楼回复数
    like: 点赞数
    dislike: 点踩数
    floor: 楼层数
    has_audio: 是否含有音频
    create_time: 10位时间戳，创建时间
    sign: 小尾巴
    imgs: 图片列表
    smileys: 表情列表
    user: UserInfo类 发布者信息
    is_thread_owner: 是否楼主
    """

    __slots__ = ('content',
                 '_reply_num',
                 '_like', '_dislike',
                 '_floor',
                 'has_audio',
                 '_create_time',
                 'sign', 'imgs', 'smileys',
                 'is_thread_owner')

    def __init__(self):
        self._text = ''
        pass

    @property
    def text(self):
        if not self._text:
            self._text = '{}\n{}'.format(self.content, self.sign)
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

    def _init_content(self, content_fragments: list):
        """
        从回复内容的碎片列表中提取有用信息
        _init_content(content_fragments:list)
        """

        texts = []
        self.imgs = []
        self.smileys = []
        self.has_audio = False
        for fragment in content_fragments:
            if fragment['type'] in ['0', '4', '9', '18']:
                texts.append(fragment['text'])
            elif fragment['type'] == '1':
                texts.append(fragment['link'])
                texts.append(' ' + fragment['text'])
            elif fragment['type'] == '2':
                self.smileys.append(fragment['text'])
            elif fragment['type'] == '3':
                self.imgs.append(fragment['origin_src'])
            elif fragment['type'] == '10':
                self.has_audio = True
        self.content = ''.join(texts)


class Posts(list):
    """
    post列表

    current_pn: 当前页数
    total_pn: 总页数
    """

    __slots__ = ('_current_pn', '_total_pn')

    def __init__(self, main_json=None):

        if main_json:
            users = UserInfo_Dict(main_json['user_list'])
            try:
                thread_owner_id = main_json["thread"]['author']['id']
                fid = main_json['forum']['id']
                tid = main_json['thread']['id']
            except Exception:
                log.warning(traceback.format_exc())
                raise

            for post_raw in main_json['post_list']:
                try:
                    post = Post()
                    post.user = users.get(post_raw['author_id'], UserInfo())
                    post.fid = fid
                    post.tid = tid
                    post.pid = post_raw['id']
                    post._init_content(post_raw['content'])
                    post.reply_num = post_raw['sub_post_number']
                    post.create_time = post_raw['time']
                    post.like = post_raw['agree']['agree_num']
                    post.dislike = post_raw['agree']['disagree_num']
                    post.floor = post_raw['floor']
                    post.is_thread_owner = post_raw['author_id'] == thread_owner_id
                    post.sign = ''.join([sign['text'] for sign in post_raw['signature']['content']
                                        if sign['type'] == '0']) if post_raw.get('signature', None) else ''
                    self.append(post)

                except Exception:
                    log.warning(traceback.format_exc())
                    raise

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
    tid: 帖子编号
    pid: 回复编号
    like: 点赞数
    dislike: 点踩数
    has_audio: 是否含有音频
    create_time: 10位时间戳，创建时间
    smileys: 表情列表
    user: UserInfo类 发布者信息
    """

    __slots__ = ('_like', '_dislike',
                 'has_audio',
                 '_create_time',
                 'smileys')

    def __init__(self):
        pass

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

    def _init_content(self, content_fragments: list):
        """
        从回复内容的碎片列表中提取有用信息
        _init_content(content_fragments:list)
        """

        texts = []
        self.smileys = []
        self.has_audio = False
        for fragment in content_fragments:
            if fragment['type'] in ['0', '4', '9']:
                texts.append(fragment['text'])
            elif fragment['type'] == '1':
                texts.append(fragment['link'])
                texts.append(' ' + fragment['text'])
            elif fragment['type'] == '2':
                self.smileys.append(fragment['text'])
            elif fragment['type'] == '10':
                self.has_audio = True
        self._text = ''.join(texts)


class Comments(list):
    """
    comment列表

    current_pn: 当前页数
    total_pn: 总页数
    """

    __slots__ = ('_current_pn', '_total_pn')

    def __init__(self, main_json=None):

        if main_json:
            try:
                fid = main_json['forum']['id']
                tid = main_json['thread']['id']
            except:
                log.warning(traceback.format_exc())
                raise

            for comment_raw in main_json['subpost_list']:
                try:
                    comment = Comment()
                    comment.fid = fid
                    comment.tid = tid
                    comment.pid = comment_raw['id']
                    comment._init_content(comment_raw['content'])
                    comment.create_time = comment_raw['time']
                    comment.like = comment_raw['agree']['agree_num']
                    comment.dislike = comment_raw['agree']['disagree_num']
                    comment.user = UserInfo(comment_raw['author'])
                    self.append(comment)

                except:
                    log.warning(traceback.format_exc())
                    raise

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


class At(_BaseContent):
    """
    @信息

    text: 标题文本
    tieba_name: 帖子所在吧
    tid: 帖子编号
    pid: 回复编号
    create_time: 10位时间戳，创建时间
    user: UserInfo类 发布者信息
    """

    __slots__ = ('tieba_name', '_create_time',)

    def __init__(self):
        super().__init__()
        self.tieba_name = ''
        self._create_time = 0

    @property
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, new_create_time):
        self._create_time = int(new_create_time)
