import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import Account, HttpCore, WsCore
from ...exception import TiebaServerError
from ._classdef import Posts
from .protobuf import PbPageReqIdl_pb2, PbPageResIdl_pb2

CMD = 302001


def pack_proto(
    account: Account,
    tid: int,
    pn: int,
    rn: int,
    sort: int,
    only_thread_author: bool,
    with_comments: bool,
    comment_sort_by_agree: bool,
    comment_rn: int,
) -> bytes:
    req_proto = PbPageReqIdl_pb2.PbPageReqIdl()
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.kz = tid
    req_proto.data.pn = pn
    req_proto.data.rn = rn if rn > 1 else 2
    req_proto.data.r = sort
    req_proto.data.lz = only_thread_author
    if with_comments:
        req_proto.data.common.BDUSS = account.BDUSS
        req_proto.data.with_floor = with_comments
        req_proto.data.floor_sort_type = comment_sort_by_agree
        req_proto.data.floor_rn = comment_rn

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Posts:
    res_proto = PbPageResIdl_pb2.PbPageResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    posts = Posts.from_tbdata(data_proto)

    return posts


async def request_http(
    http_core: HttpCore,
    tid: int,
    pn: int,
    rn: int,
    sort: int,
    only_thread_author: bool,
    with_comments: bool,
    comment_sort_by_agree: bool,
    comment_rn: int,
) -> Posts:
    data = pack_proto(
        http_core.account,
        tid,
        pn,
        rn,
        sort,
        only_thread_author,
        with_comments,
        comment_sort_by_agree,
        comment_rn,
    )

    request = http_core.pack_proto_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/pb/page", query_string=f"cmd={CMD}"),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=128 * 1024)
    return parse_body(body)


async def request_ws(
    ws_core: WsCore,
    tid: int,
    pn: int,
    rn: int,
    sort: int,
    only_thread_author: bool,
    with_comments: bool,
    comment_sort_by_agree: bool,
    comment_rn: int,
) -> Posts:
    data = pack_proto(
        ws_core.account,
        tid,
        pn,
        rn,
        sort,
        only_thread_author,
        with_comments,
        comment_sort_by_agree,
        comment_rn,
    )

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
