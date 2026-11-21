from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...enums import ContentType
from ...exception import BoolResponse, TiebaServerError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ...core import HttpCore
    from ._classdef import RecoverReq


def parse_body(body: bytes) -> None:
    res_json = json.loads(body)
    if code := res_json["no"]:
        raise TiebaServerError(code, res_json["error"])


async def request(http_core: HttpCore, fid: int, fname: str, reqs: Sequence[RecoverReq]) -> BoolResponse:
    data: list[tuple[str, str | int]] = [
        ("tbs", http_core.account.tbs),
        ("fn", fname),
        ("fid", fid),
    ]
    data += [("tid_list[]", req.tid) for req in reqs]
    data += [("pid_list[]", req.pid) for req in reqs]
    data += [("type_list[]", 0 if req.content_type is ContentType.THREAD else 1) for req in reqs]
    data += [("is_frs_mask_list[]", int(req.is_hide)) for req in reqs]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawurecoverthread"), data
    )

    body = await http_core.net_core.send(request)
    parse_body(body)

    return BoolResponse()
