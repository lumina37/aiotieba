from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import BawuTask

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> BawuTask:
    res_json = parse_json(body)
    if code := res_json["no"]:
        raise TiebaServerError(code, res_json["error"])

    bawu_task = BawuTask.from_json(res_json["data"]["bawu_task"])

    return bawu_task


async def request(http_core: HttpCore, fid: int) -> BawuTask:
    params = [
        ("fid", fid),
        ("tbs", http_core.account.tbs),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/bawu/taskInfo"), params
    )

    body = await http_core.net_core.send(request)
    return parse_body(body)
