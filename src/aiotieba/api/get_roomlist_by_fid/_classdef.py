from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class RoomList(TbErrorExt):
    """
    某吧的聊天室列表

    Attributes:
        err (Exception | None): 捕获的异常

        room_list (list[dict]): 每个聊天室的json内容
    """

    room_list: list = dcs.field(default_factory=list)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        if not data_map:
            return cls()

        room_list = []
        for x in data_map["list"]:
            room_list.extend(x["room_list"])
        return cls(room_list)
