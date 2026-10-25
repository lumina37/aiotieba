from __future__ import annotations

import hashlib
import time
from typing import TYPE_CHECKING

from ...const import CHAT_VERSION
from ...core import CHAT_APPID, LCP_SDK_VERSION
from ...helper import parse_json

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> str:
    res_json = parse_json(body)

    token = res_json["token"]
    return token


async def request(http_core: HttpCore) -> str:
    cuid = http_core.account.cuid_galaxy2
    ts = int(time.time() * 1000)
    data = [
        ("app_id", str(CHAT_APPID)),
        ("app_version", CHAT_VERSION),
        ("cuid", cuid),
        ("device_type", "android"),
        ("manufacture", ""),
        ("model_type", ""),
        ("request_id", str(ts)),
        ("sdk_version", LCP_SDK_VERSION),
        ("sign", hashlib.md5(f"{CHAT_APPID}{cuid}android{ts}".encode()).hexdigest()),
        ("ts", ts),
        ("user_key", ""),
    ]

    request = http_core.pack_pim_request("/rest/5.0/generate_lcm_token", data)

    body = await http_core.net_core.send(request)

    return parse_body(body)
