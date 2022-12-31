import httpx

from ..._exception import TiebaServerError
from ..common.core import TiebaCore
from ..common.helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ..common.typedef import SquareForums
from .protobuf import GetForumSquareReqIdl_pb2, GetForumSquareResIdl_pb2


def pack_proto(core: TiebaCore, class_name: str, pn: int, rn: int) -> bytes:
    req_proto = GetForumSquareReqIdl_pb2.GetForumSquareReqIdl()
    req_proto.data.common.BDUSS = core.BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.class_name = class_name
    req_proto.data.pn = pn
    req_proto.data.rn = rn

    return req_proto.SerializeToString()


def pack_request(client: httpx.AsyncClient, core: TiebaCore, class_name: str, pn: int, rn: int) -> httpx.Request:
    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/f/forum/getForumSquare", "cmd=309653"),
        pack_proto(core, class_name, pn, rn),
    )

    return request


def parse_proto(proto: bytes) -> SquareForums:
    res_proto = GetForumSquareResIdl_pb2.GetForumSquareResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    square_forums = SquareForums(res_proto.data)

    return square_forums


def parse_response(response: httpx.Response) -> SquareForums:
    raise_for_status(response)

    return parse_proto(response.content)
