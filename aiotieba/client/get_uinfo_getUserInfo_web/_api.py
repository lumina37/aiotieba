import sys

import aiohttp
import yarl

from .._core import WEB_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import log_exception, pack_web_get_request, parse_json, send_request
from ._classdef import UserInfo_guinfo_web


def parse_body(body: bytes) -> UserInfo_guinfo_web:
    res_json = parse_json(body)
    if code := res_json['errno']:
        raise TiebaServerError(code, res_json['errmsg'])

    user_dict = res_json['chatUser']
    user = UserInfo_guinfo_web()._init(user_dict)

    return user


async def request(connector: aiohttp.TCPConnector, core: TbCore, user_id: int) -> UserInfo_guinfo_web:

    params = [('chatUid', user_id)]

    request = pack_web_get_request(
        core,
        yarl.URL.build(scheme="http", host=WEB_BASE_HOST, path="/im/pcmsg/query/getUserInfo"),
        params,
    )

    try:
        body = await send_request(request, connector, read_bufsize=2 * 1024)
        user = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"user_id={user_id}")
        user = UserInfo_guinfo_web()._init_null()

    return user
