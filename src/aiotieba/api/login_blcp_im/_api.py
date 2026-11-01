from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

from ...const import CHAT_VERSION
from ...core import CHAT_APPID, CHAT_SDK_VERSION, BlcpLoginError, BlcpMethodID, BlcpRequest, BlcpServiceID, JsonBody
from ._classdef import LoginIMResult

if TYPE_CHECKING:
    from ...core import BlcpCore


async def request(core: BlcpCore) -> LoginIMResult:
    account = core.account
    method = BlcpMethodID.LOGIN_BY_TOKEN
    request_data = {
        "method": method,
        "appid": CHAT_APPID,
        "device_id": "android_" + account.cuid_galaxy2,
        "account_type": 1,
        "token": account.BDUSS,
        "version": 4,
        "sdk_version": CHAT_SDK_VERSION,
        "app_version": CHAT_VERSION,
        "app_open_type": 0,
        "client_identifier": json.dumps({"zid": "", "version_code": ""}),
        "tail": 0,
        "timeout": 10,
        "cookie": "",
        "device_info": {
            "app_version": CHAT_VERSION,
            "os_version": "32",
            "platform": "android",
            "appid": str(CHAT_APPID),
            "from": "1008550l",
            "cfrom": "1008550l",
        },
        "rpc": json.dumps({"rpc_retry_time": 0}),
        "user_type": 0,
        "client_logid": int(time.time() * 1_000_000),
    }

    request = BlcpRequest.create(BlcpServiceID.IM, method, JsonBody(request_data))
    response = await core.send(request)
    if response.error_code != 0:
        raise BlcpLoginError(f"IM login failed: code={response.error_code} text={response.error_text!r}")

    payload = response.payload
    err_code = payload["err_code"]
    if err_code != 0:
        raise BlcpLoginError(f"IM login failed: err_code={err_code}")

    result = LoginIMResult.from_json(payload)

    return result
