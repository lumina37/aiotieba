import sys

import yarl

from .._core import APP_BASE_HOST, HttpCore, TbCore
from .._helper import APP_INSECURE_SCHEME, log_exception, pack_proto_request, send_request
from ..exception import TiebaServerError
from ._classdef import Comments
from .protobuf import PbFloorReqIdl_pb2, PbFloorResIdl_pb2

CMD = 302002


def pack_proto(core: TbCore, tid: int, pid: int, pn: int, is_floor: bool) -> bytes:
    req_proto = PbFloorReqIdl_pb2.PbFloorReqIdl()
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = core.main_version
    req_proto.data.tid = tid
    if is_floor:
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
    comments = Comments()._init(data_proto)

    return comments


async def request_http(http_core: HttpCore, tid: int, pid: int, pn: int, is_floor: bool) -> Comments:

    request = pack_proto_request(
        http_core,
        yarl.URL.build(scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/pb/floor", query_string=f"cmd={CMD}"),
        pack_proto(http_core.core, tid, pid, pn, is_floor),
    )

    try:
        body = await send_request(request, http_core.connector, read_bufsize=8 * 1024)
        comments = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"tid={tid} pid={pid}")
        comments = Comments()._init_null()

    return comments
