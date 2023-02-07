import sys

import yarl

from .._core import APP_BASE_HOST, HttpCore, TbCore
from .._helper import APP_SECURE_SCHEME, log_exception, pack_proto_request, send_request
from ..exception import TiebaServerError
from ._classdef import Posts
from .protobuf import PbPageReqIdl_pb2, PbPageResIdl_pb2

CMD = 302001


def pack_proto(
    core: TbCore,
    tid: int,
    pn: int,
    rn: int,
    sort: int,
    only_thread_author: bool,
    with_comments: bool,
    comment_sort_by_agree: bool,
    comment_rn: int,
    is_fold: bool,
) -> bytes:
    req_proto = PbPageReqIdl_pb2.PbPageReqIdl()
    req_proto.data.common._client_type = 2
    req_proto.data.common._client_version = core.main_version
    req_proto.data.tid = tid
    req_proto.data.pn = pn
    req_proto.data.rn = rn if rn > 1 else 2
    req_proto.data.sort = sort
    req_proto.data.only_thread_author = only_thread_author
    req_proto.data.is_fold = is_fold
    if with_comments:
        req_proto.data.common.BDUSS = core._BDUSS
        req_proto.data.with_comments = with_comments
        req_proto.data.comment_sort_by_agree = comment_sort_by_agree
        req_proto.data.comment_rn = comment_rn

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> Posts:
    res_proto = PbPageResIdl_pb2.PbPageResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    posts = Posts()._init(data_proto)

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
    is_fold: bool,
) -> Posts:

    request = pack_proto_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/pb/page", query_string=f"cmd={CMD}"),
        pack_proto(
            http_core.core,
            tid,
            pn,
            rn,
            sort,
            only_thread_author,
            with_comments,
            comment_sort_by_agree,
            comment_rn,
            is_fold,
        ),
    )

    try:
        body = await send_request(request, http_core.connector, read_bufsize=128 * 1024)
        posts = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"tid={tid}")
        posts = Posts()._init_null()

    return posts
