from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json["no"]:
        raise TiebaServerError(code, res_json["error"])


async def request(http_core: HttpCore, fid: int, appeal_ids: list[int], refuse: bool) -> BoolResponse:
    data = (
        [
            ("fn", "-"),
            ("fid", fid),
        ]
        + [(f"appeal_list[{i}]", appeal_id) for i, appeal_id in enumerate(appeal_ids)]
        + [
            ("refuse_reason", "_"),
            ("status", 2 if refuse else 1),
            ("tbs", http_core.account.tbs),
        ]
    )

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/multiAppealhandle"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    parse_body(body)

    return BoolResponse()
