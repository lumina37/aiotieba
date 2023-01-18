from .._exception import TiebaServerError
from .protobuf import CommitPersonalMsgReqIdl_pb2, CommitPersonalMsgResIdl_pb2


def pack_proto(user_id: int, content: str) -> bytes:
    req_proto = CommitPersonalMsgReqIdl_pb2.CommitPersonalMsgReqIdl()
    req_proto.data.toUid = user_id
    req_proto.data.content = content
    req_proto.data.msgType = 1

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> None:
    res_proto = CommitPersonalMsgResIdl_pb2.CommitPersonalMsgResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)
    if code := res_proto.data.blockInfo.blockErrno:
        raise TiebaServerError(code, res_proto.data.blockInfo.blockErrmsg)
