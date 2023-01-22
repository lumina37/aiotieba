import sys
from typing import Dict

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, log_exception, pack_proto_request, send_request
from .protobuf import SearchPostForumReqIdl_pb2, SearchPostForumResIdl_pb2


def pack_proto(core: TbCore, fname: str) -> bytes:
    req_proto = SearchPostForumReqIdl_pb2.SearchPostForumReqIdl()
    req_proto.data.common.BDUSS = core._BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.fname = fname

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Dict[str, int]:
    res_proto = SearchPostForumResIdl_pb2.SearchPostForumResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    tab_map = {tab_proto.tab_name: tab_proto.tab_id for tab_proto in res_proto.data.exact_match.tab_info}

    return tab_map


async def request_http(connector: aiohttp.TCPConnector, core: TbCore, fname: str) -> Dict[str, int]:

    request = pack_proto_request(
        core,
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/searchPostForum", query_string="cmd=309466"
        ),
        pack_proto(core, fname),
    )

    try:
        body = await send_request(request, connector, read_bufsize=4 * 1024)
        tab_map = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"fname={fname}")
        tab_map = {}

    return tab_map
