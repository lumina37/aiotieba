import httpx

from ..._exception import TiebaServerError
from ..common.helper import pack_proto_request
from ..common.typedef import Replys
from .protobuf import ReplyMeReqIdl_pb2, ReplyMeResIdl_pb2


def pack_request(client: httpx.AsyncClient, bduss: str, version: str, pn: int) -> httpx.Request:

    req_proto = ReplyMeReqIdl_pb2.ReplyMeReqIdl()
    req_proto.data.common.BDUSS = bduss
    req_proto.data.common._client_version = version
    req_proto.data.pn = str(pn)

    request = pack_proto_request(
        client,
        "http://tiebac.baidu.com/c/u/feed/replyme?cmd=303007",
        req_proto.SerializeToString(),
    )

    return request


def parse_response(response: httpx.Response) -> Replys:
    response.raise_for_status()

    res_proto = ReplyMeResIdl_pb2.ReplyMeResIdl()
    res_proto.ParseFromString(response.content)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    replys = Replys(res_proto.data)

    return replys
