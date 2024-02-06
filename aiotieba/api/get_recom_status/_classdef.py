import dataclasses as dcs
from typing import Mapping

from ...exception import TbErrorExt


@dcs.dataclass
class RecomStatus(TbErrorExt):
    """
    大吧主推荐功能的月度配额状态

    Attributes:
        err (Exception | None): 捕获的异常

        total_recom_num (int): 本月总推荐配额
        used_recom_num (int): 本月已使用的推荐配额
    """

    total_recom_num: int = 0
    used_recom_num: int = 0

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "RecomStatus":
        total_recom_num = int(data_map['total_recommend_num'])
        used_recom_num = int(data_map['used_recommend_num'])
        return RecomStatus(total_recom_num, used_recom_num)
