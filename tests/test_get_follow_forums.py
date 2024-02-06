import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_FollowForums(client: tb.Client):
    forums = await client.get_follow_forums(4954297652)

    ##### FollowForum #####
    forum = forums[0]
    assert forum.fid > 0
    assert forum.fname != ''
    assert forum.level > 0
    assert forum.exp > 0
