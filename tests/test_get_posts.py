import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_Posts(client: tb.Client):
    posts = await client.get_posts(8211419000)

    ##### Forum_p #####
    forum = posts.forum
    assert forum.fid == 37574
    assert forum.fname == 'starry'
    assert forum.member_num > 0
    assert forum.post_num > 0

    ##### Thread_p #####
    thread = posts.thread

    # UserInfo_pt
    user = thread.user
    assert user.user_id > 0
    assert user.portrait != ''
    assert user.user_name != ''
    assert user.nick_name_new != ''
    assert user.nick_name == user.nick_name_new
    assert user.show_name == user.nick_name_new
    assert user.level > 0
    assert user.glevel > 0
    assert user.ip != ''
    assert user.priv_like != 0
    assert user.priv_reply != 0

    # VoteInfo
    vote_info = thread.vote_info
    assert vote_info.title != ''
    assert vote_info.total_vote > 0
    assert vote_info.total_user > 0
    option = vote_info.options[0]
    assert option.vote_num > 0
    assert option.text != ''

    # Thread_p
    assert thread.text != ''
    assert thread.title != ''
    assert thread.fid > 0
    assert thread.fname != ''
    assert thread.tid > 0
    assert thread.pid == posts[0].pid
    assert thread.author_id == posts[0].user.user_id
    assert thread.view_num > 0
    assert thread.reply_num > 0
    assert thread.share_num > 0
    assert thread.create_time > 0

    ##### Post #####
    assert len(posts) >= 2
    post = posts[1]

    # UserInfo_p
    user = post.user
    assert user.user_id > 0
    assert user.portrait != ''
    assert user.user_name != ''
    assert user.nick_name_new != ''
    assert user.show_name == user.nick_name_new
    assert user.level > 0
    assert user.glevel > 0
    assert user.ip != ''
    assert user.priv_like != 0
    assert user.priv_reply != 0

    # Post
    assert post.text != ''
    assert post.fid > 0
    assert post.fname != ''
    assert post.tid > 0
    assert post.pid > 0
    assert post.author_id == user.user_id
    assert post.floor > 0
    assert post.reply_num > 0
    assert post.create_time > 0
    assert post.is_thread_author == (post.author_id == thread.author_id)

    # FragText
    frag = post.contents.texts[0]
    assert frag.text != ''

    # FragAt
    frag = post.contents.ats[0]
    assert frag.text != ''
    assert frag.user_id > 0

    # FragVoice
    frag = post.contents.voice
    assert frag.md5 != ''

    # FragImage
    frag = post.contents.imgs[0]
    assert frag.src != ''
    assert frag.big_src != ''
    assert frag.origin_src != ''
    assert len(frag.hash) == 40
    assert frag.show_width > 0
    assert frag.show_height > 0

    # FragEmoji
    frag = post.contents.emojis[0]
    assert frag.id == 'image_emoticon3'
    assert frag.desc != ''

    # FragTiebaplus
    frag = post.contents.tiebapluses[0]
    assert frag.text != ''
    assert frag.url != ''
    frag = post.contents.tiebapluses[1]
    assert frag.text != ''
    assert frag.url != ''

    # FragLink
    post = posts[2]
    frag = post.contents.links[0]
    assert frag.title != ''
    assert frag.url.host == "tieba.baidu.com"
    assert frag.is_external is False
    frag = post.contents.links[1]
    assert frag.url.host == "stackoverflow.com"
    assert frag.is_external is True

    # Posts with video
    posts = await client.get_posts(6205407601)

    # FragVideo
    frag = posts.thread.contents.video
    assert frag.src != ''
    assert frag.cover_src != ''
    assert frag.duration > 0
    assert frag.width > 0
    assert frag.height > 0
    assert frag.view_num > 0


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_ShareThread_pt(client: tb.Client):
    posts = await client.get_posts(8213449397)

    ##### ShareThread_pt #####
    sthread = posts.thread.share_origin
    assert sthread.text != ''
    assert sthread.title != ''
    assert sthread.author_id > 0
    assert sthread.fid == 37574
    assert sthread.fname == 'starry'
    assert sthread.tid > 0

    # VoteInfo
    vote_info = sthread.vote_info
    assert vote_info.title != ''
    assert vote_info.total_vote > 0
    assert vote_info.total_user > 0
    option = vote_info.options[0]
    assert option.vote_num > 0
    assert option.text != ''

    # FragText
    frag = sthread.contents.texts[1]
    assert frag.text != ''

    # FragAt
    frag = sthread.contents.ats[0]
    assert frag.text != ''
    assert frag.user_id > 0

    # FragVoice
    frag = sthread.contents.voice
    assert frag.md5 != ''
    assert frag.duration > 0

    # FragImage
    frag = sthread.contents.imgs[0]
    assert frag.src != ''
    assert frag.big_src != ''
    assert frag.origin_src != ''
    assert len(frag.hash) == 40
    assert frag.show_width > 0
    assert frag.show_height > 0

    # FragLink
    frag = sthread.contents.links[0]
    assert frag.title != ''
    assert frag.url.host == "tieba.baidu.com"
    assert frag.is_external is False
