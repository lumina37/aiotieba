from typing import Generic, Iterator, List, SupportsIndex, TypeVar, overload

TypeContainer = TypeVar('TypeContainer')


class Containers(Generic[TypeContainer]):
    """
    内容列表的泛型基类
    约定取内容的通用接口

    Attributes:
        _objs (list[TypeContainer]): 内容列表
    """

    __slots__ = ['_objs']

    def __repr__(self) -> str:
        return str(self._objs)

    def __iter__(self) -> Iterator[TypeContainer]:
        return self._objs.__iter__()

    @overload
    def __getitem__(self, idx: SupportsIndex) -> TypeContainer:
        pass

    @overload
    def __getitem__(self, idx: slice) -> List[TypeContainer]:
        pass

    def __getitem__(self, idx):
        return self._objs.__getitem__(idx)

    def __setitem__(self, idx, val):
        raise NotImplementedError

    def __delitem__(self, idx):
        raise NotImplementedError

    def __len__(self) -> int:
        return self._objs.__len__()

    def __bool__(self) -> bool:
        return bool(self._objs)
