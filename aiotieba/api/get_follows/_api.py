import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import Follows


def parse_body(body: bytes) -> Follows:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    follows = Follows.from_tbdata(res_json)

    return follows


async def request(http_core: HttpCore, user_id: int, pn: int) -> Follows:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('_client_version', MAIN_VERSION),
        ('pn', pn),
        ('uid', user_id),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/follow/followList"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)
