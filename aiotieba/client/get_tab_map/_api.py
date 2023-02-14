from typing import Dict

import yarl

from .._core import HttpCore, TbCore, WsCore
from .._helper import pack_proto_request, send_request
from ..const import APP_BASE_HOST, APP_SECURE_SCHEME
from ..exception import TiebaServerError
from .protobuf import SearchPostForumReqIdl_pb2, SearchPostForumResIdl_pb2

CMD = 309466


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


async def request_http(http_core: HttpCore, fname: str) -> Dict[str, int]:
    data = pack_proto(http_core.core, fname)

    request = pack_proto_request(
        http_core,
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/searchPostForum", query_string=f"cmd={CMD}"
        ),
        data,
    )

    __log__ = "fname={fname}"  # noqa: F841

    body = await send_request(request, http_core.connector, read_bufsize=4 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, fname: str) -> Dict[str, int]:
    data = pack_proto(ws_core.core, fname)

    __log__ = "fname={fname}"  # noqa: F841

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
