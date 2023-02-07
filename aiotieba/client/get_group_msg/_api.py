import sys
from typing import List

from .._core import TbCore, WsCore
from .._helper import log_exception
from ..exception import TiebaServerError
from ._classdef import WsMsgGroup
from .protobuf import GetGroupMsgReqIdl_pb2, GetGroupMsgResIdl_pb2

CMD = 202003


def pack_proto(core: TbCore, group_ids: List[int], msg_ids: List[int], get_type: int) -> bytes:
    req_proto = GetGroupMsgReqIdl_pb2.GetGroupMsgReqIdl()
    for group_id, msg_id in zip(group_ids, msg_ids):
        group_proto = req_proto.data.groupMids.add()
        group_proto.groupId = group_id
        group_proto.lastMsgId = msg_id
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


async def request(ws_core: WsCore, group_ids: List[int], get_type: int) -> List[WsMsgGroup]:

    msg_ids = [ws_core.mid_manager.get_msg_id(gid) for gid in group_ids]
    data = pack_proto(ws_core.core, group_ids, msg_ids, get_type)

    try:
        resq = await ws_core.send(data, CMD)
        groups = parse_body(await resq.read())

    except Exception as err:
        log_exception(sys._getframe(1), err, f"group_ids={group_ids}")
        groups = []

    return groups
