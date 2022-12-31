__all__ = [
    'Appeal',
    'Appeals',
]

from typing import List, Optional

from .container import Containers


class Appeal(object):
    """
    申诉请求信息

    Attributes:
        aid (int): 申诉请求id
    """

    __slots__ = ['_aid']

    def __init__(self, _raw_data: Optional[dict] = None) -> None:

        if _raw_data:
            self._aid = int(_raw_data['appeal_id'])
        else:
            self._aid = 0

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
        objs (list[Appeal]): 申诉请求列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_has_more',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Appeals, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data['data'].get('appeal_list', [])
            self._has_more = _raw_data['data'].get('has_more', False)

        else:
            self._raw_objs = None
            self._has_more = False

    @property
    def objs(self) -> List[Appeal]:
        """
        申诉请求列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [Appeal(_dict) for _dict in self._raw_objs]
                self._raw_objs = None
            else:
                self._objs = []

        return self._objs

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more
