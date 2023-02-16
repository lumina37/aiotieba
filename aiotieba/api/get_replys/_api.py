import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import Account, HttpCore, WsCore
from ...exception import TiebaServerError
from ...request import pack_proto_request, send_request
from ._classdef import Replys
from .protobuf import ReplyMeReqIdl_pb2, ReplyMeResIdl_pb2

CMD = 303007


def pack_proto(core: Account, pn: int) -> bytes:
    req_proto = ReplyMeReqIdl_pb2.ReplyMeReqIdl()
    req_proto.data.common.BDUSS = core._BDUSS
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.pn = str(pn)

    return req_proto.SerializeToString()


def parse_body(proto: bytes) -> Replys:
    res_proto = ReplyMeResIdl_pb2.ReplyMeResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    replys = Replys(data_proto)

    return replys


async def request_http(http_core: HttpCore, pn: int) -> Replys:
    data = pack_proto(http_core.account, pn)

    request = pack_proto_request(
        http_core,
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/feed/replyme", query_string=f"cmd={CMD}"
        ),
        data,
    )

    body = await send_request(request, http_core.network, read_bufsize=16 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, pn: int) -> Replys:
    data = pack_proto(ws_core.account, pn)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
