import yarl

from ...const import APP_BASE_HOST, MAIN_VERSION
from ...core import Account, HttpCore, WsCore
from ...exception import TiebaServerError
from ._classdef import LevelInfo
from .protobuf import GetLevelInfoReqIdl_pb2, GetLevelInfoResIdl_pb2

CMD = 301005


def pack_proto(account: Account, fid: int) -> bytes:
    req_proto = GetLevelInfoReqIdl_pb2.GetLevelInfoReqIdl()
    req_proto.data.common.BDUSS = account.BDUSS
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.forum_id = fid

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> LevelInfo:
    res_proto = GetLevelInfoResIdl_pb2.GetLevelInfoResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    level_info = LevelInfo.from_tbdata(data_proto)

    return level_info


async def request_http(http_core: HttpCore, forum_id: int) -> LevelInfo:
    data = pack_proto(http_core.account, forum_id)

    request = http_core.pack_proto_request(
        yarl.URL.build(scheme="http", host=APP_BASE_HOST, path="/c/f/forum/getLevelInfo", query_string=f"cmd={CMD}"),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, forum_id: int) -> LevelInfo:
    data = pack_proto(ws_core.account, forum_id)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
