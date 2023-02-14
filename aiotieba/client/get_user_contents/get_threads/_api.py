from typing import List

import yarl

from ..._core import HttpCore, TbCore, WsCore
from ..._helper import pack_proto_request, send_request
from ...const import APP_BASE_HOST, APP_SECURE_SCHEME
from ...exception import TiebaServerError
from .._classdef import UserInfo_u, UserThread
from ..protobuf import UserPostReqIdl_pb2, UserPostResIdl_pb2

CMD = 303002


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
    uthreads = [UserThread(p) for p in data_proto.post_list]
    if uthreads:
        user = UserInfo_u(data_proto.post_list[0])
        for uthread in uthreads:
            uthread._user = user
            uthread._author_id = user._user_id

    return uthreads


async def request_http(http_core: HttpCore, user_id: int, pn: int, public_only: bool) -> List[UserThread]:
    data = pack_proto(http_core.core, user_id, pn, public_only)

    request = pack_proto_request(
        http_core,
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/feed/userpost", query_string=f"cmd={CMD}"
        ),
        data,
    )

    __log__ = "user_id={user_id}"  # noqa: F841

    body = await send_request(request, http_core.connector, read_bufsize=64 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, user_id: int, pn: int, public_only: bool) -> List[UserThread]:
    data = pack_proto(ws_core.core, user_id, pn, public_only)

    __log__ = "user_id={user_id}"  # noqa: F841

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
