import abc
from collections.abc import Iterator
from typing import Generic, List, SupportsIndex, TypeVar, overload

from .common import UserInfo


class Container(object):
    """
    基本的内容容器

    Attributes:
        text (str): 文本内容

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id
    """

    __slots__ = [
        '_text',
        '_fname',
        '_fid',
        '_tid',
        '_pid',
        '_user',
        '_author_id',
    ]

    def __init__(self) -> None:
        self._text = None
        self._fname = ''
        self._fid = 0
        self._tid = 0
        self._pid = 0
        self._user = None
        self._author_id = None

    def __repr__(self) -> str:
        return str(
            {
                'tid': self.tid,
                'pid': self.pid,
                'user': self.user.log_name,
                'text': self.text,
            }
        )

    def __eq__(self, obj: "Container") -> bool:
        return self._pid == obj._pid

    def __hash__(self) -> int:
        return self._pid

    @property
    def text(self) -> str:
        """
        文本内容
        """

        if self._text is None:
            raise NotImplementedError
        return self._text

    @property
    def fid(self) -> int:
        """
        所在吧id
        """

        return self._fid

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
        回复id
        """

        return self._pid

    @property
    def user(self) -> UserInfo:
        """
        发布者的用户信息
        """

        if self._user is None:
            self._user = UserInfo()
        return self._user

    @property
    def author_id(self) -> int:
        """
        发布者的user_id
        """

        if not self._author_id:
            self._author_id = self.user.user_id
        return self._author_id


TypeContainer = TypeVar('TypeContainer', bound=Container)


class Containers(Generic[TypeContainer]):
    """
    内容列表的泛型基类
    约定取内容的通用接口

    Attributes:
        objs (list[TypeContainer]): 内容列表
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_objs']

    def __init__(self) -> None:
        self._objs = None

    def __repr__(self) -> str:
        return str(self.objs)

    def __iter__(self) -> Iterator[TypeContainer]:
        return self.objs.__iter__()

    @overload
    def __getitem__(self, idx: SupportsIndex) -> TypeContainer:
        ...

    @overload
    def __getitem__(self, idx: slice) -> List[TypeContainer]:
        ...

    def __getitem__(self, idx):
        return self.objs.__getitem__(idx)

    def __setitem__(self, idx, val):
        raise NotImplementedError

    def __delitem__(self, idx):
        raise NotImplementedError

    def __len__(self) -> int:
        return self.objs.__len__()

    def __bool__(self) -> bool:
        return bool(self.objs)

    @property
    @abc.abstractmethod
    def objs(self) -> List[TypeContainer]:
        """
        内容列表
        """

        ...

    @property
    @abc.abstractmethod
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        ...
