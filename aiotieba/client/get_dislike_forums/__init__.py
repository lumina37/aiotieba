import httpx

from ..._exception import TiebaServerError
from ..common.core import TiebaCore
from ..common.helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ..common.typedef import DislikeForums
from .protobuf import GetDislikeListReqIdl_pb2, GetDislikeListResIdl_pb2


def pack_proto(core: TiebaCore, pn: int, rn: int) -> bytes:
    req_proto = GetDislikeListReqIdl_pb2.GetDislikeListReqIdl()
    req_proto.data.common.BDUSS = core.BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.pn = pn
    req_proto.data.rn = rn

    return req_proto.SerializeToString()


def pack_request(client: httpx.AsyncClient, core: TiebaCore, pn: int, rn: int) -> httpx.Request:

    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/u/user/getDislikeList", "cmd=309692"),
        pack_proto(core, pn, rn),
    )

    return request


def parse_proto(proto: bytes) -> DislikeForums:
    res_proto = GetDislikeListResIdl_pb2.GetDislikeListResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    dislike_forums = DislikeForums(res_proto.data)

    return dislike_forums


def parse_response(response: httpx.Response) -> DislikeForums:
    raise_for_status(response)

    return parse_proto(response.content)
