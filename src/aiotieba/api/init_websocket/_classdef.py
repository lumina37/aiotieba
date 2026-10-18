from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

from .._classdef import UserInfo_ws

if TYPE_CHECKING:
    from .._classdef import TypeMessage


@dcs.dataclass
class WsMsgGroupInfo:
    """
    websocket消息组的相关信息

    Attributes:
        group_id (int): 消息组id
        group_type (int): 消息组类别
        last_msg_id (int): 最新消息的id
    """

    group_id: int = 0
    group_type: int = 0
    last_msg_id: int = 0

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        group_id = data_proto.groupId
        group_type = data_proto.groupType
        last_msg_id = data_proto.lastMsgId
        return cls(group_id, group_type, last_msg_id)


@dcs.dataclass
class InitWsInfo:
    """
    websocket初始化的回包信息

    Attributes:
        groups (list[WsMsgGroupInfo]): 消息组信息列表
        user (UserInfo_ws): 当前账号的基础信息
    """

    groups: list[WsMsgGroupInfo] = dcs.field(default_factory=list)
    user: UserInfo_ws = dcs.field(default_factory=UserInfo_ws)

    @classmethod
    def from_proto(cls, res_proto: TypeMessage) -> Self:
        data_proto = res_proto.data

        groups = [WsMsgGroupInfo.from_proto(group_proto) for group_proto in data_proto.groupInfo]
        user = UserInfo_ws.from_proto(data_proto.userInfo)

        return cls(groups, user)
