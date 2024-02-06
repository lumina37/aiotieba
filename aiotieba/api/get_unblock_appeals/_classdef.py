import dataclasses as dcs
from typing import Mapping

from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class Appeal:
    """
    申诉请求信息

    Attributes:
        user_id (int): 申诉用户id
        portrait (str): 申诉用户portrait
        user_name (str): 申诉用户名
        nick_name (str): 申诉用户昵称

        appeal_id (int): 申诉id
        appeal_reason (str): 申诉理由
        appeal_time (int): 申诉时间 10位时间戳 以秒为单位

        punish_reason (str): 封禁理由
        punish_time (int): 封禁开始时间 10位时间戳 以秒为单位
        punish_day (int): 封禁天数
        op_name (str): 操作人用户名
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name: str = ''

    appeal_id: int = 0
    appeal_reason: str = ''
    appeal_time: int = 0

    punish_reason: str = ''
    punish_time: int = 0
    punish_day: int = 0
    op_name: str = ''

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Appeal":
        user_map = data_map['user']
        user_id = user_map['id']
        portrait = user_map['portrait']
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = user_map['name']
        nick_name = user_map['name_show']
        appeal_id = int(data_map['appeal_id'])
        appeal_reason = data_map['appeal_reason']
        appeal_time = int(data_map['appeal_time'])
        punish_reason = data_map['punish_reason']
        punish_time = int(data_map['punish_start_time'])
        punish_day = data_map['punish_day_num']
        op_name = data_map['operate_man']
        return Appeal(
            user_id,
            portrait,
            user_name,
            nick_name,
            appeal_id,
            appeal_reason,
            appeal_time,
            punish_reason,
            punish_time,
            punish_day,
            op_name,
        )


@dcs.dataclass
class Appeals(TbErrorExt, Containers[Appeal]):
    """
    申诉请求列表

    Attributes:
        objs (list[Appeal]): 申诉请求列表
        err (Exception | None): 捕获的异常

        has_more (bool): 是否还有下一页
    """

    has_more: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Appeals":
        objs = [Appeal.from_tbdata(m) for m in data_map['data'].get('appeal_list', [])]
        has_more = data_map['data'].get('has_more', False)
        return Appeals(objs, has_more)
