import sys
from typing import List

import aiohttp
import yarl

from ..._core import APP_BASE_HOST, TbCore
from ..._exception import TiebaServerError
from ..._helper import APP_SECURE_SCHEME, log_exception, pack_proto_request, send_request
from .._classdef import UserInfo_u, UserPosts
from ..protobuf import UserPostReqIdl_pb2, UserPostResIdl_pb2


def pack_proto(core: TbCore, user_id: int, pn: int) -> bytes:
    req_proto = UserPostReqIdl_pb2.UserPostReqIdl()
    req_proto.data.common.BDUSS = core._BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.user_id = user_id
    req_proto.data.need_content = 1
    req_proto.data.pn = pn
    req_proto.data.is_view_card = 1

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> List[UserPosts]:
    res_proto = UserPostResIdl_pb2.UserPostResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    uposts_list = [UserPosts()._init(p) for p in data_proto.post_list]
    if uposts_list:
        user = UserInfo_u()._init(data_proto.post_list[0])
        for uposts in uposts_list:
            for upost in uposts:
                upost._user = user
                upost._author_id = user._user_id

    return uposts_list


async def request_http(connector: aiohttp.TCPConnector, core: TbCore, user_id: int, pn: int) -> List[UserPosts]:

    request = pack_proto_request(
        core,
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/feed/userpost", query_string="cmd=303002"
        ),
        pack_proto(core, user_id, pn),
    )

    try:
        body = await send_request(request, connector, read_bufsize=8 * 1024)
        uposts_list = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"user_id={user_id}")
        uposts_list = []

    return uposts_list
