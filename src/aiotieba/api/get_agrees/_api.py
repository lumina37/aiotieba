from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST, LATEST_VERSION
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import Agrees

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> Agrees:
    res_json = parse_json(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    agrees = Agrees.from_json(res_json)

    return agrees


async def request(http_core: HttpCore, last_agree_id: int, rn: int) -> Agrees:
    data = [
        ("BDUSS", http_core.account.BDUSS),
        ("_client_version", LATEST_VERSION),
        ("id", last_agree_id),
        ("rn", rn),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/u/feed/agreeme"), data
    )

    body = await http_core.net_core.send(request)

    return parse_body(body)
