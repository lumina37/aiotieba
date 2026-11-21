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


async def request(
    http_core: HttpCore, tid: int, pid: int, is_comment: bool, is_disagree: bool, is_undo: bool
) -> BoolResponse:
    if pid:
        content_type = 2 if is_comment else 1
    else:
        content_type = 3

    data = [
        ("agree_type", 5 if is_disagree else 2),
        ("content_type", content_type),
        ("op_type", str(int(is_undo))),
        ("post_id", pid),
        ("thread_id", tid),
    ]

    request = http_core.pack_web_sign_form_request(
        yarl.URL.build(scheme="https", host=APP_BASE_HOST, path="/c/c/agree/opAgree"), data
    )

    body = await http_core.net_core.send(request)
    parse_body(body)

    return BoolResponse()
