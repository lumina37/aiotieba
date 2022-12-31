from typing import List

import httpx

from ..._exception import TiebaServerError
from ..common.core import TiebaCore
from ..common.helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ..common.typedef import NewThread
from .protobuf import UserPostReqIdl_pb2, UserPostResIdl_pb2


def pack_proto(core: TiebaCore, user_id: int, pn: int, public_only: bool) -> bytes:
    req_proto = UserPostReqIdl_pb2.UserPostReqIdl()
    req_proto.data.common.BDUSS = core.BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.user_id = user_id
    req_proto.data.is_thread = 1
    req_proto.data.need_content = 1
    req_proto.data.pn = pn
    req_proto.data.is_view_card = 2 if public_only else 1

    return req_proto.SerializeToString()


def pack_request(client: httpx.AsyncClient, core: TiebaCore, user_id: int, pn: int, public_only: bool) -> httpx.Request:
    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/u/feed/userpost", "cmd=303002"),
        pack_proto(core, user_id, pn, public_only),
    )

    return request


def parse_proto(proto: bytes) -> List[NewThread]:
    res_proto = UserPostResIdl_pb2.UserPostResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    threads = [NewThread(thread_proto) for thread_proto in res_proto.data.post_list]

    return threads


def parse_response(response: httpx.Response) -> List[NewThread]:
    raise_for_status(response)

    return parse_proto(response.content)
