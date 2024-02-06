import yarl

from ...const import APP_BASE_HOST, APP_INSECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore, WsCore
from ...exception import TiebaServerError
from ._classdef import Threads
from .protobuf import FrsPageReqIdl_pb2, FrsPageResIdl_pb2

CMD = 301001


def pack_proto(fname: str, pn: int, rn: int, sort: int, is_good: bool) -> bytes:
    req_proto = FrsPageReqIdl_pb2.FrsPageReqIdl()
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.kw = fname
    req_proto.data.pn = pn
    req_proto.data.rn = 105
    req_proto.data.rn_need = rn if rn > 0 else 1
    req_proto.data.is_good = is_good
    req_proto.data.sort_type = sort

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Threads:
    res_proto = FrsPageResIdl_pb2.FrsPageResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    threads = Threads.from_tbdata(data_proto)

    return threads


async def request_http(http_core: HttpCore, fname: str, pn: int, rn: int, sort: int, is_good: bool) -> Threads:
    data = pack_proto(fname, pn, rn, sort, is_good)

    request = http_core.pack_proto_request(
        yarl.URL.build(scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/frs/page", query_string=f"cmd={CMD}"),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=256 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, fname: str, pn: int, rn: int, sort: int, is_good: bool) -> Threads:
    data = pack_proto(fname, pn, rn, sort, is_good)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
