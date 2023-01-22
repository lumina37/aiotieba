import sys

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_INSECURE_SCHEME, log_exception, pack_proto_request, send_request
from ._classdef import UserInfo_guinfo_app
from .protobuf import GetUserInfoReqIdl_pb2, GetUserInfoResIdl_pb2


def pack_proto(user_id: int) -> bytes:
    req_proto = GetUserInfoReqIdl_pb2.GetUserInfoReqIdl()
    req_proto.data.user_id = user_id

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> UserInfo_guinfo_app:
    res_proto = GetUserInfoResIdl_pb2.GetUserInfoResIdl()
    res_proto.ParseFromString(body)

    if error_code := res_proto.error.errorno:
        raise TiebaServerError(error_code, res_proto.error.errmsg)

    user_proto = res_proto.data.user
    user = UserInfo_guinfo_app()._init(user_proto)

    return user


async def request_http(connector: aiohttp.TCPConnector, core: TbCore, user_id: int) -> UserInfo_guinfo_app:

    request = pack_proto_request(
        core,
        yarl.URL.build(
            scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/user/getuserinfo", query_string="cmd=303024"
        ),
        pack_proto(user_id),
    )

    try:
        body = await send_request(request, connector, read_bufsize=1024)
        user = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"user_id={user_id}")
        user = UserInfo_guinfo_app()._init_null()

    return user
