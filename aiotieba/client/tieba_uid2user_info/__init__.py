import httpx

from ..._exception import TiebaServerError
from ...typedef import UserInfo
from ..common.helper import pack_proto_request
from .protobuf import GetUserByTiebaUidReqIdl_pb2, GetUserByTiebaUidResIdl_pb2


def pack_request(client: httpx.AsyncClient, tieba_uid: int) -> httpx.Request:
    req_proto = GetUserByTiebaUidReqIdl_pb2.GetUserByTiebaUidReqIdl()
    req_proto.data.tieba_uid = str(tieba_uid)
    request = pack_proto_request(
        client, "http://tiebac.baidu.com/c/u/user/getUserByTiebaUid?cmd=309702", req_proto.SerializeToString()
    )

    return request


def parse_response(response: httpx.Response) -> UserInfo:
    res_proto = GetUserByTiebaUidResIdl_pb2.GetUserByTiebaUidResIdl()
    res_proto.ParseFromString(response.content)

    if int(res_proto.error.errorno):
        raise TiebaServerError(res_proto.error.errmsg)

    user_proto = res_proto.data.user
    user = UserInfo(_raw_data=user_proto)

    return user
