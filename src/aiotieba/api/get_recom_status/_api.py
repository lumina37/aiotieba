from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import TiebaServerError
from ._classdef import RecomStatus

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> RecomStatus:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    status = RecomStatus.from_json(res_json)

    return status


async def request(http_core: HttpCore, fid: int) -> RecomStatus:
    data = [
        ("forum_id", fid),
        ("pn", 1),
        ("rn", 0),
    ]

    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/f/bawu/getRecomThreadList"), data
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
