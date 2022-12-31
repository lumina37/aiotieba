from typing import Dict, List

import httpx

from ..._exception import TiebaServerError
from ..common.core import TiebaCore
from ..common.helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ..common.typedef import UserInfo
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


def _parse_user_info(proto) -> UserInfo:
    user = UserInfo()
    user.user_id = proto.id
    user.portrait = proto.portrait
    user._user_name = proto.name
    user.nick_name = proto.name_show
    user._level = proto.user_level
    return user


def parse_proto(proto: bytes) -> Dict[str, List[UserInfo]]:
    res_proto = GetBawuInfoResIdl_pb2.GetBawuInfoResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    roledes_protos = res_proto.data.bawu_team_info.bawu_team_list
    bawu_dict = {
        roledes_proto.role_name: [_parse_user_info(roleinfo_proto) for roleinfo_proto in roledes_proto.role_info]
        for roledes_proto in roledes_protos
    }

    return bawu_dict


def parse_response(response: httpx.Response) -> Dict[str, List[UserInfo]]:
    raise_for_status(response)

    return parse_proto(response.content)
