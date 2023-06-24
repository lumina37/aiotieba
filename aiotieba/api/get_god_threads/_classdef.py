from typing import Mapping, Optional

from .._classdef import Containers


class GodThread(object):
    """
    精选神帖

    Attributes:
        tid (int): 主题帖id
    """

    __slots__ = ['_tid']

    def __init__(self, data_map: Mapping) -> None:
        self._tid = data_map['tid']

    def __repr__(self) -> str:
        return str({'tid': self.tid})

    @property
    def tid(self) -> int:
        """
        主题帖id
        """

        return self._tid


class GodThreads(Containers[GodThread]):
    """
    精选神帖列表

    Attributes:
        _objs (list[Recover]): 待恢复帖子列表

        page (Page_recover): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_has_more']

    def __init__(self, data_map: Optional[Mapping] = None) -> None:
        if data_map:
            self._has_more = data_map['data']['has_more']
            self._objs = [GodThread(t) for t in data_map['data']['thread_list']]
        else:
            self._objs = []

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more
