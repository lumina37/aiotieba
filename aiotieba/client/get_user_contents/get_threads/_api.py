import sys
from typing import List

import aiohttp
import yarl

from ..._core import APP_BASE_HOST, TbCore
from ..._exception import TiebaServerError
from ..._helper import APP_SECURE_SCHEME, log_exception, pack_proto_request, send_request
from .._classdef import UserInfo_u, UserThread
from ..protobuf import UserPostReqIdl_pb2, UserPostResIdl_pb2


def pack_proto(core: TbCore, user_id: int, pn: int, public_only: bool) -> bytes:
    req_proto = UserPostReqIdl_pb2.UserPostReqIdl()
    req_proto.data.common.BDUSS = core._BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.user_id = user_id
    req_proto.data.is_thread = 1
    req_proto.data.need_content = 1
    req_proto.data.pn = pn
    req_proto.data.is_view_card = 2 if public_only else 1

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> List[UserThread]:
    res_proto = UserPostResIdl_pb2.UserPostResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    uthreads = [UserThread()._init(p) for p in data_proto.post_list]
    if uthreads:
        user = UserInfo_u()._init(data_proto.post_list[0])
        for uthread in uthreads:
            uthread._user = user
            uthread._author_id = user._user_id

    return uthreads


async def request_http(
    connector: aiohttp.TCPConnector, core: TbCore, user_id: int, pn: int, public_only: bool
) -> List[UserThread]:

    request = pack_proto_request(
        core,
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/feed/userpost", query_string="cmd=303002"
        ),
        pack_proto(core, user_id, pn, public_only),
    )

    try:
        body = await send_request(request, connector, read_bufsize=64 * 1024)
        threads = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"user_id={user_id}")
        threads = []

    return threads
