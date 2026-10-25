from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from .._classdef import TypeMessage


@dcs.dataclass
class SetMsgReadedResult:
    """
    设置私信已读的返回值

    Attributes:
        read_msg_id (int): 服务端记录的已读位置msg_id
        group_id (int): 私信消息组id
        to_uid (int): 对端user_id
        to_user_type (int): 对端用户类别
    """

    read_msg_id: int = 0
    group_id: int = 0
    to_uid: int = 0
    to_user_type: int = 0

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        read_msg_id = data_proto.readMsgId
        group_id = data_proto.groupId
        to_uid = data_proto.toUid
        to_user_type = data_proto.toUserType
        return cls(read_msg_id, group_id, to_uid, to_user_type)
