import sys

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_INSECURE_SCHEME, log_exception, pack_proto_request, send_request
from ._classdef import UserInfo_TUid
from .protobuf import GetUserByTiebaUidReqIdl_pb2, GetUserByTiebaUidResIdl_pb2


def pack_proto(core: TbCore, tieba_uid: int) -> bytes:
    req_proto = GetUserByTiebaUidReqIdl_pb2.GetUserByTiebaUidReqIdl()
    req_proto.data.common._client_version = core.main_version
    req_proto.data.tieba_uid = str(tieba_uid)

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> UserInfo_TUid:
    res_proto = GetUserByTiebaUidResIdl_pb2.GetUserByTiebaUidResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    user_proto = res_proto.data.user
    user = UserInfo_TUid()._init(user_proto)

    return user


async def request_http(connector: aiohttp.TCPConnector, core: TbCore, tieba_uid: int) -> UserInfo_TUid:

    request = pack_proto_request(
        core,
        yarl.URL.build(
            scheme=APP_INSECURE_SCHEME,
            host=APP_BASE_HOST,
            path="/c/u/user/getUserByTiebaUid",
            query_string="cmd=309702",
        ),
        pack_proto(core, tieba_uid),
    )

    try:
        body = await send_request(request, connector, read_bufsize=1024)
        user = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"tieba_uid={tieba_uid}")
        user = UserInfo_TUid()._init_null()

    return user
