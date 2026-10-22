from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

from ...const import CHAT_VERSION
from ...core import CHAT_APPID, CHAT_SDK_VERSION, BLCPLoginError, BLCPMethodID, BLCPServiceID
from ._classdef import LoginIMResult

if TYPE_CHECKING:
    from ...core import BLCPCore


async def request(core: BLCPCore) -> LoginIMResult:
    account = core.account
    method = BLCPMethodID.LOGIN_BY_TOKEN
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

    response = await core.request(BLCPServiceID.IM, method, request_data)
    if response.error_code != 0:
        raise BLCPLoginError(f"IM登录失败 code={response.error_code} text={response.error_text!r}")

    payload = response.payload
    err_code = payload["err_code"]
    if err_code != 0:
        raise BLCPLoginError(f"IM登录失败 err_code={err_code}")

    result = LoginIMResult.from_json(payload)

    return result
