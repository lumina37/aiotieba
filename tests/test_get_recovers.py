import pytest

import aiotieba as tb
from aiotieba import ContentType


@pytest.mark.flaky(reruns=2, reruns_delay=5.0)
@pytest.mark.asyncio
async def test_Recovers(client: tb.Client):
    recovers = await client.get_recovers(21841105)

    ##### Recover #####
    recover = recovers[0]
    assert recover.tid > 0
    assert recover.content_type in [ContentType.THREAD, ContentType.POST, ContentType.COMMENT]
    assert recover.op_show_name != ""
    assert recover.op_time != 0

    ##### Thread_rec #####
    assert recover.thread.tid == recover.tid
    assert recover.thread.title != ""
    assert recover.thread.user.portrait != ""

    ##### Post_rec #####
    if recover.content_type is ContentType.COMMENT:
        assert recover.post.pid > 0
        assert recover.post.text != ""
    else:
        assert not recover.post

    ##### Recover #####
    assert recover.user.portrait != ""
    if recover.content_type is ContentType.THREAD:
        assert recover.pid == 0
    else:
        assert recover.pid > 0
