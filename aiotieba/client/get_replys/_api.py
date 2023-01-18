import aiohttp
import yarl

from .._core import APP_BASE_HOST, APP_SECURE_SCHEME, TbCore
from .._exception import TiebaServerError
from .._helper import pack_proto_request, send_request
from ._classdef import Replys
from .protobuf import ReplyMeReqIdl_pb2, ReplyMeResIdl_pb2


def pack_proto(core: TbCore, pn: int) -> bytes:
    req_proto = ReplyMeReqIdl_pb2.ReplyMeReqIdl()
    req_proto.data.common.BDUSS = core._BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.pn = str(pn)

    return req_proto.SerializeToString()


async def request_http(connector: aiohttp.TCPConnector, core: TbCore, proto: bytes) -> bytes:

    request = pack_proto_request(
        core,
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/feed/replyme", query_string="cmd=303007"
        ),
        proto,
    )

    body = await send_request(request, connector, read_bufsize=16 * 1024)

    return body


def parse_body(proto: bytes) -> Replys:
    res_proto = ReplyMeResIdl_pb2.ReplyMeResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    replys = Replys()._init(data_proto)

    return replys
