import dataclasses as dcs
from typing import Dict

from ...exception import TbErrorExt
from .._classdef import TypeMessage


@dcs.dataclass
class TabMap(TbErrorExt):
    """
    分区名到分区id的映射

    Attributes:
        err (Exception | None): 捕获的异常

        map (dict[str, int]): 分区名到分区id的映射
    """

    map: Dict[str, int] = dcs.field(default_factory=dict)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "TabMap":
        map_ = {tab_proto.tab_name: tab_proto.tab_id for tab_proto in data_proto.exact_match.tab_info}
        return TabMap(map_)

    def __getitem__(self, key: str) -> int:
        return self.map[key]
