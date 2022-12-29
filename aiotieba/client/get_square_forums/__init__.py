import httpx

from ..._exception import TiebaServerError
from ..common.helper import pack_proto_request
from ..common.typedef import SquareForums
from .protobuf import GetForumSquareReqIdl_pb2, GetForumSquareResIdl_pb2


def pack_request(
    client: httpx.AsyncClient, bduss: str, version: str, class_name: str, pn: int, rn: int
) -> httpx.Request:

    req_proto = GetForumSquareReqIdl_pb2.GetForumSquareReqIdl()
    req_proto.data.common.BDUSS = bduss
    req_proto.data.common._client_version = version
    req_proto.data.class_name = class_name
    req_proto.data.pn = pn
    req_proto.data.rn = rn

    request = pack_proto_request(
        client,
        "http://tiebac.baidu.com/c/f/forum/getForumSquare?cmd=309653",
        req_proto.SerializeToString(),
    )

    return request


def parse_response(response: httpx.Response) -> SquareForums:
    response.raise_for_status()

    res_proto = GetForumSquareResIdl_pb2.GetForumSquareResIdl()
    res_proto.ParseFromString(response.content)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    square_forums = SquareForums(res_proto.data)

    return square_forums
