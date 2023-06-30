from typing import List, Tuple

import yarl

from ...const import APP_BASE_HOST, APP_INSECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore, WsCore
from ...exception import TiebaServerError
from ._classdef import Thread_home, UserInfo_home
from .protobuf import ProfileReqIdl_pb2, ProfileResIdl_pb2

CMD = 303012


def null_ret_factory() -> Tuple[UserInfo_home, List[Thread_home]]:
    return UserInfo_home(), []


def pack_proto(user_id: int, pn: int, with_threads: bool) -> bytes:
    req_proto = ProfileReqIdl_pb2.ProfileReqIdl()
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.common._client_type = 2
    req_proto.data.uid = user_id
    req_proto.data.need_post_count = 1
    req_proto.data.pn = pn
    req_proto.data.page = bool(not with_threads)

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Tuple[UserInfo_home, List[Thread_home]]:
    res_proto = ProfileResIdl_pb2.ProfileResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    user = UserInfo_home(data_proto.user)

    anti_proto = data_proto.anti_stat
    if anti_proto.block_stat and anti_proto.hide_stat and anti_proto.days_tofree > 30:
        user._is_blocked = True
    else:
        user._is_blocked = False

    threads = [Thread_home(p) for p in data_proto.post_list]

    for thread in threads:
        thread._user = user

    return user, threads


async def request_http(
    http_core: HttpCore, user_id: int, pn: int, with_threads: bool
) -> Tuple[UserInfo_home, List[Thread_home]]:
    data = pack_proto(user_id, with_threads)

    request = http_core.pack_proto_request(
        yarl.URL.build(
            scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/user/profile", query_string=f"cmd={CMD}"
        ),
        data,
    )

    __log__ = "user_id={user_id}"  # noqa: F841

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)


async def request_ws(
    ws_core: WsCore, user_id: int, pn: int, with_threads: bool
) -> Tuple[UserInfo_home, List[Thread_home]]:
    data = pack_proto(user_id, with_threads)

    __log__ = "user_id={user_id}"  # noqa: F841

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
