import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_Ats(client: tb.Client):
    ats = await client.get_ats()

    ##### At #####
    at = ats[0]

    # UserInfo_at
    user = at.user
    assert user.user_id > 0
    assert user.portrait != ''
    assert user.nick_name_new != ''
    assert user.nick_name == user.nick_name_new
    assert user.show_name == user.nick_name_new
    assert user.priv_like != 0
    assert user.priv_reply != 0

    # At
    assert at.text != ""
    assert at.fname != ''
    assert at.tid > 0
    assert at.pid > 0
    assert at.author_id == user.user_id
    assert at.create_time > 0
