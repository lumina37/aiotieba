from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from .._classdef import TypeMessage


@dcs.dataclass
class LevelInfo:
    """
    用户于某贴吧的等级信息

    Attributes:
        user_level (int): 等级数值
        level_name (str): 等级名称
        is_like (bool): 是否已关注

    """

    level_name: str = ""
    user_level: int = 0
    is_like: bool = False

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        user_level = data_proto.user_level
        level_name = data_proto.level_name
        is_like = bool(data_proto.is_like)
        return cls(level_name, user_level, is_like)
