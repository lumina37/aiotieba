import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import is_portrait, parse_json
from ._classdef import UserInfo_panel


def parse_body(body: bytes) -> UserInfo_panel:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    user_dict = res_json['data']
    user = UserInfo_panel.from_tbdata(user_dict)

    return user


async def request(http_core: HttpCore, name_or_portrait: str) -> UserInfo_panel:
    if is_portrait(name_or_portrait):
        params = [('id', name_or_portrait)]
    else:
        params = [('un', name_or_portrait)]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/home/get/panel"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
