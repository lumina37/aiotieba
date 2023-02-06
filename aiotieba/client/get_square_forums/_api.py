import sys

import yarl

from .._core import APP_BASE_HOST, HttpCore, TbCore
from .._helper import APP_SECURE_SCHEME, log_exception, pack_proto_request, send_request
from ..exception import TiebaServerError
from ._classdef import SquareForums
from .protobuf import GetForumSquareReqIdl_pb2, GetForumSquareResIdl_pb2

CMD = 309653


def pack_proto(core: TbCore, cname: str, pn: int, rn: int) -> bytes:
    req_proto = GetForumSquareReqIdl_pb2.GetForumSquareReqIdl()
    req_proto.data.common.BDUSS = core._BDUSS
    req_proto.data.common._client_version = core.main_version
    req_proto.data.class_name = cname
    req_proto.data.pn = pn
    req_proto.data.rn = rn

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> SquareForums:
    res_proto = GetForumSquareResIdl_pb2.GetForumSquareResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    square_forums = SquareForums()._init(data_proto)

    return square_forums


async def request_http(http_core: HttpCore, cname: str, pn: int, rn: int) -> SquareForums:

    request = pack_proto_request(
        http_core,
        yarl.URL.build(
            scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/getForumSquare", query_string=f"cmd={CMD}"
        ),
        pack_proto(http_core.core, cname, pn, rn),
    )

    try:
        body = await send_request(request, http_core.connector, read_bufsize=16 * 1024)
        square_forums = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"cname={cname}")
        square_forums = SquareForums()._init_null()

    return square_forums
