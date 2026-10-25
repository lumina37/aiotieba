from __future__ import annotations

from typing import TYPE_CHECKING

from ...exception import TiebaServerError, TiebaValueError
from ._classdef import SendMsgResult
from .protobuf import CommitPersonalMsgReqIdl_pb2, CommitPersonalMsgResIdl_pb2

if TYPE_CHECKING:
    from ...core import WsCore

CMD = 205001


def pack_proto(user_id: int, content: str, local_msg_id: int) -> bytes:
    req_proto = CommitPersonalMsgReqIdl_pb2.CommitPersonalMsgReqIdl()
    req_proto.data.toUid = user_id
    req_proto.data.content = content
    req_proto.data.msgType = 1
    req_proto.data.recordId = local_msg_id

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> SendMsgResult:
    res_proto = CommitPersonalMsgResIdl_pb2.CommitPersonalMsgResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)
    if code := res_proto.data.blockInfo.blockErrno:
        raise TiebaServerError(code, res_proto.data.blockInfo.blockErrmsg)
    if not res_proto.data.msgId:
        raise TiebaValueError("msgId is 0")

    result = SendMsgResult.from_proto(res_proto.data)

    return result


async def request(ws_core: WsCore, user_id: int, content: str) -> SendMsgResult:
    local_msg_id = ws_core.mid_manager.get_local_msg_id(user_id)
    data = pack_proto(user_id, content, local_msg_id)

    resp = await ws_core.send(data, CMD)
    result = parse_body(await resp.read())

    return result
