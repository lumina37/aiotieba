import sys

import yarl

from .._core import APP_BASE_HOST, HttpCore
from .._helper import APP_SECURE_SCHEME, log_exception, pack_form_request, parse_json, send_request
from ..exception import TiebaServerError
from ._classdef import FollowForums


def parse_body(body: bytes) -> FollowForums:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    follow_forums = FollowForums()._init(res_json)

    return follow_forums


async def request(http_core: HttpCore, user_id: int, pn: int, rn: int) -> FollowForums:

    data = [
        ('BDUSS', http_core.core._BDUSS),
        ('_client_version', http_core.core.main_version),
        ('friend_uid', user_id),
        ('page_no', pn),
        ('page_size', rn),
    ]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/f/forum/like"),
        data,
    )

    try:
        body = await send_request(request, http_core.connector, read_bufsize=16 * 1024)
        follow_forums = parse_body(body)

    except Exception as err:
        log_exception(sys._getframe(1), err, f"user_id={user_id}")
        follow_forums = FollowForums()._init_null()

    return follow_forums
