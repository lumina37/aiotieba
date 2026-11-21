from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST
from ...exception import BoolResponse, TiebaServerError

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> None:
    res_json = json.loads(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])


async def request(http_core: HttpCore, fname: str, fid: int, tid: int, is_vip: bool, is_set: bool) -> BoolResponse:
    data = [
        ("fid", fid),
        ("is_member_top", int(is_vip)),
        ("ntn", "set" if is_set else ""),
        ("word", fname),
        ("z", tid),
    ]

    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/c/bawu/committop"), data
    )

    body = await http_core.net_core.send(request)
    parse_body(body)

    return BoolResponse()
