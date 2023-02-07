import sys

import yarl

from .._core import WEB_BASE_HOST, HttpCore
from .._helper import log_exception, pack_web_get_request, parse_json, send_request
from ..exception import TiebaValueError
from ._classdef import UserInfo_json


def parse_body(body: bytes) -> UserInfo_json:
    if not body:
        raise TiebaValueError("empty body")

    text = body.decode('utf-8', errors='ignore')
    res_json = parse_json(text)

    user_dict = res_json['creator']
    user = UserInfo_json()._init(user_dict)

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

    try:
        body = await send_request(request, http_core.connector, read_bufsize=2 * 1024)
        user = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"user_name={user_name}")
        user = UserInfo_json()._init_null()

    return user
