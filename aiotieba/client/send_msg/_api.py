import sys

from .._core import WsCore
from .._helper import log_exception, log_success
from ..exception import TiebaServerError
from .protobuf import CommitPersonalMsgReqIdl_pb2, CommitPersonalMsgResIdl_pb2

CMD = 205001


def pack_proto(user_id: int, content: str, record_id: int) -> bytes:
    req_proto = CommitPersonalMsgReqIdl_pb2.CommitPersonalMsgReqIdl()
    req_proto.data.toUid = user_id
    req_proto.data.content = content
    req_proto.data.msgType = 1
    req_proto.data.recordId = record_id

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> int:
    res_proto = CommitPersonalMsgResIdl_pb2.CommitPersonalMsgResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)
    if code := res_proto.data.blockInfo.blockErrno:
        raise TiebaServerError(code, res_proto.data.blockInfo.blockErrmsg)

    msg_id = res_proto.data.msgId
    return msg_id


async def request(ws_core: WsCore, user_id: int, content: str) -> int:
    data = pack_proto(user_id, content, ws_core.mid_manager.get_record_id())

    log_str = f"user_id={user_id}"
    frame = sys._getframe(1)

    try:
        resq = await ws_core.send(data, CMD)
        msg_id = parse_body(await resq.read())

    except Exception as err:
        log_exception(frame, err, log_str)
        msg_id = 0

    log_success(frame, log_str)
    return msg_id
