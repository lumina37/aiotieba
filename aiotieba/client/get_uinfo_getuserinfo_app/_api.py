import httpx

from .._exception import TiebaServerError
from .._helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ._classdef import UserInfo_guinfo_app
from .protobuf import GetUserInfoReqIdl_pb2, GetUserInfoResIdl_pb2


def pack_proto(user_id: int) -> bytes:
    req_proto = GetUserInfoReqIdl_pb2.GetUserInfoReqIdl()
    req_proto.data.user_id = user_id

    return req_proto.SerializeToString()


def pack_request(client: httpx.AsyncClient, user_id: int) -> httpx.Request:
    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/u/user/getuserinfo", "cmd=303024"),
        pack_proto(user_id),
    )

    return request


def parse_proto(proto: bytes) -> UserInfo_guinfo_app:
    res_proto = GetUserInfoResIdl_pb2.GetUserInfoResIdl()
    res_proto.ParseFromString(proto)

    if error_code := res_proto.error.errorno:
        raise TiebaServerError(error_code, res_proto.error.errmsg)

    user_proto = res_proto.data.user
    user = UserInfo_guinfo_app()._init(user_proto)

    return user


def parse_response(response: httpx.Response) -> UserInfo_guinfo_app:
    raise_for_status(response)

    return parse_proto(response.content)
