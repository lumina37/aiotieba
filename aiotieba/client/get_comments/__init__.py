import httpx

from ..._exception import TiebaServerError
from ..common.helper import pack_proto_request
from ..common.typedef import Comments
from .protobuf import PbFloorReqIdl_pb2, PbFloorResIdl_pb2


def pack_request(client: httpx.AsyncClient, version: str, tid: int, pid: int, pn: int, is_floor: bool) -> httpx.Request:

    req_proto = PbFloorReqIdl_pb2.PbFloorReqIdl()
    req_proto.data.common._client_version = version
    req_proto.data.tid = tid
    if is_floor:
        req_proto.data.spid = pid
    else:
        req_proto.data.pid = pid
    req_proto.data.pn = pn

    request = pack_proto_request(
        client,
        "http://tiebac.baidu.com/c/f/pb/floor?cmd=302002",
        req_proto.SerializeToString(),
    )

    return request


def parse_response(response: httpx.Response) -> Comments:
    res_proto = PbFloorResIdl_pb2.PbFloorResIdl()
    res_proto.ParseFromString(response.content)

    if int(res_proto.error.errorno):
        raise TiebaServerError(res_proto.error.errmsg)

    comments = Comments(res_proto.data)

    return comments
