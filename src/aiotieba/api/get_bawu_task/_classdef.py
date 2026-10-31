from __future__ import annotations

import dataclasses as dcs
from datetime import datetime
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from ...helper import default_datetime

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class BawuTask(TbErrorExt):
    """
    吧主考核信息

    Attributes:
        err (Exception | None): 捕获的异常

        end_dt (datetime): 考核截止时间
    """

    end_dt: datetime = dcs.field(default_factory=default_datetime)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        end_dt = datetime.fromtimestamp(data_map["end_time"])
        return cls(end_dt)
