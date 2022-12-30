import httpx

from ..._exception import TiebaServerError
from ..common.helper import pack_proto_request
from ..common.typedef import DislikeForums
from .protobuf import GetDislikeListReqIdl_pb2, GetDislikeListResIdl_pb2


def pack_request(client: httpx.AsyncClient, bduss: str, version: str, pn: int, rn: int) -> httpx.Request:

    req_proto = GetDislikeListReqIdl_pb2.GetDislikeListReqIdl()
    req_proto.data.common.BDUSS = bduss
    req_proto.data.common._client_version = version
    req_proto.data.pn = pn
    req_proto.data.rn = rn

    request = pack_proto_request(
        client,
        "http://tiebac.baidu.com/c/u/user/getDislikeList?cmd=309692",
        req_proto.SerializeToString(),
    )

    return request


def parse_response(response: httpx.Response) -> DislikeForums:
    response.raise_for_status()

    res_proto = GetDislikeListResIdl_pb2.GetDislikeListResIdl()
    res_proto.ParseFromString(response.content)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    dislike_forums = DislikeForums(res_proto.data)

    return dislike_forums
