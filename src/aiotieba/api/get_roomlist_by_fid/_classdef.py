from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class RoomList:
    """
    某吧的聊天室列表

    Attributes:
        room_list (list[dict]): 每个聊天室的json内容
    """

    room_list: list

    @staticmethod
    def from_json(data_map: Mapping) -> Self:  # TODO: 解析json并参数化而不是直接返回
        room_list = []
        for x in data_map["list"]:
            room_list.extend(x["room_list"])
        return RoomList(room_list)
