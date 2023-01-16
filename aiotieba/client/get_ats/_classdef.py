from typing import Mapping

from .._classdef import Containers


class Page_at(object):
    """
    页信息

    Attributes:
        current_page (int): 当前页码

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = [
        '_current_page',
        '_has_more',
        '_has_prev',
    ]

    def _init(self, data_map: Mapping) -> "Page_at":
        self._current_page = int(data_map['current_page'])
        self._has_more = bool(int(data_map['has_more']))
        self._has_prev = bool(int(data_map['has_prev']))
        return self

    def _init_null(self) -> "Page_at":
        self._current_page = 0
        self._has_more = False
        self._has_prev = False
        return self

    def __repr__(self) -> str:
        return str(
            {
                'current_page': self._current_page,
                'has_more': self._has_more,
                'has_prev': self._has_prev,
            }
        )

    @property
    def current_page(self) -> int:
        """
        当前页码
        """

        return self._current_page

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


class UserInfo_at(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

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
        '_priv_like',
        '_priv_reply',
    ]

    def _init(self, data_map: Mapping) -> "UserInfo_at":
        self._user_id = int(data_map['id'])
        if '?' in (portrait := data_map['portrait']):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_map['name']
        self._nick_name_new = data_map['name_show']
        if priv_sets := data_map['priv_sets']:
            self._priv_like = int(priv_sets.get('like', 1))
            self._priv_reply = int(priv_sets.get('reply', 1))
        else:
            self._priv_like = 1
            self._priv_reply = 1
        return self

    def _init_null(self) -> "UserInfo_at":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
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
                'priv_like': self._priv_like,
                'priv_reply': self._priv_reply,
            }
        )

    def __eq__(self, obj: "UserInfo_at") -> bool:
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


class At(object):
    """
    @信息

    Attributes:
        text (str): 文本内容

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo_at): 发布者的用户信息
        author_id (int): 发布者的user_id

        is_floor (bool): 是否楼中楼
        is_thread (bool): 是否主题帖

        create_time (int): 创建时间
    """

    __slots__ = [
        '_text',
        '_fname',
        '_tid',
        '_pid',
        '_user',
        '_author_id',
        '_is_floor',
        '_is_thread',
        '_create_time',
    ]

    def _init(self, data_map: Mapping) -> "At":
        self._text = data_map['content']
        self._fname = data_map['fname']
        self._tid = int(data_map['thread_id'])
        self._pid = int(data_map['post_id'])
        self._user = UserInfo_at()._init(data_map['replyer'])
        self._author_id = self._user._user_id
        self._is_floor = bool(int(data_map['is_floor']))
        self._is_thread = bool(int(data_map['is_first_post']))
        self._create_time = int(data_map['time'])
        return self

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'pid': self._pid,
                'user': self._user.log_name,
                'text': self._text,
                'is_floor': self._is_floor,
                'is_thread': self._is_thread,
            }
        )

    def __eq__(self, obj: "At") -> bool:
        return self._pid == obj._pid

    def __hash__(self) -> int:
        return self._pid

    @property
    def text(self) -> str:
        """
        文本内容
        """

        return self._text

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
        所在主题帖id
        """

        return self._pid

    @property
    def user(self) -> UserInfo_at:
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
    def is_floor(self) -> bool:
        """
        是否楼中楼
        """

        return self._is_floor

    @property
    def is_thread(self) -> bool:
        """
        是否主题帖
        """

        return self._is_thread

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._create_time


class Ats(Containers[At]):
    """
    @信息列表

    Attributes:
        _objs (list[At]): @信息列表

        page (Page_at): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def _init(self, data_map: Mapping) -> "Ats":
        self._objs = [At()._init(m) for m in data_map.get('at_list', [])]
        self._page = Page_at()._init(data_map['page'])
        return self

    def _init_null(self) -> "Ats":
        self._objs = []
        self._page = Page_at()._init_null()
        return self

    @property
    def page(self) -> Page_at:
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
