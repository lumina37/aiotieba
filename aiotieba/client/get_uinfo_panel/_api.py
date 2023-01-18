import aiohttp
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import is_portrait, pack_web_get_request, parse_json, send_request
from ._classdef import UserInfo_panel


async def request(connector: aiohttp.TCPConnector, core: TbCore, name_or_portrait: str) -> bytes:

    if is_portrait(name_or_portrait):
        params = [('id', name_or_portrait)]
    else:
        params = [('un', name_or_portrait)]

    request = pack_web_get_request(
        core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/home/get/panel"),
        params,
    )

    body = await send_request(request, connector, read_bufsize=64 * 1024)

    return body


def parse_body(body: bytes) -> UserInfo_panel:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    user_dict = res_json['data']
    user = UserInfo_panel()._init(user_dict)

    return user
