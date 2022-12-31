import httpx

from ..._exception import TiebaServerError
from ..common.core import TiebaCore
from ..common.helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ..common.typedef import Comments
from .protobuf import PbFloorReqIdl_pb2, PbFloorResIdl_pb2


def pack_proto(core: TiebaCore, tid: int, pid: int, pn: int, is_floor: bool) -> bytes:
    req_proto = PbFloorReqIdl_pb2.PbFloorReqIdl()
    req_proto.data.common._client_version = core.main_version
    req_proto.data.tid = tid
    if is_floor:
        req_proto.data.spid = pid
    else:
        req_proto.data.pid = pid
    req_proto.data.pn = pn

    return req_proto.SerializeToString()


def pack_request(
    client: httpx.AsyncClient, core: TiebaCore, tid: int, pid: int, pn: int, is_floor: bool
) -> httpx.Request:
    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/f/pb/floor", "cmd=302002"),
        pack_proto(core, tid, pid, pn, is_floor),
    )

    return request


def parse_proto(proto: bytes) -> Comments:
    res_proto = PbFloorResIdl_pb2.PbFloorResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    comments = Comments(res_proto.data)

    return comments


def parse_response(response: httpx.Response) -> Comments:
    raise_for_status(response)

    return parse_proto(response.content)
