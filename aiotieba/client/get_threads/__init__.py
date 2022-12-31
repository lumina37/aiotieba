import httpx

from ..._exception import TiebaServerError
from ..common.core import TiebaCore
from ..common.helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ..common.typedef import Threads
from .protobuf import FrsPageReqIdl_pb2, FrsPageResIdl_pb2


def pack_proto(core: TiebaCore, fname: str, pn: int, rn: int, sort: int, is_good: bool) -> bytes:
    req_proto = FrsPageReqIdl_pb2.FrsPageReqIdl()
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = core.main_version
    req_proto.data.fname = fname
    req_proto.data.pn = pn
    req_proto.data.rn = rn if rn > 0 else 1
    req_proto.data.is_good = is_good
    req_proto.data.sort = sort

    return req_proto.SerializeToString()


def pack_request(
    client: httpx.AsyncClient, core: TiebaCore, fname: str, pn: int, rn: int, sort: int, is_good: bool
) -> httpx.Request:
    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/f/frs/page", "cmd=301001"),
        pack_proto(core, fname, pn, rn, sort, is_good),
    )

    return request


def parse_proto(proto: bytes) -> Threads:
    res_proto = FrsPageResIdl_pb2.FrsPageResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    threads = Threads(res_proto.data)

    return threads


def parse_response(response: httpx.Response) -> Threads:
    raise_for_status(response)

    return parse_proto(response.content)
