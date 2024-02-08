import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_Homepage(client: tb.Client):
    homepage = await client.get_homepage(957339815)

    ##### Thread_pf #####
    thread = homepage[0]
    assert len(thread.contents) > 0
    assert thread.fid > 0
    assert thread.fname != ''
    assert thread.tid > 0
    assert thread.pid > 0
    assert thread.author_id == thread.user.user_id
    assert thread.view_num > 0
    assert thread.create_time > 0

    ##### UserInfo_pf #####
    user = homepage.user
    assert user.user_id == thread.user.user_id
    assert user.user_id > 0
    assert user.portrait != ''
    assert user.user_name != ''
    assert user.nick_name_new != ''
    assert user.tieba_uid > 0
    assert user.glevel > 0
    assert user.gender != tb.Gender.UNKNOWN
    assert user.age > 0.0
    assert user.post_num > 0
    assert user.agree_num > 0
    assert user.fan_num > 0
    assert user.follow_num > 0
    assert user.forum_num > 0
    assert user.ip != ''
