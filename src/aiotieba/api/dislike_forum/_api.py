from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import BoolResponse, TiebaServerError
from ...helper import pack_json

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> None:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])


async def request(http_core: HttpCore, fid: int) -> BoolResponse:
    data = [
        (
            "dislike",
            pack_json([{"tid": 1, "dislike_ids": 7, "fid": fid, "click_time": int(time.time() * 1000)}]),
        ),
        ("dislike_from", "homepage"),
    ]

    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/c/excellent/submitDislike"), data
    )

    body = await http_core.net_core.send(request)
    parse_body(body)

    return BoolResponse()
