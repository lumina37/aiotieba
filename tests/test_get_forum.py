import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=5.0)
@pytest.mark.asyncio(loop_scope="session")
async def test_Forum(client: tb.Client):
    fname = "starry"
    forum = await client.get_forum(fname)

    ##### Forum #####
    assert forum.fid == 37574
    assert forum.fname == fname
    assert forum.category != ""
    assert forum.subcategory != ""
    assert forum.small_avatar != ""
    assert forum.slogan != ""
    assert forum.member_num > 0
    assert forum.post_num > 0
    assert forum.thread_num > 0
    assert forum.has_bawu is True

    ##### BawuInfo_f #####
    assert len(forum.admins) > 0

    admin = forum.admins[0]
    assert admin.user_id > 0
    assert admin.portrait != ""
    assert admin.user_name != ""
    assert bool(admin) is True
    assert str(admin) != ""
    assert admin.log_name != ""
