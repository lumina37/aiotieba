import yarl

from .._core import HttpCore
from .._helper import is_portrait, pack_web_get_request, parse_json, send_request
from ..const import WEB_BASE_HOST
from ..exception import TiebaServerError
from ._classdef import UserInfo_panel


def parse_body(body: bytes) -> UserInfo_panel:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    user_dict = res_json['data']
    user = UserInfo_panel(user_dict)

    return user


async def request(http_core: HttpCore, name_or_portrait: str) -> UserInfo_panel:
    if is_portrait(name_or_portrait):
        params = [('id', name_or_portrait)]
    else:
        params = [('un', name_or_portrait)]

    request = pack_web_get_request(
        http_core,
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/home/get/panel"),
        params,
    )

    __log__ = "user={name_or_portrait}"  # noqa: F841

    body = await send_request(request, http_core.connector, read_bufsize=64 * 1024)
    return parse_body(body)
