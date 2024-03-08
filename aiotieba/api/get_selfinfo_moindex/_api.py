import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import UserInfo_moindex


def parse_body(body: bytes) -> UserInfo_moindex:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    user_dict = res_json['data']
    user = UserInfo_moindex.from_tbdata(user_dict)

    return user


async def request(http_core: HttpCore) -> UserInfo_moindex:
    params = [('need_user', 1)]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/newmoindex"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=4 * 1024)
    return parse_body(body)
