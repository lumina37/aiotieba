from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json
from ...helper.crypto import PC_SALT, sign

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])


async def request(http_core: HttpCore, fid: int, tid: int, pid: int, fname: str) -> BoolResponse:
    data: list[tuple[str, str | int]] = [
        ("fid", fid),
        ("z", tid),
        ("pid", pid),
        ("owner_uid", 0),
        ("word", fname),
        ("tbs", http_core.account.tbs),
        ("subapp_type", "pc"),
        ("_client_type", 20),
    ]
    data = sign(data, salt=PC_SALT)

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/c/c/bawu/delpost_pc"), data
    )

    body = await http_core.net_core.send(request)
    parse_body(body)

    return BoolResponse()
