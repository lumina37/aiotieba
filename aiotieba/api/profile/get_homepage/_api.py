from typing import List, Tuple

import yarl

from ....const import APP_BASE_HOST, APP_INSECURE_SCHEME, MAIN_VERSION
from ....core import HttpCore, WsCore
from ....exception import TiebaServerError
from .._classdef import Thread_pf, UserInfo_pf
from .._const import CMD
from ..protobuf import ProfileReqIdl_pb2, ProfileResIdl_pb2


def null_ret_factory() -> Tuple[UserInfo_pf, List[Thread_pf]]:
    return UserInfo_pf(), []


def pack_proto(user_id: int, pn: int) -> bytes:
    req_proto = ProfileReqIdl_pb2.ProfileReqIdl()
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.common._client_type = 2
    req_proto.data.uid = user_id
    req_proto.data.need_post_count = 1
    req_proto.data.pn = pn

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Tuple[UserInfo_pf, List[Thread_pf]]:
    res_proto = ProfileResIdl_pb2.ProfileResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    user = UserInfo_pf(data_proto.user)

    anti_proto = data_proto.anti_stat
    if anti_proto.block_stat and anti_proto.hide_stat and anti_proto.days_tofree > 30:
        user._is_blocked = True
    else:
        user._is_blocked = False

    threads = [Thread_pf(p) for p in data_proto.post_list]

    for thread in threads:
        thread._user = user

    return user, threads


async def request_http(http_core: HttpCore, user_id: int, pn: int) -> Tuple[UserInfo_pf, List[Thread_pf]]:
    data = pack_proto(user_id, pn)

    request = http_core.pack_proto_request(
        yarl.URL.build(
            scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/user/profile", query_string=f"cmd={CMD}"
        ),
        data,
    )

    __log__ = "user_id={user_id}"  # noqa: F841

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, user_id: int, pn: int) -> Tuple[UserInfo_pf, List[Thread_pf]]:
    data = pack_proto(user_id, pn)

    __log__ = "user_id={user_id}"  # noqa: F841

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
