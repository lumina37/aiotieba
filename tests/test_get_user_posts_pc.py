import pytest

import aiotieba as tb
from aiotieba import ObjType


@pytest.mark.flaky(reruns=2, reruns_delay=5.0)
@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_posts_pc(client: tb.Client):
    user_id = 4954297652
    uposts = await client.get_user_posts_pc(user_id)

    ##### PcUserPost #####
    upost = uposts[0]
    assert len(upost.contents) > 0
    assert upost.fid > 0
    assert upost.tid > 0
    assert upost.pid > 0
    assert upost.obj_type in [ObjType.POST, ObjType.COMMENT]
    assert upost.create_time > 0

    # 以下为PC侧独有 ppid仅在楼中楼有效
    comment = next((p for p in uposts if p.obj_type == ObjType.COMMENT), None)
    if comment is not None:
        assert comment.ppid > 0
        assert comment.ppid != comment.pid

    ##### UserInfo_pcu #####
    user = upost.user
    assert user.user_id == upost.author_id
    assert user.portrait != ""
    assert user.user_name != ""
    assert user.nick_name_new != ""

    # 以下为PC侧独有
    for icon in user.icons:
        assert icon != ""

    ##### Thread_pcup #####
    thread = upost.thread
    assert thread
    assert thread.tid == upost.tid
    assert thread.fid == upost.fid
    assert thread.title != ""
    assert thread.create_time > 0
    assert thread.view_num > 0
    assert thread.reply_num > 0
    assert thread.type != tb.ThreadType.UNKNOWN

    # 以下为PC侧独有
    assert thread.fname != ""
    assert thread.pid > 0
    assert thread.user.user_id > 0
    assert thread.last_time > 0

    ##### Forum_pcup #####
    forum = thread.forum
    assert forum
    assert forum.fid == thread.fid

    # 以下为PC侧独有
    assert forum.fname == thread.fname
