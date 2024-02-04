import dataclasses as dcs

from .._classdef import TypeMessage


@dcs.dataclass
class WsNotify:
    """
    websocket主动推送消息提醒

    Attributes:
        note_type (int): 提醒类别
        group_id (int): 消息组id
        group_type (int): 消息组类别
        msg_id (int): 消息id
        create_time (int): 推送时间 10位时间戳 以秒为单位
    """

    note_type: int = 0
    group_id: int = 0
    group_type: int = 0
    msg_id: int = 0
    create_time: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "WsNotify":
        data_proto = data_proto.data
        note_type = data_proto.type
        group_type = data_proto.groupType
        group_id = data_proto.groupId
        msg_id = data_proto.msgId
        create_time = str(create_time) if (create_time := data_proto.et) else 0
        return WsNotify(note_type, group_id, group_type, msg_id, create_time)
