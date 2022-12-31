from typing import List, Tuple

import httpx

from ..._exception import TiebaServerError
from ..common.core import TiebaCore
from ..common.helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ..common.typedef import NewThread, UserInfo
from .protobuf import ProfileReqIdl_pb2, ProfileResIdl_pb2


def pack_proto(core: TiebaCore, portrait: str, with_threads: bool) -> bytes:
    req_proto = ProfileReqIdl_pb2.ProfileReqIdl()
    req_proto.data.common._client_version = core.main_version
    req_proto.data.need_post_count = 1
    req_proto.data.friend_uid_portrait = portrait
    if with_threads:
        req_proto.data.common._client_type = 2
    req_proto.data.pn = 1
    req_proto.data.rn = 20
    # req_proto.data.uid = (await self.get_self_info()).user_id  # 用该字段检查共同关注的吧

    return req_proto.SerializeToString()


def pack_request(client: httpx.AsyncClient, core: TiebaCore, portrait: str, with_threads: bool) -> httpx.Request:
    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/u/user/profile", "cmd=303012"),
        pack_proto(core, portrait, with_threads),
    )

    return request


def parse_proto(proto: bytes) -> Tuple[UserInfo, List[NewThread]]:
    res_proto = ProfileResIdl_pb2.ProfileResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    user = UserInfo(_raw_data=res_proto.data.user)
    threads = [NewThread(thread_proto) for thread_proto in res_proto.data.post_list]
    for thread in threads:
        thread._user = user

    return user, threads


def parse_response(response: httpx.Response) -> Tuple[UserInfo, List[NewThread]]:
    raise_for_status(response)

    return parse_proto(response.content)
