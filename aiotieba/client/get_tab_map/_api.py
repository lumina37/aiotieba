from typing import Dict

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, pack_proto_request, send_request
from .protobuf import SearchPostForumReqIdl_pb2, SearchPostForumResIdl_pb2


def pack_proto(core: TbCore, fname: str) -> bytes:
    req_proto = SearchPostForumReqIdl_pb2.SearchPostForumReqIdl()
    req_proto.data.common.BDUSS = core._BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.fname = fname

    return req_proto.SerializeToString()


async def request_http(connector: aiohttp.TCPConnector, core: TbCore, proto: bytes) -> bytes:

    request = pack_proto_request(
        core,
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/searchPostForum", query_string="cmd=309466"
        ),
        proto,
    )

    body = await send_request(request, connector, read_bufsize=4 * 1024)

    return body


def parse_body(body: bytes) -> Dict[str, int]:
    res_proto = SearchPostForumResIdl_pb2.SearchPostForumResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    tab_map = {tab_proto.tab_name: tab_proto.tab_id for tab_proto in res_proto.data.exact_match.tab_info}

    return tab_map
