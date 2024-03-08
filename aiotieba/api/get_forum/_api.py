import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import Forum


def parse_body(body: bytes) -> Forum:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    forum_dict = res_json['forum']
    forum = Forum.from_tbdata(forum_dict)

    return forum


async def request(http_core: HttpCore, fname: str) -> Forum:
    data = [('kw', fname)]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/frs/frsBottom"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)
