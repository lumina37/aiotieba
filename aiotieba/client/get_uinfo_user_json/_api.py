import aiohttp
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import pack_web_get_request, parse_json, send_request
from ._classdef import UserInfo_json


async def request(connector: aiohttp.TCPConnector, core: TbCore, user_name: str) -> bytes:

    params = [
        ('un', user_name),
        ('ie', 'utf-8'),
    ]

    request = pack_web_get_request(
        core,
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/i/sys/user_json"),
        params,
    )

    body = await send_request(request, connector, read_bufsize=2 * 1024)

    return body


def parse_response(body: bytes) -> UserInfo_json:
    if not body:
        raise TiebaServerError(-1, "empty response")

    text = body.decode('utf-8', errors='ignore')
    res_json = parse_json(text)

    user_dict = res_json['creator']
    user = UserInfo_json()._init(user_dict)

    return user
