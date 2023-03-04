import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...exception import TiebaValueError
from ...helper import parse_json
from ...request import pack_web_get_request, send_request
from ._classdef import UserInfo_json


def parse_body(body: bytes) -> UserInfo_json:
    if not body:
        raise TiebaValueError("Empty body")

    text = body.decode('utf-8', errors='ignore')
    res_json = parse_json(text)

    user_dict = res_json['creator']
    user = UserInfo_json(user_dict)

    return user


async def request(http_core: HttpCore, user_name: str) -> UserInfo_json:
    params = [
        ('un', user_name),
        ('ie', 'utf-8'),
    ]

    request = pack_web_get_request(
        http_core,
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/i/sys/user_json"),
        params,
    )

    __log__ = "user_name={user_name}"  # noqa: F841

    body = await send_request(request, http_core.network, read_bufsize=2 * 1024)
    return parse_body(body)
