import aiohttp
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import pack_web_get_request, parse_json, send_request
from ._classdef import UserInfo_guinfo_web


async def request(connector: aiohttp.TCPConnector, core: TbCore, user_id: int) -> bytes:

    params = [('chatUid', user_id)]

    request = pack_web_get_request(
        core,
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/im/pcmsg/query/getUserInfo"),
        params,
    )

    body = await send_request(request, connector, read_bufsize=2 * 1024)

    return body


def parse_body(body: bytes) -> UserInfo_guinfo_web:
    res_json = parse_json(body)
    if code := res_json['errno']:
        raise TiebaServerError(code, res_json['errmsg'])

    user_dict = res_json['chatUser']
    user = UserInfo_guinfo_web()._init(user_dict)

    return user
