from .._classdef import Containers, TypeMessage


class UserInfo_reply(object):
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

    def _init(self, data_proto: TypeMessage) -> "UserInfo_reply":
        self._user_id = data_proto.id
        if '?' in (portrait := data_proto.portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.name
        self._nick_name_new = data_proto.name_show
        self._priv_like = priv_like if (priv_like := data_proto.priv_sets.like) else 1
        self._priv_reply = priv_reply if (priv_reply := data_proto.priv_sets.reply) else 1
        return self

    def _init_null(self) -> "UserInfo_reply":
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

    def __eq__(self, obj: "UserInfo_reply") -> bool:
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


class UserInfo_reply_p(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_user_id',
        '_user_name',
        '_nick_name_new',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_reply_p":
        self._user_id = data_proto.id
        self._user_name = data_proto.name
        self._nick_name_new = data_proto.name_show
        return self

    def _init_null(self) -> "UserInfo_reply_p":
        self._user_id = 0
        self._user_name = ''
        self._nick_name_new = ''
        return self

    def __str__(self) -> str:
        return self._user_name or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'user_name': self._user_name,
                'show_name': self.show_name,
            }
        )

    def __eq__(self, obj: "UserInfo_reply_p") -> bool:
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
        else:
            return f"{self._nick_name_new}/{self._user_id}"


class UserInfo_reply_t(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_nick_name_new',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_reply_t":
        self._user_id = data_proto.id
        self._portrait = data_proto.portrait
        self._nick_name_new = data_proto.name_show
        return self

    def _init_null(self) -> "UserInfo_reply_t":
        self._user_id = 0
        self._portrait = ''
        self._nick_name_new = ''
        return self

    def __str__(self) -> str:
        return self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'portrait': self._portrait,
                'show_name': self._nick_name_new,
            }
        )

    def __eq__(self, obj: "UserInfo_reply_t") -> bool:
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

        return self._nick_name_new

    @property
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        if self._portrait:
            return f"{self._nick_name_new}/{self._portrait}"
        else:
            return str(self._user_id)


class Reply(object):
    """
    回复信息
    Attributes:
        text (str): 文本内容

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        ppid (int): 所在楼层pid
        pid (int): 回复id
        user (UserInfo_reply): 发布者的用户信息
        author_id (int): 发布者的user_id
        post_user (UserInfo_reply_p): 楼层用户信息
        thread_user (UserInfo_reply_t): 楼主用户信息

        is_floor (bool): 是否楼中楼
        create_time (int): 创建时间
    """

    __slots__ = [
        '_text',
        '_fname',
        '_tid',
        '_ppid',
        '_pid',
        '_user',
        '_author_id',
        '_post_user',
        '_thread_user',
        '_is_floor',
        '_create_time',
    ]

    def _init(self, data_proto: TypeMessage) -> "Reply":
        self._text = data_proto.content
        self._fname = data_proto.fname
        self._tid = data_proto.thread_id
        self._ppid = data_proto.quote_pid
        self._pid = data_proto.post_id
        self._user = UserInfo_reply()._init(data_proto.replyer)
        self._author_id = self._user._user_id
        self._post_user = UserInfo_reply_p()._init(data_proto.quote_user)
        self._thread_user = UserInfo_reply_t()._init(data_proto.thread_author_user)
        self._is_floor = bool(data_proto.is_floor)
        self._create_time = data_proto.time
        return self

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'pid': self._pid,
                'user': self._user.log_name,
                'text': self.text,
                'post_user': self._post_user.log_name,
                'thread_user': self._thread_user.log_name,
                'is_floor': self._is_floor,
            }
        )

    def __eq__(self, obj: "Reply") -> bool:
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
    def ppid(self) -> int:
        """
        所在楼层pid
        """

        return self._ppid

    @property
    def pid(self) -> int:
        """
        回复id
        """

        return self._pid

    @property
    def user(self) -> UserInfo_reply:
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
    def post_user(self) -> UserInfo_reply_p:
        """
        楼层用户信息
        """

        return self._post_user

    @property
    def thread_user(self) -> UserInfo_reply_t:
        """
        楼主用户信息
        """

        return self._thread_user

    @property
    def is_floor(self) -> bool:
        """
        是否楼中楼
        """

        return self._is_floor

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._create_time


class Page_reply(object):
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

    def _init(self, data_proto: TypeMessage) -> "Page_reply":
        self._current_page = data_proto.current_page
        self._has_more = bool(data_proto.has_more)
        self._has_prev = bool(data_proto.has_prev)
        return self

    def _init_null(self) -> "Page_reply":
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


class Replys(Containers[Reply]):
    """
    收到回复列表

    Attributes:
        objs (list[Reply]): 收到回复列表

        page (Page_reply): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def _init(self, data_proto: TypeMessage) -> "Replys":
        self._objs = [Reply()._init(p) for p in data_proto.reply_list]
        self._page = Page_reply()._init(data_proto.page)
        return self

    def _init_null(self) -> "Replys":
        self._objs = []
        self._page = Page_reply()._init_null()
        return self

    @property
    def page(self) -> Page_reply:
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
