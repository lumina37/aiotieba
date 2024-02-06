import dataclasses as dcs
from typing import List

from ...exception import TbErrorExt
from .._classdef import Containers, TypeMessage


@dcs.dataclass
class UserInfo_ws:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名

        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_ws":
        user_id = data_proto.userId
        portrait = data_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.userName
        return UserInfo_ws(user_id, portrait, user_name)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_ws") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def log_name(self) -> str:
        return str(self)


@dcs.dataclass
class WsMessage:
    """
    websocket消息

    Attributes:
        msg_id (int): 消息id
        msg_type (str): 消息类型
        text (str): 文本内容
        user (UserInfo_ws): 文本内容
        create_time (int): 发送时间 10位时间戳 以秒为单位
    """

    msg_id: int = 0
    msg_type: int = 0
    text: str = ""
    user: UserInfo_ws = dcs.field(default_factory=UserInfo_ws)
    create_time: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> None:
        msg_id = data_proto.msgId
        msg_type = data_proto.msgType
        text = data_proto.content
        user = UserInfo_ws.from_tbdata(data_proto.userInfo)
        create_time = data_proto.createTime
        return WsMessage(msg_id, msg_type, text, user, create_time)


@dcs.dataclass
class WsMsgGroup:
    """
    websocket消息组

    Attributes:
        group_id (str): 消息组id
        group_type (int): 消息组类别
        messages (list[WsMessage]): 消息列表
    """

    group_id: int = 0
    group_type: int = 0
    messages: List[WsMessage] = dcs.field(default_factory=list)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "WsMsgGroup":
        group_id = data_proto.groupInfo.groupId
        group_type = data_proto.groupInfo.groupType
        messages = [WsMessage.from_tbdata(p) for p in data_proto.msgList]
        return WsMsgGroup(group_id, group_type, messages)


@dcs.dataclass
class WsMsgGroups(TbErrorExt, Containers[WsMsgGroup]):
    """
    websocket消息组列表

    Attributes:
        objs (list[WsMsgGroup]): websocket消息组列表
        err (Exception | None): 捕获的异常
    """

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "WsMsgGroups":
        objs = [WsMsgGroup.from_tbdata(p) for p in data_proto.groupInfo]
        return WsMsgGroups(objs)
