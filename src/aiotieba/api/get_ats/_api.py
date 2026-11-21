from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import TiebaServerError
from ._classdef import Ats

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> Ats:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    ats = Ats.from_json(res_json)

    return ats


async def request(http_core: HttpCore, pn: int) -> Ats:
    data = [
        ("pn", pn),
    ]

    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/u/feed/atme"), data
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
