from typing import Dict, List

import httpx

from .._classdef.core import TiebaCore
from .._exception import TiebaServerError
from .._helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ._classdef import UserInfo_bawu
from .protobuf import GetBawuInfoReqIdl_pb2, GetBawuInfoResIdl_pb2


def pack_proto(core: TiebaCore, fid: int) -> bytes:
    req_proto = GetBawuInfoReqIdl_pb2.GetBawuInfoReqIdl()
    req_proto.data.common._client_version = core.main_version
    req_proto.data.fid = fid

    return req_proto.SerializeToString()


def pack_request(client: httpx.AsyncClient, core: TiebaCore, fid: int) -> httpx.Request:

    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/f/forum/getBawuInfo", "cmd=301007"),
        pack_proto(core, fid),
    )

    return request


def parse_proto(proto: bytes) -> Dict[str, List[UserInfo_bawu]]:
    res_proto = GetBawuInfoResIdl_pb2.GetBawuInfoResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    rdes_protos = res_proto.data.bawu_team_info.bawu_team_list
    bawu_dict = {
        rdes_proto.role_name: [UserInfo_bawu()._init(p) for p in rdes_proto.role_info] for rdes_proto in rdes_protos
    }

    return bawu_dict


def parse_response(response: httpx.Response) -> Dict[str, List[UserInfo_bawu]]:
    raise_for_status(response)

    return parse_proto(response.content)
