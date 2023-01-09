import httpx

from .._classdef.core import TiebaCore
from .._exception import TiebaServerError
from .._helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ._classdef import SquareForums
from .protobuf import GetForumSquareReqIdl_pb2, GetForumSquareResIdl_pb2


def pack_proto(core: TiebaCore, cname: str, pn: int, rn: int) -> bytes:
    req_proto = GetForumSquareReqIdl_pb2.GetForumSquareReqIdl()
    req_proto.data.common.BDUSS = core.BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.class_name = cname
    req_proto.data.pn = pn
    req_proto.data.rn = rn

    return req_proto.SerializeToString()


def pack_request(client: httpx.AsyncClient, core: TiebaCore, cname: str, pn: int, rn: int) -> httpx.Request:
    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/f/forum/getForumSquare", "cmd=309653"),
        pack_proto(core, cname, pn, rn),
    )

    return request


def parse_proto(proto: bytes) -> SquareForums:
    res_proto = GetForumSquareResIdl_pb2.GetForumSquareResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    square_forums = SquareForums()._init(data_proto)

    return square_forums


def parse_response(response: httpx.Response) -> SquareForums:
    raise_for_status(response)

    return parse_proto(response.content)
