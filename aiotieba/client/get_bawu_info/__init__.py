from typing import Dict, List

import httpx

from ..._exception import TiebaServerError
from ..common.helper import pack_proto_request
from ..common.typedef import UserInfo
from .protobuf import GetBawuInfoReqIdl_pb2, GetBawuInfoResIdl_pb2


def pack_request(client: httpx.AsyncClient, version: str, fid: int) -> httpx.Request:

    req_proto = GetBawuInfoReqIdl_pb2.GetBawuInfoReqIdl()
    req_proto.data.common._client_version = version
    req_proto.data.fid = fid

    request = pack_proto_request(
        client,
        "http://tiebac.baidu.com/c/f/forum/getBawuInfo?cmd=301007",
        req_proto.SerializeToString(),
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


def parse_response(response: httpx.Response) -> Dict[str, List[UserInfo]]:
    response.raise_for_status()

    res_proto = GetBawuInfoResIdl_pb2.GetBawuInfoResIdl()
    res_proto.ParseFromString(response.content)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    roledes_protos = res_proto.data.bawu_team_info.bawu_team_list
    bawu_dict = {
        roledes_proto.role_name: [_parse_user_info(roleinfo_proto) for roleinfo_proto in roledes_proto.role_info]
        for roledes_proto in roledes_protos
    }

    return bawu_dict
