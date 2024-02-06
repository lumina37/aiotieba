import yarl

from ....const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ....core import Account, HttpCore, WsCore
from ....exception import TiebaServerError
from .._classdef import UserThreads
from .._const import CMD
from ..protobuf import UserPostReqIdl_pb2, UserPostResIdl_pb2


def pack_proto(account: Account, user_id: int, pn: int, public_only: bool) -> bytes:
    req_proto = UserPostReqIdl_pb2.UserPostReqIdl()
    req_proto.data.common.BDUSS = account.BDUSS
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.user_id = user_id
    req_proto.data.is_thread = 1
    req_proto.data.need_content = 1
    req_proto.data.pn = pn
    req_proto.data.is_view_card = 2 if public_only else 1

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> UserThreads:
    res_proto = UserPostResIdl_pb2.UserPostResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    uthreads = UserThreads.from_tbdata(data_proto)

    return uthreads


async def request_http(http_core: HttpCore, user_id: int, pn: int, public_only: bool) -> UserThreads:
    data = pack_proto(http_core.account, user_id, pn, public_only)

    request = http_core.pack_proto_request(
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/feed/userpost", query_string=f"cmd={CMD}"
        ),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, user_id: int, pn: int, public_only: bool) -> UserThreads:
    data = pack_proto(ws_core.account, user_id, pn, public_only)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
