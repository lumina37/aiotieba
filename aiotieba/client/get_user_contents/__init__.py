from typing import List

import httpx

from ..._exception import TiebaServerError
from ..common.helper import pack_proto_request
from ..common.typedef import NewThread, UserInfo, UserPosts
from .protobuf import UserPostReqIdl_pb2, UserPostResIdl_pb2


def pack_request(
    client: httpx.AsyncClient, bduss: str, version: str, user_id: int, pn: int, is_thread: bool, public_only: bool
) -> httpx.Request:

    req_proto = UserPostReqIdl_pb2.UserPostReqIdl()
    req_proto.data.common.BDUSS = bduss
    req_proto.data.common._client_version = version
    req_proto.data.user_id = user_id
    req_proto.data.is_thread = is_thread
    req_proto.data.need_content = 1
    req_proto.data.pn = pn
    req_proto.data.is_view_card = 2 if public_only else 1

    request = pack_proto_request(
        client,
        "http://tiebac.baidu.com/c/u/feed/userpost?cmd=303002",
        req_proto.SerializeToString(),
    )

    return request


def thread_parse_response(response: httpx.Response, user: UserInfo) -> List[NewThread]:
    response.raise_for_status()

    res_proto = UserPostResIdl_pb2.UserPostResIdl()
    res_proto.ParseFromString(response.content)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    threads = [NewThread(thread_proto) for thread_proto in res_proto.data.post_list]
    for thread in threads:
        thread._user = user

    return threads


def userpost_parse_response(response: httpx.Response, user: UserInfo) -> List[UserPosts]:
    response.raise_for_status()

    res_proto = UserPostResIdl_pb2.UserPostResIdl()
    res_proto.ParseFromString(response.content)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    res_list = [UserPosts(posts_proto) for posts_proto in res_proto.data.post_list]
    for userposts in res_list:
        for userpost in userposts:
            userpost._user = user

    return res_list
