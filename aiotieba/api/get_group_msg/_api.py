from typing import List

from ...const import POST_VERSION
from ...core import Account, WsCore
from ...exception import TiebaServerError
from ._classdef import WsMsgGroups
from .protobuf import GetGroupMsgReqIdl_pb2, GetGroupMsgResIdl_pb2

CMD = 202003


def pack_proto(account: Account, group_ids: List[int], msg_ids: List[int], get_type: int) -> bytes:
    req_proto = GetGroupMsgReqIdl_pb2.GetGroupMsgReqIdl()
    for group_id, msg_id in zip(group_ids, msg_ids):
        group_proto = req_proto.data.groupMids.add()
        group_proto.groupId = group_id
        group_proto.lastMsgId = msg_id
    req_proto.data.gettype = str(get_type)
    req_proto.cuid = f"{account.cuid}|com.baidu.tieba_mini{POST_VERSION}"

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> WsMsgGroups:
    res_proto = GetGroupMsgResIdl_pb2.GetGroupMsgResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    groups = WsMsgGroups.from_tbdata(data_proto)

    return groups


async def request(ws_core: WsCore, group_ids: List[int], get_type: int) -> WsMsgGroups:
    msg_ids = [ws_core.mid_manager.get_msg_id(gid) for gid in group_ids]
    data = pack_proto(ws_core.account, group_ids, msg_ids, get_type)

    resp = await ws_core.send(data, CMD)
    return parse_body(await resp.read())
