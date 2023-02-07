import sys

from .._classdef import MsgType
from .._core import WsCore
from .._helper import log_exception, log_success
from ..exception import TiebaServerError
from ..get_group_msg import WsMessage
from .protobuf import CommitReceivedPmsgReqIdl_pb2, CommitReceivedPmsgResIdl_pb2

CMD = 205006


def pack_proto(user_id: int, group_id: int, msg_id: int) -> bytes:
    req_proto = CommitReceivedPmsgReqIdl_pb2.CommitReceivedPmsgReqIdl()
    req_proto.data.groupId = group_id
    req_proto.data.toUid = user_id
    req_proto.data.msgType = MsgType.READED
    req_proto.data.msgId = msg_id

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> None:
    res_proto = CommitReceivedPmsgResIdl_pb2.CommitReceivedPmsgResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)


async def request(ws_core: WsCore, message: WsMessage) -> bool:
    user_id = message._user._user_id
    msg_id = message._msg_id
    data = pack_proto(user_id, ws_core.mid_manager.priv_gid, msg_id)

    log_str = f"user_id={user_id} msg_id={msg_id}"
    frame = sys._getframe(1)

    try:
        resq = await ws_core.send(data, CMD)
        parse_body(await resq.read())

    except Exception as err:
        log_exception(frame, err, log_str)
        return False

    log_success(frame, log_str)
    return True
