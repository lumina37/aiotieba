import yarl

from ....const import APP_BASE_HOST, APP_INSECURE_SCHEME, MAIN_VERSION
from ....core import HttpCore, WsCore
from ....exception import TiebaServerError
from .._classdef import Homepage
from .._const import CMD
from ..protobuf import ProfileReqIdl_pb2, ProfileResIdl_pb2


def pack_proto(user_id: int, pn: int) -> bytes:
    req_proto = ProfileReqIdl_pb2.ProfileReqIdl()
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.common._client_type = 2
    req_proto.data.uid = user_id
    req_proto.data.need_post_count = 1
    req_proto.data.pn = pn

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Homepage:
    res_proto = ProfileResIdl_pb2.ProfileResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    homepage = Homepage.from_tbdata(data_proto)

    return homepage


async def request_http(http_core: HttpCore, user_id: int, pn: int) -> Homepage:
    data = pack_proto(user_id, pn)

    request = http_core.pack_proto_request(
        yarl.URL.build(
            scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/user/profile", query_string=f"cmd={CMD}"
        ),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, user_id: int, pn: int) -> Homepage:
    data = pack_proto(user_id, pn)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
