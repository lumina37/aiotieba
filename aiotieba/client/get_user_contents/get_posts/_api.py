from typing import List

import httpx

from ..._classdef.core import TiebaCore
from ..._exception import TiebaServerError
from ..._helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from .._classdef import UserInfo_u, UserPosts
from ..protobuf import UserPostReqIdl_pb2, UserPostResIdl_pb2


def pack_proto(core: TiebaCore, user_id: int, pn: int) -> bytes:
    req_proto = UserPostReqIdl_pb2.UserPostReqIdl()
    req_proto.data.common.BDUSS = core.BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.user_id = user_id
    req_proto.data.need_content = 1
    req_proto.data.pn = pn
    req_proto.data.is_view_card = 1

    return req_proto.SerializeToString()


def pack_request(client: httpx.AsyncClient, core: TiebaCore, user_id: int, pn: int) -> httpx.Request:
    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/u/feed/userpost", "cmd=303002"),
        pack_proto(core, user_id, pn),
    )

    return request


def parse_proto(proto: bytes) -> List[UserPosts]:
    res_proto = UserPostResIdl_pb2.UserPostResIdl()
    res_proto.ParseFromString(proto)

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


def parse_response(response: httpx.Response) -> List[UserPosts]:
    raise_for_status(response)

    return parse_proto(response.content)
