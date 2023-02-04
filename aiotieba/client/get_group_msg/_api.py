from typing import List

from .._core import TbCore
from .._exception import TiebaServerError
from ._classdef import MsgGroup
from .protobuf import GetGroupMsgReqIdl_pb2, GetGroupMsgResIdl_pb2

CMD = 202003


def pack_proto(core: TbCore, groups: List[MsgGroup], get_type: int) -> bytes:
    req_proto = GetGroupMsgReqIdl_pb2.GetGroupMsgReqIdl()
    for group in groups:
        group_proto = req_proto.data.groupMids.add()
        group_proto.groupId = group._group_type
        group_proto.lastMsgId = group._last_msg_id
    req_proto.data.gettype = str(get_type)
    req_proto.cuid = f"{core.cuid}|com.baidu.tieba_mini{core.post_version}"

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> None:
    res_proto = GetGroupMsgResIdl_pb2.GetGroupMsgResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)
