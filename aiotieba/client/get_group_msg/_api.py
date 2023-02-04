from typing import List

from .._core import TbCore
from .._exception import TiebaServerError
from ..push_notify import WsNotify
from ._classdef import WsMsgGroup
from .protobuf import GetGroupMsgReqIdl_pb2, GetGroupMsgResIdl_pb2

CMD = 202003


def pack_proto(core: TbCore, notifies: List[WsNotify], get_type: int) -> bytes:
    req_proto = GetGroupMsgReqIdl_pb2.GetGroupMsgReqIdl()
    req_proto.data.width = 720
    req_proto.data.height = 1280
    req_proto.data.smallWidth = 240
    req_proto.data.smallHeight = 240
    for notify in notifies:
        group_proto = req_proto.data.groupMids.add()
        group_proto.groupId = notify._group_id
        group_proto.lastMsgId = notify._last_msg_id
    req_proto.data.gettype = str(get_type)
    req_proto.cuid = f"{core.cuid}|com.baidu.tieba_mini{core.post_version}"

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> List[WsMsgGroup]:
    res_proto = GetGroupMsgResIdl_pb2.GetGroupMsgResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    groups = [WsMsgGroup()._init(p) for p in res_proto.data.groupInfo]

    return groups
