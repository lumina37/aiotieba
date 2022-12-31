__all__ = [
    'UserPost',
    'UserPosts',
]

from typing import List, Optional

from .common import TypeMessage
from .container import Container, Containers
from .frags import Fragments


class UserPost(Container):
    """
    用户历史回复信息

    Attributes:
        text (str): 文本内容
        contents (Fragments): 正文内容碎片列表

        fid (int): 所在吧id
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id

        create_time (int): 创建时间
    """

    __slots__ = [
        '_contents',
        '_create_time',
    ]

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
        super(UserPost, self).__init__()

        if _raw_data:
            self._contents = _raw_data.post_content
            self._pid = _raw_data.post_id
            self._create_time = _raw_data.create_time

        else:
            self._contents = None
            self._create_time = 0

    def __eq__(self, obj: "UserPost") -> bool:
        return super(UserPost, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(UserPost, self).__hash__()

    @property
    def text(self) -> str:
        """
        文本内容
        """

        if self._text is None:
            self._text = self.contents.text
        return self._text

    @property
    def contents(self) -> Fragments:
        """
        正文内容碎片列表
        """

        if not isinstance(self._contents, Fragments):
            if self._contents is not None:
                self._contents = Fragments(self._contents)
            else:
                self._contents = Fragments()

        return self._contents

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳
        """

        return self._create_time


class UserPosts(Containers[UserPost]):
    """
    用户历史回复信息列表

    Attributes:
        objs (list[UserPost]): 用户历史回复信息列表
        fid (int): 所在吧id
        tid (int): 所在主题帖id
    """

    __slots__ = [
        '_fid',
        '_tid',
    ]

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
        super(UserPosts, self).__init__()

        if _raw_data:
            self._objs = _raw_data.content
            self._fid = _raw_data.forum_id
            self._tid = _raw_data.thread_id

        else:
            self._fid = 0
            self._tid = 0

    @property
    def objs(self) -> List[UserPost]:
        """
        用户历史回复信息列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:

                self._objs = [UserPost(_proto) for _proto in self._objs]

                for post in self._objs:
                    post._fid = self.fid
                    post._tid = self.tid

            else:
                self._objs = []

        return self._objs

    @property
    def fid(self) -> int:
        """
        所在吧id
        """

        return self._fid

    @property
    def tid(self) -> int:
        """
        所在主题帖id
        """

        return self._tid
