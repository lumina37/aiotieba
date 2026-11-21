from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST, LATEST_VERSION
from ...exception import BoolResponse, TiebaServerError, TiebaValueError

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> None:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])
    if int(res_json["user_info"]["sign_bonus_point"]) == 0:
        raise TiebaValueError("sign_bonus_point is 0")


async def request(http_core: HttpCore, fname: str) -> BoolResponse:
    data = [
        ("_client_version", LATEST_VERSION),
        ("kw", fname),
    ]

    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/c/forum/sign"), data
    )

    body = await http_core.net_core.send(request)
    parse_body(body)

    return BoolResponse()
