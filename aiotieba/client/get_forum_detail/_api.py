import yarl

from .._core import HttpCore
from .._helper import pack_form_request, parse_json, send_request
from ..const import APP_BASE_HOST, APP_INSECURE_SCHEME
from ..exception import TiebaServerError
from ._classdef import Forum_detail


def parse_body(body: bytes) -> Forum_detail:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    forum_dict = res_json['forum_info']
    forum = Forum_detail(forum_dict)

    return forum


async def request(http_core: HttpCore, fid: int) -> Forum_detail:
    data = [
        ('_client_version', http_core.core.main_version),
        ('forum_id', fid),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/getforumdetail"),
        data,
    )

    __log__ = "fid={fid}"  # noqa: F841

    body = await send_request(request, http_core.connector, read_bufsize=8 * 1024)
    return parse_body(body)
