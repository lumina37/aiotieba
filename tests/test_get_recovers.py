import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_Recovers(client: tb.Client):
    recovers = await client.get_recovers(21841105)

    ##### Recover #####
    recover = recovers[0]
    assert recover.tid > 0
    assert recover.op_show_name != ''
    assert recover.op_time != 0
