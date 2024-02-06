import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import UserInfo_guinfo_web


def parse_body(body: bytes) -> UserInfo_guinfo_web:
    res_json = parse_json(body)
    if code := res_json['errno']:
        raise TiebaServerError(code, res_json['errmsg'])

    user_dict = res_json['chatUser']
    user = UserInfo_guinfo_web.from_tbdata(user_dict)

    return user


async def request(http_core: HttpCore, user_id: int) -> UserInfo_guinfo_web:
    params = [('chatUid', user_id)]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/im/pcmsg/query/getUserInfo"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    return parse_body(body)
