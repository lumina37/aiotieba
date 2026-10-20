import pytest

import aiotieba as tb
from aiotieba.const import LATEST_VERSION


@pytest.mark.flaky(reruns=2, reruns_delay=5.0)
@pytest.mark.asyncio
async def test_InitWsInfo(client: tb.Client):
    ##### init_websocket #####
    ok = await client.init_websocket()

    ws_core = client._ws_cores[LATEST_VERSION]

    assert ok
    assert ws_core.status == tb.WsStatus.OPEN

    ##### UserInfo_ws #####
    user = client.account.user

    assert user.user_id > 0
    assert user.user_name != ""
    assert user.portrait.startswith("tb.")

    ##### MidManager #####
    mid_manager = ws_core.mid_manager

    assert mid_manager.priv_gid > 0
    assert len(mid_manager.gid2mid) > 1

    ##### get_self_info #####
    self_info = await client.get_self_info()

    assert self_info.user_id == user.user_id
    assert self_info.tieba_uid > 0
