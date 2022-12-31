import httpx

from ..._exception import TiebaServerError
from ..common.core import TiebaCore
from ..common.helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ..common.typedef import Replys
from .protobuf import ReplyMeReqIdl_pb2, ReplyMeResIdl_pb2


def pack_proto(core: TiebaCore, pn: int) -> bytes:
    req_proto = ReplyMeReqIdl_pb2.ReplyMeReqIdl()
    req_proto.data.common.BDUSS = core.BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.pn = str(pn)

    return req_proto.SerializeToString()


def pack_request(client: httpx.AsyncClient, core: TiebaCore, pn: int) -> httpx.Request:

    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/u/feed/replyme", "cmd=303007"),
        pack_proto(core, pn),
    )

    return request


def parse_proto(proto: bytes) -> Replys:
    res_proto = ReplyMeResIdl_pb2.ReplyMeResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    replys = Replys(res_proto.data)

    return replys


def parse_response(response: httpx.Response) -> Replys:
    raise_for_status(response)

    return parse_proto(response.content)
