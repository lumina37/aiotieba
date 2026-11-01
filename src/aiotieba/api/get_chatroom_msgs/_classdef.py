from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from ...exception import TbErrorExt
from ...helper import parse_json
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class ChatroomMsg:
    """
    吧群消息

    Attributes:
        msg_id (int): 消息id
        msg_key (str): 消息key
        msg_type (int): 消息类型
        user_id (int): 发送者user_id 为0时表示系统消息

        content (dict): 消息内容的原始json字符串解析得到的结构 随消息类型变化

        text (str): 文本消息的正文 非文本消息为空字符串

        create_time (int): 发送时间 10位时间戳 以秒为单位
    """

    msg_id: int = 0
    msg_key: str = ""
    msg_type: int = 0
    user_id: int = 0
    content: dict = dcs.field(default_factory=dict)
    text: str = ""
    create_time: int = 0

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        msg_id = data_map["msgid"]
        msg_key = data_map["msg_key"]
        msg_type = data_map["type"]
        user_id = data_map["from_user"]
        content = parse_json(data_map["content"])

        text = ""
        if "text" in content:
            text_map = parse_json(content["text"])
            if "content_body" in text_map:
                text_map = parse_json(text_map["content_body"])
            if "text" in text_map:
                text = text_map["text"]

        create_time = data_map["create_time"]

        return cls(msg_id, msg_key, msg_type, user_id, content, text, create_time)


@dcs.dataclass
class ChatroomMsgs(TbErrorExt, Containers[ChatroomMsg]):
    """
    吧群消息列表

    Attributes:
        objs (list[ChatroomMsg]): 吧群消息列表
        err (Exception | None): 捕获的异常
    """

    @classmethod
    def from_json(cls, data_map: Mapping) -> Self:
        objs = [ChatroomMsg.from_json(m) for m in data_map["messages"]]
        return cls(objs)
