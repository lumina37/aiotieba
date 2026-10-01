import pytest

import aiotieba as tb
from aiotieba import ObjType


@pytest.mark.flaky(reruns=2, reruns_delay=5.0)
@pytest.mark.asyncio(loop_scope="session")
async def test_Ats(client: tb.Client):
    ats = await client.get_ats()

    ##### At #####
    at = ats[0]

    # UserInfo_at
    user = at.user
    assert user.user_id > 0
    assert user.portrait != ""
    assert user.nick_name_new != ""
    assert user.nick_name == user.nick_name_new
    assert user.show_name == user.nick_name_new
    assert user.priv_like != 0
    assert user.priv_reply != 0

    # At
    assert at.text != ""
    assert at.fname != ""
    assert at.fid > 0
    assert at.tid > 0
    assert at.pid > 0
    assert at.author_id == user.user_id
    assert at.obj_type in [ObjType.THREAD, ObjType.POST, ObjType.COMMENT]
    assert at.create_time > 0

    ##### Thread_at #####
    assert at.thread
    assert at.thread.tid == at.tid
    assert at.thread.contents.text != ""
    assert at.thread.user.user_id > 0

    ##### Post_at #####
    comment = next((at for at in ats if at.obj_type == ObjType.COMMENT), None)
    if comment is not None:
        assert comment.post
        assert comment.post.pid > 0
        assert comment.post.user.user_id > 0
