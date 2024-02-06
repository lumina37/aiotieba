import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import RecomStatus


def parse_body(body: bytes) -> RecomStatus:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    status = RecomStatus.from_tbdata(res_json)

    return status


async def request(http_core: HttpCore, fid: int) -> RecomStatus:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('_client_version', MAIN_VERSION),
        ('forum_id', fid),
        ('pn', 1),
        ('rn', 0),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/bawu/getRecomThreadList"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    return parse_body(body)
