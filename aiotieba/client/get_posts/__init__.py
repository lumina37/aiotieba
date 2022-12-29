import httpx

from ..._exception import TiebaServerError
from ..common.helper import pack_proto_request
from ..common.typedef import Posts
from .protobuf import PbPageReqIdl_pb2, PbPageResIdl_pb2


def pack_request(
    client: httpx.AsyncClient,
    version: str,
    tid: int,
    pn: int,
    rn: int,
    sort: int,
    only_thread_author: bool,
    with_comments: bool,
    comment_sort_by_agree: bool,
    comment_rn: int,
    is_fold: bool,
) -> httpx.Request:

    req_proto = PbPageReqIdl_pb2.PbPageReqIdl()
    req_proto.data.common._client_version = version
    req_proto.data.tid = tid
    req_proto.data.pn = pn
    req_proto.data.rn = rn if rn > 1 else 2
    req_proto.data.sort = sort
    req_proto.data.only_thread_author = only_thread_author
    req_proto.data.is_fold = is_fold
    if with_comments:
        req_proto.data.with_comments = with_comments
        req_proto.data.comment_sort_by_agree = comment_sort_by_agree
        req_proto.data.comment_rn = comment_rn

    request = pack_proto_request(
        client,
        "http://tiebac.baidu.com/c/f/pb/page?cmd=302001",
        req_proto.SerializeToString(),
    )

    return request


def parse_response(response: httpx.Response) -> Posts:
    response.raise_for_status()

    res_proto = PbPageResIdl_pb2.PbPageResIdl()
    res_proto.ParseFromString(response.content)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    posts = Posts(res_proto.data)

    return posts
