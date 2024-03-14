import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=5.0)
@pytest.mark.asyncio(scope="session")
async def test_get_user_info(client: tb.Client):
    self_info = await client.get_self_info(tb.ReqUInfo.BASIC)
    assert self_info.user_id > 0
    assert self_info.portrait != ''
    assert self_info.user_name != ''

    self_info = await client.get_self_info()
    assert self_info.user_id > 0
    assert self_info.portrait != ''
    assert self_info.user_name != ''
    assert self_info.nick_name_new != ''
    assert self_info.tieba_uid > 0
    assert self_info.glevel > 0
    assert self_info.age > 0
    assert self_info.ip != ''
    assert self_info.post_num > 0
    assert self_info.priv_like != 0
    assert self_info.priv_reply != 0

    homepage = await client.get_homepage(self_info.user_id)
    user = homepage.user
    assert user.user_id == self_info.user_id
    assert user.portrait == self_info.portrait
    assert user.user_name == self_info.user_name

    user = await client.get_user_info(self_info.portrait, tb.enums.ReqUInfo.BASIC)
    assert user.user_id == self_info.user_id
    assert user.portrait == self_info.portrait
    assert user.user_name == self_info.user_name

    user = await client.get_user_info(user.user_id, tb.enums.ReqUInfo.BASIC)
    assert user.user_id == self_info.user_id
    assert user.portrait == self_info.portrait
    assert user.user_name == self_info.user_name

    user = await client.get_user_info(user.user_name, tb.enums.ReqUInfo.BASIC)
    assert user.user_id == self_info.user_id
    assert user.portrait == self_info.portrait
    assert user.user_name == self_info.user_name

    user = await client.get_user_info(user.portrait)
    assert user.user_id == self_info.user_id
    assert user.portrait == self_info.portrait
    assert user.user_name == self_info.user_name
    assert user.tieba_uid > 0
    assert user.glevel > 0
    assert user.age > 0
    assert user.ip != ''
    assert user.post_num > 0
    assert user.priv_like != 0
    assert user.priv_reply != 0

    user = await client.get_user_info(user.user_id)
    assert user.user_id == self_info.user_id
    assert user.portrait == self_info.portrait
    assert user.user_name == self_info.user_name
    assert user.tieba_uid > 0
    assert user.glevel > 0
    assert user.age > 0
    assert user.ip != ''
    assert user.post_num > 0
    assert user.priv_like != 0
    assert user.priv_reply != 0

    user = await client.tieba_uid2user_info(3356245857)
    assert user.user_id == self_info.user_id
    assert user.portrait == self_info.portrait
    assert user.user_name == self_info.user_name
    assert user.tieba_uid > 0
    assert user.age > 0
