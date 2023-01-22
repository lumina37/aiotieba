import sys

import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, log_exception, pack_proto_request, send_request
from ._classdef import DislikeForums
from .protobuf import GetDislikeListReqIdl_pb2, GetDislikeListResIdl_pb2


def pack_proto(core: TbCore, pn: int, rn: int) -> bytes:
    req_proto = GetDislikeListReqIdl_pb2.GetDislikeListReqIdl()
    req_proto.data.common.BDUSS = core._BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.pn = pn
    req_proto.data.rn = rn

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> DislikeForums:
    res_proto = GetDislikeListResIdl_pb2.GetDislikeListResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    dislike_forums = DislikeForums()._init(data_proto)

    return dislike_forums


async def request_http(connector: aiohttp.TCPConnector, core: TbCore, pn: int, rn: int) -> DislikeForums:

    request = pack_proto_request(
        core,
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/user/getDislikeList", query_string="cmd=309692"
        ),
        pack_proto(core, pn, rn),
    )

    try:
        body = await send_request(request, connector, read_bufsize=8 * 1024)
        dislike_forums = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err)
        dislike_forums = DislikeForums()._init_null()

    return dislike_forums
