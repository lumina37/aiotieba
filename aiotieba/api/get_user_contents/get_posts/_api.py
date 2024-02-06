import yarl

from ....const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ....core import Account, HttpCore, WsCore
from ....exception import TiebaServerError
from .._classdef import UserPostss
from .._const import CMD
from ..protobuf import UserPostReqIdl_pb2, UserPostResIdl_pb2


def pack_proto(account: Account, user_id: int, pn: int) -> bytes:
    req_proto = UserPostReqIdl_pb2.UserPostReqIdl()
    req_proto.data.common.BDUSS = account.BDUSS
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.user_id = user_id
    req_proto.data.need_content = 1
    req_proto.data.pn = pn
    req_proto.data.is_view_card = 1

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> UserPostss:
    res_proto = UserPostResIdl_pb2.UserPostResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    upostss = UserPostss.from_tbdata(data_proto)

    return upostss


async def request_http(http_core: HttpCore, user_id: int, pn: int) -> UserPostss:
    data = pack_proto(http_core.account, user_id, pn)

    request = http_core.pack_proto_request(
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/feed/userpost", query_string=f"cmd={CMD}"
        ),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, user_id: int, pn: int) -> UserPostss:
    data = pack_proto(ws_core.account, user_id, pn)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
