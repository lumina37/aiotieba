from __future__ import annotations

import random
import time
from sys import maxsize as LONG_MAX
from typing import TYPE_CHECKING

from ...const import CHAT_VERSION
from ...core import (
    CHAT_APPID,
    LCP_SDK_VERSION,
    BLCPLoginError,
    BLCPMethodID,
    BLCPRequest,
    BLCPServiceID,
    LcmBody,
)

if TYPE_CHECKING:
    from ...core import BLCPCore


async def request(core: BLCPCore, token: str) -> int:
    correlation_id = random.randint(0, LONG_MAX)
    body = LcmBody.login(
        log_id=correlation_id,
        token=token,
        timestamp=int(time.time() * 1000),
        cuid=core.account.cuid_galaxy2,
        app_id=CHAT_APPID,
        app_version=CHAT_VERSION,
        sdk_version=LCP_SDK_VERSION,
    )
    request = BLCPRequest.create(BLCPServiceID.LCM, BLCPMethodID.LOGIN, body, correlation_id=correlation_id)

    response = await core.send(request)
    if not response.ok:
        raise BLCPLoginError(f"LCP握手失败 code={response.error_code} text={response.error_text!r}")

    return response.lcm.next_interval_ms
