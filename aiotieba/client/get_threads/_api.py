import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_NON_SECURE_SCHEME, pack_proto_request, send_request
from ._classdef import Threads
from .protobuf import FrsPageReqIdl_pb2, FrsPageResIdl_pb2


def pack_proto(core: TbCore, fname: str, pn: int, rn: int, sort: int, is_good: bool) -> bytes:
    req_proto = FrsPageReqIdl_pb2.FrsPageReqIdl()
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = core.main_version
    req_proto.data.fname = fname
    req_proto.data.pn = pn
    req_proto.data.rn = 105
    req_proto.data.rn_need = rn if rn > 0 else 1
    req_proto.data.is_good = is_good
    req_proto.data.sort = sort

    return req_proto.SerializeToString()


async def request_http(connector: aiohttp.TCPConnector, core: TbCore, proto: bytes) -> aiohttp.ClientRequest:
    request = pack_proto_request(
        core,
        yarl.URL.build(
            scheme=APP_NON_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/frs/page", query_string="cmd=301001"
        ),
        proto,
    )

    body = await send_request(request, connector, read_bufsize=256 * 1024)

    return body


def parse_body(body: bytes) -> Threads:
    res_proto = FrsPageResIdl_pb2.FrsPageResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    threads = Threads()._init(data_proto)

    return threads
