from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST, LATEST_VERSION
from ...exception import BoolResponse, TiebaServerError
from .protobuf import AddPollReqIdl_pb2, AddPollResIdl_pb2

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ...core import Account, HttpCore, WsCore

CMD = 309006


def parse_body(body: bytes) -> None:
    res_proto = AddPollResIdl_pb2.AddPollResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)


def pack_proto(account: Account, tid: int, options: Iterable[int]) -> bytes:
    req_proto = AddPollReqIdl_pb2.AddPollReqIdl()
    req_proto.data.common.BDUSS = account.BDUSS
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = LATEST_VERSION
    req_proto.data.thread_id = tid
    req_proto.data.options = ",".join(map(str, options))
    req_proto.data.forum_id = 6

    return req_proto.SerializeToString()


async def request_http(http_core: HttpCore, tid: int, options: Iterable[int]) -> BoolResponse:
    data = pack_proto(http_core.account, tid, options)

    request = http_core.pack_proto_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/c/post/addPollPost", query_string=f"cmd={CMD}"),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    return BoolResponse()


async def request_ws(ws_core: WsCore, tid: int, options: Iterable[int]) -> BoolResponse:
    data = pack_proto(ws_core.account, tid, options)

    response = await ws_core.send(data, CMD)
    parse_body(await response.read())

    return BoolResponse()
