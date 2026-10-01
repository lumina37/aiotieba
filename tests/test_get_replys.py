import pytest

import aiotieba as tb
from aiotieba import ObjType


@pytest.mark.flaky(reruns=2, reruns_delay=5.0)
@pytest.mark.asyncio(loop_scope="session")
async def test_Replys(client: tb.Client):
    replys = await client.get_replys()

    assert replys.err is None
    assert replys.page.current_page == 1
    assert len(replys.objs) > 0

    reply = replys.objs[0]
    assert reply.pid > 0
    assert reply.fname != ""
    assert reply.create_time > 0
    assert reply.user.user_id > 0
    assert reply.user.portrait != ""

    ##### Contents_rep #####
    assert len(reply.contents) > 0
    assert reply.contents.text != ""
    assert reply.contents.text == reply.text

    ##### Thread_rep #####
    assert reply.thread
    assert reply.thread.tid > 0
    assert reply.thread.user.user_id > 0

    ##### ObjType #####
    assert reply.obj_type in [ObjType.POST, ObjType.COMMENT]

    ##### Post_rep #####
    comment = next((reply for reply in replys.objs if reply.obj_type == ObjType.COMMENT), None)
    if comment is not None:
        assert comment.post
        assert comment.post.pid > 0
        assert comment.post.user.user_id > 0
