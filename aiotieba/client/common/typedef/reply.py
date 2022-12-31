__all__ = [
    'Reply',
    'Replys',
]

from typing import List, Optional

from .common import Page, TypeMessage, UserInfo
from .container import Container, Containers


class Reply(Container):
    """
    回复信息
    Attributes:
        text (str): 文本内容

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id
        post_pid (int): 楼层pid
        post_user (UserInfo): 楼层用户信息
        thread_user (UserInfo): 楼主用户信息

        is_floor (bool): 是否楼中楼
        create_time (int): 创建时间
    """

    __slots__ = [
        '_post_pid',
        '_post_user',
        '_thread_user',
        '_is_floor',
        '_create_time',
    ]

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
        super(Reply, self).__init__()

        if _raw_data:
            self._text = _raw_data.content

            self._fname = _raw_data.fname
            self._tid = _raw_data.thread_id
            self._pid = _raw_data.post_id
            self._user = _raw_data.replyer
            self._post_pid = _raw_data.quote_pid
            self._post_user = _raw_data.quote_user
            self._thread_user = _raw_data.thread_author_user

            self._is_floor = bool(_raw_data.is_floor)
            self._create_time = _raw_data.time

        else:
            self._text = ''

            self._post_pid = 0
            self._post_user = None
            self._thread_user = None

            self._is_floor = False
            self._create_time = 0

    def __eq__(self, obj: "Reply") -> bool:
        return super(Reply, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(Reply, self).__hash__()

    @property
    def text(self) -> str:
        """
        文本内容
        """

        return self._text

    @property
    def user(self) -> UserInfo:
        """
        发布者的用户信息
        """

        if not isinstance(self._user, UserInfo):
            if self._user is not None:
                self._user = UserInfo(_raw_data=self._user) if self._user.id else UserInfo()
            else:
                self._user = UserInfo()

        return self._user

    @property
    def post_pid(self) -> int:
        """
        楼层pid
        """

        return self._post_pid

    @property
    def post_user(self) -> UserInfo:
        """
        楼层用户信息
        """

        if not isinstance(self._post_user, UserInfo):
            if self._post_user is not None:
                self._post_user = UserInfo(_raw_data=self._post_user) if self._post_user.id else UserInfo()
            else:
                self._post_user = UserInfo()

        return self._post_user

    @property
    def thread_user(self) -> UserInfo:
        """
        楼主用户信息
        """

        if not isinstance(self._thread_user, UserInfo):
            if self._thread_user is not None:
                self._thread_user = UserInfo(_raw_data=self._thread_user) if self._thread_user.id else UserInfo()
            else:
                self._thread_user = UserInfo()

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
            10位时间戳
        """

        return self._create_time


class Replys(Containers[Reply]):
    """
    收到回复列表

    Attributes:
        objs (list[Reply]): 收到回复列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
        super(Replys, self).__init__()

        if _raw_data:
            self._objs = _raw_data.reply_list
            self._page = _raw_data.page

        else:
            self._page = None

    @property
    def objs(self) -> List[Reply]:
        """
        收到回复列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:
                self._objs = [Reply(_proto) for _proto in self._objs]
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                self._page = Page(self._page)
            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more
