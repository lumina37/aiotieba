from __future__ import annotations

import random
import time
from sys import maxsize as LONG_MAX
from typing import TYPE_CHECKING

from ...api._protobuf import Lcm_pb2
from ...const import CHAT_VERSION
from ...core import (
    BLCP_SDK_VERSION,
    CHAT_APPID,
    BlcpLoginError,
    BlcpMethodID,
    BlcpRequest,
    BlcpServiceID,
    ProtoLcmBody,
)

if TYPE_CHECKING:
    from ...core import BlcpCore


async def request(core: BlcpCore, token: str) -> int:
    correlation_id = random.randint(0, LONG_MAX)

    rpc_data = Lcm_pb2.RpcData()
    lcm_request = rpc_data.lcm_request
    lcm_request.log_id = correlation_id
    lcm_request.token = token
    lcm_request.timestamp = int(time.time() * 1000)
    lcm_request.start_type = -1
    lcm_request.conn_type = 1
    common = lcm_request.common
    common.cuid = core.account.cuid_galaxy2
    common.device = "android"
    common.app_id = str(CHAT_APPID)
    common.app_version = CHAT_VERSION
    common.sdk_version = BLCP_SDK_VERSION
    common.network = "wifi"
    body = ProtoLcmBody.from_proto(rpc_data)

    request = BlcpRequest.create(BlcpServiceID.LCM, BlcpMethodID.LOGIN, body, correlation_id=correlation_id)

    response = await core.send(request)
    if not response.ok:
        raise BlcpLoginError(f"BLCP握手失败 code={response.error_code} text={response.error_text!r}")

    return response.lcm.next_interval_ms
