import dataclasses as dcs

from .._classdef import TypeMessage


@dcs.dataclass
class LevelInfo:
    """
    用户于某贴吧的等级信息

    Attributes:
        user_level (int): 等级数值
        level_name (str): 等级名称
        is_like (int): 是否已关注

    """

    level_name: str = ""
    user_level: int = 0
    is_like: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "LevelInfo":
        user_level = data_proto.user_level
        level_name = data_proto.level_name
        is_like = data_proto.is_like
        return LevelInfo(level_name, user_level, is_like)
