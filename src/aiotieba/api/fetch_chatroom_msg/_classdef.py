from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from ...helper import parse_json

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class ChatroomMessage:
    """
    吧群消息

    Attributes:
        msg_id (int): 消息id
        msg_type (int): 消息类型
        user_id (int): 发送者user_id 为0时表示系统消息
        create_time (int): 发送时间 10位时间戳 以秒为单位
        content (dict): 消息内容 结构随消息类型变化
    """

    msg_id: int = 0
    msg_type: int = 0
    user_id: int = 0
    create_time: int = 0
    content: dict = dcs.field(default_factory=dict)

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        msg_id = data_map["msgid"]
        msg_type = data_map["type"]
        user_id = data_map["from_user"]
        create_time = data_map["create_time"]
        content = parse_json(parse_json(data_map["content"])["text"])

        return cls(msg_id, msg_type, user_id, create_time, content)
