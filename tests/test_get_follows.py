import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_Follows(client: tb.Client):
    follows = await client.get_follows(957339815)

    ##### Fan #####
    follow = follows[0]
    assert follow.user_id > 0
    assert follow.portrait != ''
