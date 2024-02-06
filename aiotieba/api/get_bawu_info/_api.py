import yarl

from ...const import APP_BASE_HOST, APP_INSECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore, WsCore
from ...exception import TiebaServerError
from ._classdef import BawuInfo
from .protobuf import GetBawuInfoReqIdl_pb2, GetBawuInfoResIdl_pb2

CMD = 301007


def pack_proto(fid: int) -> bytes:
    req_proto = GetBawuInfoReqIdl_pb2.GetBawuInfoReqIdl()
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.fid = fid

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> BawuInfo:
    res_proto = GetBawuInfoResIdl_pb2.GetBawuInfoResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    bawu_info = BawuInfo.from_tbdata(data_proto)

    return bawu_info


async def request_http(http_core: HttpCore, fid: int) -> BawuInfo:
    data = pack_proto(fid)

    request = http_core.pack_proto_request(
        yarl.URL.build(
            scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/getBawuInfo", query_string=f"cmd={CMD}"
        ),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, fid: int) -> BawuInfo:
    data = pack_proto(ws_core.account, fid)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
