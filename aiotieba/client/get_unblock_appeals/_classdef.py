from typing import Mapping

from .._classdef import Containers


class Appeal(object):
    """
    申诉请求信息

    Attributes:
        user_id (int): 申诉用户id
        portrait (str): 申诉用户portrait
        user_name (str): 申诉用户名
        nick_name (str): 申诉用户昵称

        appeal_id (int): 申诉id
        appeal_reason (str): 申诉理由
        appeal_time (int): 申诉时间

        punish_reason (str): 封禁理由
        punish_time (int): 封禁开始时间
        punish_day (int): 封禁天数
        op_name (str): 操作人用户名
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
        '_nick_name',
        '_appeal_id',
        '_appeal_reason',
        '_appeal_time',
        '_punish_reason',
        '_punish_time',
        '_punish_day',
        '_op_name',
    ]

    def _init(self, data_map: Mapping) -> "Appeal":
        user_map = data_map['user']
        self._user_id = user_map['id']
        if '?' in (portrait := user_map['portrait']):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = user_map['name']
        self._nick_name = user_map['name_show']
        self._appeal_id = int(data_map['appeal_id'])
        self._appeal_reason = data_map['appeal_reason']
        self._appeal_time = int(data_map['appeal_time'])
        self._punish_reason = data_map['punish_reason']
        self._punish_time = int(data_map['punish_start_time'])
        self._punish_day = data_map['punish_day_num']
        self._op_name = data_map['operate_man']
        return self

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'portrait': self._portrait,
                'user_name': self._user_name,
                'nick_name': self._nick_name,
                'appeal_id': self._appeal_id,
                'appeal_reason': self._appeal_reason,
                'punish_reason': self._punish_reason,
                'punish_day': self._punish_day,
                'op_name': self._op_name,
            }
        )

    @property
    def user_id(self) -> int:
        """
        申诉用户id
        """

        return self._user_id

    @property
    def user_name(self) -> str:
        """
        申诉用户名
        """

        return self._user_name

    @property
    def nick_name(self) -> str:
        """
        申诉用户昵称
        """

        return self._nick_name

    @property
    def appeal_id(self) -> int:
        """
        申诉id
        """

        return self._appeal_id

    @property
    def appeal_reason(self) -> str:
        """
        申诉理由
        """

        return self._appeal_reason

    @property
    def appeal_time(self) -> int:
        """
        申诉时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._appeal_time

    @property
    def punish_reason(self) -> str:
        """
        封禁理由
        """

        return self._punish_reason

    @property
    def punish_time(self) -> int:
        """
        封禁开始时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._punish_time

    @property
    def punish_day(self) -> int:
        """
        封禁天数
        """

        return self._punish_day

    @property
    def op_name(self) -> str:
        """
        操作人用户名
        """

        return self._op_name


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
