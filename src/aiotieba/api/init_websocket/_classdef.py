import dataclasses as dcs

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

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "WsMsgGroupInfo":
        group_id = data_proto.groupId
        group_type = data_proto.groupType
        last_msg_id = data_proto.lastMsgId
        return WsMsgGroupInfo(group_id, group_type, last_msg_id)
