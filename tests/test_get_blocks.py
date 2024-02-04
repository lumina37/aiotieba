import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_Blocks(client: tb.Client):
    blocks = await client.get_blocks(21841105)

    ##### Block #####
    block = blocks[0]
    assert block.user_id > 0
    assert block.day in [1, 3, 10]
