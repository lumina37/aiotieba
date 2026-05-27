from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...exception import TiebaServerError
from ...helper import parse_json
from ...helper.crypto import PC_SALT, sign
from ._classdef import UserInfo_uc

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> UserInfo_uc:
    res_json = parse_json(body)
    if code := res_json["error_code"]:
        raise TiebaServerError(code, res_json["error_msg"])

    data_map = res_json["data"]["user_info"]
    user = UserInfo_uc.from_json(data_map)

    return user


async def request(http_core: HttpCore, portrait: str) -> UserInfo_uc:
    params = [
        ("portrait", portrait),
        ("subapp_type", "pc"),
        ("_client_type", 20),
    ]
    params = sign(params, salt=PC_SALT)

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/c/u/pc/userCard"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)
