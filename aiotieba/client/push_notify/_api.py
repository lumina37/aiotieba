from ..get_group_msg import MsgGroup
from .protobuf import PushNotifyResIdl_pb2

CMD = 202006


def parse_body(body: bytes) -> MsgGroup:
    res_proto = PushNotifyResIdl_pb2.PushNotifyResIdl()
    res_proto.ParseFromString(body)

    group_proto = res_proto.multiMsg[0].data
    group = MsgGroup(group_proto.groupId, group_proto.msgId)

    return group
