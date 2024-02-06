import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaValueError
from ...helper import parse_json
from ._classdef import UserInfo_json


def parse_body(body: bytes) -> UserInfo_json:
    if not body:
        raise TiebaValueError("Empty body")

    text = body.decode('utf-8', errors='ignore')
    res_json = parse_json(text)

    user_dict = res_json['creator']
    user = UserInfo_json.from_tbdata(user_dict)

    return user


async def request(http_core: HttpCore, user_name: str) -> UserInfo_json:
    params = [
        ('un', user_name),
        ('ie', 'utf-8'),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/i/sys/user_json"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    return parse_body(body)
