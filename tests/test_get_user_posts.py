import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=5.0)
@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_posts(client: tb.Client):
    user_id = 4954297652
    postss = await client.get_user_posts(user_id)

    ##### UserPosts #####
    posts = postss[0]
    assert posts.fid > 0
    assert posts.tid > 0

    ##### UserPost #####
    post = posts[0]
    assert len(post.contents) > 0
    assert post.fid > 0
    assert post.tid > 0
    assert post.pid > 0
    assert post.create_time > 0

    ##### UserInfo_u #####
    user = post.user
    assert user.user_id == post.author_id
    assert user.portrait != ''
    assert user.user_name != ''
    assert user.nick_name_new != ''
