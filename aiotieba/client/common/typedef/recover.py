__all__ = [
    'Recover',
    'Recovers',
]


from typing import List, Optional

import bs4

from .container import Containers


class Recover(object):
    """
    待恢复帖子信息

    Attributes:
        tid (int): 所在主题帖id
        pid (int): 回复id
        is_hide (bool): 是否为屏蔽
    """

    __slots__ = [
        '_tid',
        '_pid',
        '_is_hide',
    ]

    def __init__(self, _raw_data: Optional[bs4.element.Tag] = None) -> None:

        if _raw_data:
            self._tid = int(_raw_data['attr-tid'])
            self._pid = int(_raw_data['attr-pid'])
            self._is_hide = bool(int(_raw_data['attr-isfrsmask']))

        else:
            self._tid = 0
            self._pid = 0
            self._is_hide = False

    def __repr__(self) -> str:
        return str(
            {
                'tid': self.tid,
                'pid': self.pid,
                'is_hide': self.is_hide,
            }
        )

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
    def is_hide(self) -> bool:
        """
        是否为屏蔽
        """

        return self._is_hide


class Recovers(Containers[Recover]):
    """
    待恢复帖子列表

    Attributes:
        objs (list[Recover]): 待恢复帖子列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_has_more']

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Recovers, self).__init__()

        if _raw_data:
            self._objs = _raw_data['data']['content']
            self._has_more = _raw_data['data']['page']['have_next']

        else:
            self._has_more = False

    @property
    def objs(self) -> List[Recover]:
        """
        待恢复帖子列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:
                soup = bs4.BeautifulSoup(self._objs, 'lxml')
                self._objs = [Recover(_tag) for _tag in soup('a', class_='recover_list_item_btn')]

            else:
                self._objs = []

        return self._objs

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more
