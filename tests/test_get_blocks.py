import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=5.0)
@pytest.mark.asyncio
async def test_Blocks(client: tb.Client):
    blocks = await client.get_blocks(21841105)

    ##### Block #####
    block = blocks[0]
    assert block.user_id > 0
    assert block.day > 0
    assert block.nick_name_new != ""
    assert block.block_time.year > 2000
