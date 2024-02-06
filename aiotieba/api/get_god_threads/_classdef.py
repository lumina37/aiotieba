import dataclasses as dcs
from typing import Mapping

from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class GodThread:
    """
    精选神帖

    Attributes:
        tid (int): 主题帖id
    """

    tid: int = 0

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "GodThread":
        tid = data_map['tid']
        return GodThread(tid)


@dcs.dataclass
class GodThreads(TbErrorExt, Containers[GodThread]):
    """
    精选神帖列表

    Attributes:
        objs (list[GodThread]): 精选神帖列表
        err (Exception | None): 捕获的异常

        has_more (bool): 是否还有下一页
    """

    has_more: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "GodThreads":
        objs = [GodThread.from_tbdata(t) for t in data_map['data']['thread_list']]
        has_more = data_map['data']['has_more']
        return GodThreads(objs, has_more)
