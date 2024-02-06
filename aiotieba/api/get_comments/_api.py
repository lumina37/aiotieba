import yarl

from ...const import APP_BASE_HOST, APP_INSECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore, WsCore
from ...exception import TiebaServerError
from ._classdef import Comments
from .protobuf import PbFloorReqIdl_pb2, PbFloorResIdl_pb2

CMD = 302002


def pack_proto(tid: int, pid: int, pn: int, is_comment: bool) -> bytes:
    req_proto = PbFloorReqIdl_pb2.PbFloorReqIdl()
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.kz = tid
    if is_comment:
        req_proto.data.spid = pid
    else:
        req_proto.data.pid = pid
    req_proto.data.pn = pn

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Comments:
    res_proto = PbFloorResIdl_pb2.PbFloorResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    comments = Comments.from_tbdata(data_proto)

    return comments


async def request_http(http_core: HttpCore, tid: int, pid: int, pn: int, is_comment: bool) -> Comments:
    data = pack_proto(tid, pid, pn, is_comment)

    request = http_core.pack_proto_request(
        yarl.URL.build(scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/pb/floor", query_string=f"cmd={CMD}"),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, tid: int, pid: int, pn: int, is_comment: bool) -> Comments:
    data = pack_proto(tid, pid, pn, is_comment)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
