from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import TiebaServerError
from ._classdef import BlacklistUsers

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> BlacklistUsers:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    blacklist_users = BlacklistUsers.from_json(res_json)

    return blacklist_users


async def request(http_core: HttpCore) -> BlacklistUsers:
    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/u/user/userBlackPage"), []
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
