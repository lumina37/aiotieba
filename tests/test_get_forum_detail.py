import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_Forum_detail(client: tb.Client):
    forum = await client.get_forum_detail(21841105)

    ##### Forum_detail #####
    assert forum.fid > 0
    assert forum.fname != ''
    assert forum.small_avatar != ""
    assert forum.origin_avatar != ""
    assert forum.slogan != ""
    assert forum.member_num > 0
    assert forum.post_num > 0
    assert forum.has_bawu is True
