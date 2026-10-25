from __future__ import annotations

import dataclasses as dcs
from typing import Self

from ...exception import TbErrorExt
from .._classdef import Containers, TypeMessage, UserInfo_ws


@dcs.dataclass
class WsMessage:
    """
    websocket消息

    Attributes:
        msg_id (int): 消息id
        msg_type (int): 消息类型
        text (str): 文本内容
        user (UserInfo_ws): 用户信息
        create_time (int): 发送时间 10位时间戳 以秒为单位
    """

    msg_id: int = 0
    msg_type: int = 0
    text: str = ""
    user: UserInfo_ws = dcs.field(default_factory=UserInfo_ws)
    create_time: int = 0

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        msg_id = data_proto.msgId
        msg_type = data_proto.msgType
        text = data_proto.content
        user = UserInfo_ws.from_proto(data_proto.userInfo)
        create_time = data_proto.createTime
        return cls(msg_id, msg_type, text, user, create_time)


@dcs.dataclass
class WsMsgGroup:
    """
    websocket消息组

    Attributes:
        group_id (int): 消息组id
        group_type (int): 消息组类别
        messages (list[WsMessage]): 消息列表
    """

    group_id: int = 0
    group_type: int = 0
    messages: list[WsMessage] = dcs.field(default_factory=list)

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        group_id = data_proto.groupInfo.groupId
        group_type = data_proto.groupInfo.groupType
        messages = [WsMessage.from_proto(p) for p in data_proto.msgList]
        return cls(group_id, group_type, messages)


@dcs.dataclass
class WsMsgGroups(TbErrorExt, Containers[WsMsgGroup]):
    """
    websocket消息组列表

    Attributes:
        objs (list[WsMsgGroup]): websocket消息组列表
        err (Exception | None): 捕获的异常
    """

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        objs = [WsMsgGroup.from_proto(p) for p in data_proto.groupInfo if p.groupInfo.groupId]
        return cls(objs)
