from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import TiebaServerError
from ._classdef import Statistics

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> Statistics:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    data_map = res_json["data"]
    stat = Statistics.from_json(data_map)

    return stat


async def request(http_core: HttpCore, fid: int) -> Statistics:
    data = [
        ("forum_id", fid),
    ]

    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/f/forum/getforumdata"), data
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
