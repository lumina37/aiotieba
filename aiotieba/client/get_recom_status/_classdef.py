from typing import Mapping


class RecomStatus(object):
    """
    大吧主推荐功能的月度配额状态

    Attributes:
        total_recom_num (int): 本月总推荐配额
        used_recom_num (int): 本月已使用的推荐配额
    """

    __slots__ = [
        '_total_recom_num',
        '_used_recom_num',
    ]

    def _init(self, data_map: Mapping) -> "RecomStatus":
        self._total_recom_num = int(data_map['total_recommend_num'])
        self._used_recom_num = int(data_map['used_recommend_num'])
        return self

    def _init_null(self) -> "RecomStatus":
        self._total_recom_num = 0
        self._used_recom_num = 0
        return self

    def __repr__(self) -> str:
        return str(
            {
                'total_recom_num': self._total_recom_num,
                'used_recom_num': self._used_recom_num,
            }
        )

    @property
    def total_recom_num(self) -> int:
        """
        本月总推荐配额
        """

        return self._total_recom_num

    @property
    def used_recom_num(self) -> int:
        """
        本月已使用的推荐配额
        """

        return self._used_recom_num
