import yarl

from ...const import APP_BASE_HOST, APP_INSECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
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
        ('_client_version', MAIN_VERSION),
        ('forum_id', fid),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_INSECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/getforumdetail"), data
    )

    __log__ = "fid={fid}"  # noqa: F841

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)
