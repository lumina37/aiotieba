import sys

import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import Account, HttpCore, WsCore
from ...enums import BlacklistType
from ...exception import TiebaServerError
from ...helper import log_success
from .protobuf import SetUserBlackReqIdl_pb2, SetUserBlackResIdl_pb2

CMD = 309697


def pack_proto(account: Account, user_id: int, btype: BlacklistType) -> bytes:
    req_proto = SetUserBlackReqIdl_pb2.SetUserBlackReqIdl()
    req_proto.data.common.BDUSS = account._BDUSS
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.black_uid = user_id
    req_proto.data.perm_list.follow = 1 if btype & BlacklistType.FOLLOW else 2
    req_proto.data.perm_list.interact = 1 if btype & BlacklistType.INTERACT else 2
    req_proto.data.perm_list.chat = 1 if btype & BlacklistType.CHAT else 2

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> None:
    res_proto = SetUserBlackResIdl_pb2.SetUserBlackResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)


async def request_http(http_core: HttpCore, user_id: int, btype: BlacklistType) -> bool:
    data = pack_proto(http_core.account, user_id, btype)

    request = http_core.pack_proto_request(
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/user/setUserBlack", query_string=f"cmd={CMD}"
        ),
        data,
    )

    __log__ = f"user_id={user_id}"

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    log_success(sys._getframe(1), __log__)
    return True


async def request_ws(ws_core: WsCore, user_id: int, btype: BlacklistType) -> bool:
    data = pack_proto(ws_core.account, user_id, btype)

    __log__ = f"user_id={user_id}"

    response = await ws_core.send(data, CMD)
    parse_body(await response.read())

    log_success(sys._getframe(1), __log__)
    return True
