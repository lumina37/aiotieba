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

    blacklist_users = BlacklistUsers.from_tbdata(res_json)

    return blacklist_users


async def request(http_core: HttpCore) -> BlacklistUsers:
    data = [
        ('BDUSS', http_core.account.BDUSS),
        ('_client_version', MAIN_VERSION),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/u/user/userBlackPage"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=32 * 1024)
    return parse_body(body)
