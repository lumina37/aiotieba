import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_Fans(client: tb.Client):
    fans = await client.get_fans(957339815)

    ##### Fan #####
    fan = fans[0]
    assert fan.user_id > 0
    assert fan.portrait != ''
