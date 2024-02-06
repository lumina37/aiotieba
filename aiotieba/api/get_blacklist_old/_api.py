import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import Account, HttpCore, WsCore
from ...exception import TiebaServerError
from ._classdef import BlacklistOldUsers
from .protobuf import UserMuteQueryReqIdl_pb2, UserMuteQueryResIdl_pb2

CMD = 303028


def pack_proto(account: Account, pn: int, rn: int) -> bytes:
    req_proto = UserMuteQueryReqIdl_pb2.UserMuteQueryReqIdl()
    req_proto.data.common.BDUSS = account.BDUSS
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.pn = pn
    req_proto.data.rn = rn

    return req_proto.SerializeToString()


def parse_body(proto: bytes) -> BlacklistOldUsers:
    res_proto = UserMuteQueryResIdl_pb2.UserMuteQueryResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    blacklist_users = BlacklistOldUsers.from_tbdata(data_proto)

    return blacklist_users


async def request_http(http_core: HttpCore, pn: int, rn: int) -> BlacklistOldUsers:
    data = pack_proto(http_core.account, pn, rn)

    request = http_core.pack_proto_request(
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/user/userMuteQuery", query_string=f"cmd={CMD}"
        ),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, pn: int, rn: int) -> BlacklistOldUsers:
    data = pack_proto(ws_core.account, pn, rn)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
