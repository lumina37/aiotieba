__all__ = [
    'At',
    'Ats',
]

from typing import List, Optional

from google.protobuf.json_format import ParseDict

from ..protobuf import Page_pb2, User_pb2
from .common import Page, UserInfo
from .container import Container, Containers


class At(Container):
    """
    @信息

    Attributes:
        text (str): 文本内容

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id

        is_floor (bool): 是否楼中楼
        is_thread (bool): 是否主题帖

        create_time (int): 创建时间
    """

    __slots__ = [
        '_is_floor',
        '_is_thread',
        '_create_time',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(At, self).__init__()

        if _raw_data:
            self._text = _raw_data['content']

            self._fname = _raw_data['fname']
            self._tid = int(_raw_data['thread_id'])
            self._pid = int(_raw_data['post_id'])
            self._user = _raw_data['replyer']

            self._is_floor = bool(int(_raw_data['is_floor']))
            self._is_thread = bool(int(_raw_data['is_first_post']))
            self._create_time = int(_raw_data['time'])

        else:
            self._text = ''

            self._is_floor = False
            self._is_thread = False
            self._create_time = 0

    def __eq__(self, obj: "At") -> bool:
        return super(At, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(At, self).__hash__()

    @property
    def user(self) -> UserInfo:
        """
        发布者的用户信息
        """

        if not isinstance(self._user, UserInfo):
            if self._user is not None:
                user_proto = ParseDict(self._user, User_pb2.User(), ignore_unknown_fields=True)
                self._user = UserInfo(_raw_data=user_proto) if user_proto.id else UserInfo()
            else:
                self._user = UserInfo()

        return self._user

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
            10位时间戳
        """

        return self._create_time


class Ats(Containers[At]):
    """
    @信息列表

    Attributes:
        objs (list[At]): @信息列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Ats, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data.get('at_list', None)
            self._page = _raw_data['page']

        else:
            self._raw_objs = None
            self._page = None

    @property
    def objs(self) -> List[At]:
        """
        @信息列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [At(_dict) for _dict in self._raw_objs]
                self._raw_objs = None
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
                page_proto = ParseDict(self._page, Page_pb2.Page(), ignore_unknown_fields=True)
                self._page = Page(page_proto)
            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more
