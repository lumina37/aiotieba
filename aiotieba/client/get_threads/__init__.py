import httpx

from ..._exception import TiebaServerError
from ..common.helper import pack_proto_request
from ..common.typedef import Threads
from .protobuf import FrsPageReqIdl_pb2, FrsPageResIdl_pb2


def pack_request(
    client: httpx.AsyncClient, version: str, fname: str, pn: int, rn: int, sort: int, is_good: bool
) -> httpx.Request:

    req_proto = FrsPageReqIdl_pb2.FrsPageReqIdl()
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = version
    req_proto.data.fname = fname
    req_proto.data.pn = pn
    req_proto.data.rn = rn if rn > 0 else 1
    req_proto.data.is_good = is_good
    req_proto.data.sort = sort

    request = pack_proto_request(
        client,
        "http://tiebac.baidu.com/c/f/frs/page?cmd=301001",
        req_proto.SerializeToString(),
    )

    return request


def parse_response(response: httpx.Response) -> Threads:
    response.raise_for_status()

    res_proto = FrsPageResIdl_pb2.FrsPageResIdl()
    res_proto.ParseFromString(response.content)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    threads = Threads(res_proto.data)

    return threads
