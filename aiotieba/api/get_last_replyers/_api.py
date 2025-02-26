import yarl

from ...const import APP_BASE_HOST
from ...core import HttpCore, WsCore
from ...exception import TiebaServerError
from ._classdef import Threads_lp
from .protobuf import FrsPageReqIdl4lp_pb2, FrsPageResIdl4lp_pb2

CMD = 301001


def pack_proto(fname: str, pn: int, rn: int, sort: int, is_good: bool) -> bytes:
    req_proto = FrsPageReqIdl4lp_pb2.FrsPageReqIdl4lp()
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = "6.0.1"
    req_proto.data.kw = fname
    req_proto.data.pn = 0 if pn == 1 else pn
    req_proto.data.rn = rn
    req_proto.data.rn_need = rn + 5
    req_proto.data.is_good = is_good
    req_proto.data.sort_type = sort

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Threads_lp:
    res_proto = FrsPageResIdl4lp_pb2.FrsPageResIdl4lp()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    threads = Threads_lp.from_tbdata(data_proto)

    return threads


async def request_http(http_core: HttpCore, fname: str, pn: int, rn: int, sort: int, is_good: bool) -> Threads_lp:
    data = pack_proto(fname, pn, rn, sort, is_good)

    request = http_core.pack_proto_request(
        yarl.URL.build(scheme="http", host=APP_BASE_HOST, path="/c/f/frs/page", query_string=f"cmd={CMD}"),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=256 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, fname: str, pn: int, rn: int, sort: int, is_good: bool) -> Threads_lp:
    data = pack_proto(fname, pn, rn, sort, is_good)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
