from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import TiebaServerError
from ._classdef import UserInfo_selfinit

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> UserInfo_selfinit:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    user_dict = res_json["user_info"]
    user = UserInfo_selfinit.from_json(user_dict)

    return user


async def request(http_core: HttpCore) -> UserInfo_selfinit:
    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/s/initNickname"), []
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
