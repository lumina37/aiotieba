import yarl

from ...const import APP_BASE_HOST, APP_INSECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore, WsCore
from ...exception import TiebaServerError
from ._classdef import Forum_detail
from .protobuf import GetForumDetailReqIdl_pb2, GetForumDetailResIdl_pb2

CMD = 303021


def pack_proto(fid: int) -> bytes:
    req_proto = GetForumDetailReqIdl_pb2.GetForumDetailReqIdl()
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.forum_id = fid

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Forum_detail:
    res_proto = GetForumDetailResIdl_pb2.GetForumDetailResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    forum = Forum_detail.from_tbdata(data_proto)

    return forum


async def request_http(http_core: HttpCore, fid: int) -> Forum_detail:
    data = pack_proto(fid)

    request = http_core.pack_proto_request(
        yarl.URL.build(
            scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/getforumdetail", query_string=f"cmd={CMD}"
        ),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=4 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, fid: int) -> Forum_detail:
    data = pack_proto(fid)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
