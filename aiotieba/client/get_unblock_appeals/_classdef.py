from collections.abc import Mapping

from .._classdef import Containers


class Appeal(object):
    """
    申诉请求信息

    Attributes:
        aid (int): 申诉请求id
    """

    __slots__ = ['_aid']

    def _init(self, data_map: Mapping) -> "Appeal":
        self._aid = int(data_map['appeal_id'])
        return self

    def __repr__(self) -> str:
        return str({'aid': self.aid})

    @property
    def aid(self) -> int:
        """
        申诉请求id
        """

        return self._aid


class Appeals(Containers[Appeal]):
    """
    申诉请求列表

    Attributes:
        _objs (list[Appeal]): 申诉请求列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_has_more']

    def _init(self, data_map: Mapping) -> "Appeals":
        self._objs = [Appeal()._init(m) for m in data_map['data'].get('appeal_list', [])]
        self._has_more = data_map['data'].get('has_more', False)
        return self

    def _init_null(self) -> "Appeals":
        self._objs = []
        self._has_more = False
        return self

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more
