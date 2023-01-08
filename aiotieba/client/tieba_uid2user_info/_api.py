import httpx

from .._exception import TiebaServerError
from .._helper import APP_BASE_HOST, pack_proto_request, raise_for_status, url
from ._classdef import UserInfo_TUid
from .protobuf import GetUserByTiebaUidReqIdl_pb2, GetUserByTiebaUidResIdl_pb2


def pack_proto(tieba_uid: int) -> bytes:
    req_proto = GetUserByTiebaUidReqIdl_pb2.GetUserByTiebaUidReqIdl()
    req_proto.data.tieba_uid = str(tieba_uid)

    return req_proto.SerializeToString()


def pack_request(client: httpx.AsyncClient, tieba_uid: int) -> httpx.Request:

    request = pack_proto_request(
        client,
        url("http", APP_BASE_HOST, "/c/u/user/getUserByTiebaUid", "cmd=309702"),
        pack_proto(tieba_uid),
    )

    return request


def parse_proto(proto: bytes) -> UserInfo_TUid:
    res_proto = GetUserByTiebaUidResIdl_pb2.GetUserByTiebaUidResIdl()
    res_proto.ParseFromString(proto)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    user_proto = res_proto.data.user
    user = UserInfo_TUid()._init(user_proto)

    return user


def parse_response(response: httpx.Response) -> UserInfo_TUid:
    raise_for_status(response)

    return parse_proto(response.content)
