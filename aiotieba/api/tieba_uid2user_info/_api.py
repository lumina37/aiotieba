import yarl

from ...const import APP_BASE_HOST, APP_INSECURE_SCHEME, MAIN_VERSION
from ...core import Account, HttpCore, WsCore
from ...exception import TiebaServerError
from ...request import pack_proto_request, send_request
from ._classdef import UserInfo_TUid
from .protobuf import GetUserByTiebaUidReqIdl_pb2, GetUserByTiebaUidResIdl_pb2

CMD = 309702


def pack_proto(core: Account, tieba_uid: int) -> bytes:
    req_proto = GetUserByTiebaUidReqIdl_pb2.GetUserByTiebaUidReqIdl()
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.tieba_uid = str(tieba_uid)

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> UserInfo_TUid:
    res_proto = GetUserByTiebaUidResIdl_pb2.GetUserByTiebaUidResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    user_proto = res_proto.data.user
    user = UserInfo_TUid(user_proto)

    return user


async def request_http(http_core: HttpCore, tieba_uid: int) -> UserInfo_TUid:
    data = pack_proto(http_core.account, tieba_uid)

    request = pack_proto_request(
        http_core,
        yarl.URL.build(
            scheme=APP_INSECURE_SCHEME,
            host=APP_BASE_HOST,
            path="/c/u/user/getUserByTiebaUid",
            query_string=f"cmd={CMD}",
        ),
        data,
    )

    __log__ = "tieba_uid={tieba_uid}"  # noqa: F841

    body = await send_request(request, http_core.network, read_bufsize=1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, tieba_uid: int) -> UserInfo_TUid:
    data = pack_proto(ws_core.account, tieba_uid)

    __log__ = "tieba_uid={tieba_uid}"  # noqa: F841

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
