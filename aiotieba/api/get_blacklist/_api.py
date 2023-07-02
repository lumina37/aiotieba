import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME, MAIN_VERSION
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import BlacklistUsers


def parse_body(body: bytes) -> BlacklistUsers:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    blacklistusers = BlacklistUsers(res_json)

    return blacklistusers


async def request(http_core: HttpCore, pn: int) -> BlacklistUsers:
    data = [
        ('BDUSS', http_core.account._BDUSS),
        ('_client_version', MAIN_VERSION),
        ('pn', pn),
        ('rn', 30),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/user/userBlackPage"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    return parse_body(body)
