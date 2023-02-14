from typing import Dict, List

import yarl

from .._core import HttpCore, TbCore, WsCore
from .._helper import pack_proto_request, send_request
from ..const import APP_BASE_HOST, APP_INSECURE_SCHEME
from ..exception import TiebaServerError
from ._classdef import UserInfo_bawu
from .protobuf import GetBawuInfoReqIdl_pb2, GetBawuInfoResIdl_pb2

CMD = 301007


def pack_proto(core: TbCore, fid: int) -> bytes:
    req_proto = GetBawuInfoReqIdl_pb2.GetBawuInfoReqIdl()
    req_proto.data.common._client_version = core.main_version
    req_proto.data.fid = fid

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Dict[str, List[UserInfo_bawu]]:
    res_proto = GetBawuInfoResIdl_pb2.GetBawuInfoResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    rdes_protos = res_proto.data.bawu_team_info.bawu_team_list
    bawu_dict = {rdes_proto.role_name: [UserInfo_bawu(p) for p in rdes_proto.role_info] for rdes_proto in rdes_protos}

    return bawu_dict


async def request_http(http_core: HttpCore, fid: int) -> Dict[str, List[UserInfo_bawu]]:
    data = pack_proto(http_core.core, fid)

    request = pack_proto_request(
        http_core,
        yarl.URL.build(
            scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/getBawuInfo", query_string=f"cmd={CMD}"
        ),
        data,
    )

    __log__ = "fid={fid}"  # noqa: F841

    body = await send_request(request, http_core.connector, read_bufsize=8 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, fid: int) -> Dict[str, List[UserInfo_bawu]]:
    data = pack_proto(ws_core.core, fid)

    __log__ = "fid={fid}"  # noqa: F841

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
