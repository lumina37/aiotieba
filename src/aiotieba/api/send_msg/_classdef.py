from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from .._classdef import TypeMessage


@dcs.dataclass
class SendMsgResult:
    """
    发送私信的返回值

    Attributes:
        group_id (int): 私信消息组id
        local_msg_id (int): 本端消息id 由服务端回显
        to_uid (int): 接收方user_id
        to_user_type (int): 接收方用户类别
    """

    group_id: int = 0
    local_msg_id: int = 0
    to_uid: int = 0
    to_user_type: int = 0

    @classmethod
    def from_proto(cls, data_proto: TypeMessage) -> Self:
        group_id = data_proto.groupId
        local_msg_id = data_proto.recordId
        to_uid = data_proto.toUid
        to_user_type = data_proto.toUserType
        return cls(group_id, local_msg_id, to_uid, to_user_type)
