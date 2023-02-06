import sys
from typing import List, Tuple

import yarl

from .._core import APP_BASE_HOST, HttpCore, TbCore
from .._helper import APP_INSECURE_SCHEME, log_exception, pack_proto_request, send_request
from ..exception import TiebaServerError
from ._classdef import Thread_home, UserInfo_home
from .protobuf import ProfileReqIdl_pb2, ProfileResIdl_pb2

CMD = 303012


def pack_proto(core: TbCore, portrait: str, with_threads: bool) -> bytes:
    req_proto = ProfileReqIdl_pb2.ProfileReqIdl()
    req_proto.data.common._client_version = core.main_version
    req_proto.data.need_post_count = 1
    req_proto.data.friend_uid_portrait = portrait
    if with_threads:
        req_proto.data.common._client_type = 2
    req_proto.data.pn = 1
    req_proto.data.rn = 20

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Tuple[UserInfo_home, List[Thread_home]]:
    res_proto = ProfileResIdl_pb2.ProfileResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    user = UserInfo_home()._init(data_proto.user)

    anti_proto = data_proto.anti_stat
    if anti_proto.block_stat and anti_proto.hide_stat and anti_proto.days_tofree > 30:
        user._is_blocked = True
    else:
        user._is_blocked = False

    threads = [Thread_home()._init(p) for p in data_proto.post_list]

    for thread in threads:
        thread._user = user

    return user, threads


async def request_http(
    http_core: HttpCore, portrait: str, with_threads: bool
) -> Tuple[UserInfo_home, List[Thread_home]]:

    request = pack_proto_request(
        http_core,
        yarl.URL.build(
            scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/user/profile", query_string=f"cmd={CMD}"
        ),
        pack_proto(http_core.core, portrait, with_threads),
    )

    try:
        body = await send_request(request, http_core.connector, read_bufsize=64 * 1024)
        user, threads = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"portrait={portrait}")
        user = UserInfo_home()._init_null()
        threads = []

    return user, threads
