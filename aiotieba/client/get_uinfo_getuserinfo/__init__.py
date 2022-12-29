import httpx

from ..._exception import TiebaServerError
from ..common.helper import pack_proto_request
from ..common.typedef import UserInfo
from .protobuf import GetUserInfoReqIdl_pb2, GetUserInfoResIdl_pb2


def pack_request(client: httpx.AsyncClient, user_id: int) -> httpx.Request:

    req_proto = GetUserInfoReqIdl_pb2.GetUserInfoReqIdl()
    req_proto.data.user_id = user_id

    request = pack_proto_request(
        client,
        "http://tiebac.baidu.com/c/u/user/getuserinfo?cmd=303024",
        req_proto.SerializeToString(),
    )

    return request


def parse_response(response: httpx.Response) -> UserInfo:
    response.raise_for_status()

    res_proto = GetUserInfoResIdl_pb2.GetUserInfoResIdl()
    res_proto.ParseFromString(response.content)

    if error_code := res_proto.error.errorno:
        raise TiebaServerError(error_code, res_proto.error.errmsg)

    user_proto = res_proto.data.user
    user = UserInfo(_raw_data=user_proto)

    return user
