from typing import Mapping, Optional

from .._classdef import Containers


class FollowForum(object):
    """
    吧广场贴吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        level (int): 用户等级
        exp (int): 经验值
    """

    __slots__ = [
        '_fid',
        '_fname',
        '_level',
        '_exp',
    ]

    def __init__(self, data_map: Mapping) -> None:
        self._fid = int(data_map['id'])
        self._fname = data_map['name']
        self._level = int(data_map['level_id'])
        self._exp = int(data_map['cur_score'])

    def __repr__(self) -> str:
        return str(
            {
                'fid': self._fid,
                'fname': self._fname,
                'level': self._level,
                'exp': self._exp,
            }
        )

    def __eq__(self, obj: "FollowForum") -> bool:
        return self._fid == obj._fid

    def __hash__(self) -> int:
        return self._fid

    @property
    def fid(self) -> int:
        """
        贴吧id
        """

        return self._fid

    @property
    def fname(self) -> str:
        """
        贴吧名
        """

        return self._fname

    @property
    def level(self) -> int:
        """
        用户等级
        """

        return self._level

    @property
    def exp(self) -> int:
        """
        经验值
        """

        return self._exp


class FollowForums(Containers[FollowForum]):
    """
    用户关注贴吧列表

    Attributes:
        _objs (list[Forum]): 用户关注贴吧列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_has_more']

    def __init__(self, data_map: Optional[Mapping] = None) -> None:
        if data_map and (forum_list := data_map.get('forum_list', {})):
            forum_dicts = forum_list.get('non-gconforum', [])
            self._objs = [FollowForum(m) for m in forum_dicts]
            forum_dicts = forum_list.get('gconforum', [])
            self._objs += [FollowForum(m) for m in forum_dicts]
            self._has_more = bool(int(data_map['has_more']))
        else:
            self._objs = []
            self._has_more = False

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more
