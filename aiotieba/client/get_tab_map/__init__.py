from typing import Dict

import httpx

from ..._exception import TiebaServerError
from ..common.core import TiebaCore
from ..common.helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from .protobuf import SearchPostForumReqIdl_pb2, SearchPostForumResIdl_pb2


def pack_proto(core: TiebaCore, fname: str) -> bytes:
    req_proto = SearchPostForumReqIdl_pb2.SearchPostForumReqIdl()
    req_proto.data.common.BDUSS = core.BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.fname = fname

    return req_proto.SerializeToString()


def pack_request(client: httpx.AsyncClient, core: TiebaCore, fname: str) -> httpx.Request:
    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/f/forum/searchPostForum", "cmd=309466"),
        pack_proto(core, fname),
    )

    return request


def parse_proto(proto: bytes) -> Dict[str, int]:
    res_proto = SearchPostForumResIdl_pb2.SearchPostForumResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    tab_map = {tab_proto.tab_name: tab_proto.tab_id for tab_proto in res_proto.data.exact_match.tab_info}

    return tab_map


def parse_response(response: httpx.Response) -> Dict[str, int]:
    raise_for_status(response)

    return parse_proto(response.content)
