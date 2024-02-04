import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_Comments(client: tb.Client):
    comments = await client.get_comments(8211419000, 146544112004)
    comment = comments[0]

    ##### Forum_c #####
    forum = comments.forum
    assert forum.fid == 37574
    assert forum.fname == 'starry'

    ##### Thread_c #####
    thread = comments.thread

    # UserInfo_ct
    user = thread.user
    assert user.user_id > 0
    assert user.portrait != ''
    assert user.user_name != ''
    assert user.nick_name_new != ''
    assert user.nick_name == user.nick_name_new
    assert user.show_name == user.nick_name_new
    assert user.level > 0

    # Thread_c
    assert thread.title != ''
    assert thread.fid > 0
    assert thread.fname != ''
    assert thread.tid == 8211419000
    assert thread.author_id == user.user_id
    assert thread.reply_num > 0

    ##### Post_c #####
    post = comments.post

    # UserInfo_cp
    user = post.user
    assert user.user_id > 0
    assert user.portrait != ''
    assert user.user_name != ''
    assert user.nick_name_new != ''
    assert user.nick_name == user.nick_name_new
    assert user.show_name == user.nick_name_new
    assert user.level > 0
    assert user.gender > 0
    assert user.priv_like != 0
    assert user.priv_reply != 0

    # Post_c
    assert post.text != ""
    assert post.fid > 0
    assert post.fname != ''
    assert post.tid > 0
    assert post.pid > 0
    assert post.author_id == user.user_id
    assert post.floor > 0
    assert post.create_time > 0

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
    assert frag.duration > 0

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
    assert frag.desc != ''
    assert frag.id == 'image_emoticon3'

    ##### Comment #####
    comment = comments[0]

    # UserInfo_c
    user = comment.user
    assert user.user_id > 0
    assert user.portrait != ''
    assert user.user_name != ''
    assert user.nick_name_new != ''
    assert user.nick_name == user.nick_name_new
    assert user.show_name == user.nick_name_new
    assert user.level > 0
    assert user.gender > 0
    assert user.priv_like != 0
    assert user.priv_reply != 0

    # Comment
    assert comment.text != ""
    assert comment.fid > 0
    assert comment.fname != ''
    assert comment.tid > 0
    assert comment.ppid > 0
    assert comment.pid > 0
    assert comment.author_id == user.user_id
    assert comment.floor > 0
    assert comment.create_time > 0
    assert comment.is_thread_author == (comment.author_id == thread.author_id)

    # FragText
    frag = comment.contents.texts[0]
    assert frag.text != ''

    # FragAt
    frag = comment.contents.ats[0]
    assert frag.text != ''
    assert frag.user_id > 0

    # FragVoice
    frag = comment.contents.voice
    assert frag.md5 != ''
    assert frag.duration > 0

    # FragEmoji
    frag = comment.contents.emojis[0]
    assert frag.desc != ''

    # FragTiebaplus
    frag = comment.contents.tiebapluses[0]
    assert frag.text != ''
    assert frag.url != ''
    frag = comment.contents.tiebapluses[1]
    assert frag.text != ''
    assert frag.url != ''

    comment = comments[1]
    assert comment.reply_to_id != 0


@pytest.mark.flaky(reruns=2, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_FragLink(client: tb.Client):
    comments = await client.get_comments(8211419000, 146546137439)

    ##### Post_c #####
    post = comments.post

    # FragLink
    frag = post.contents.links[0]
    assert frag.title != ''
    assert frag.url.host == "tieba.baidu.com"
    assert frag.is_external is False
    frag = post.contents.links[1]
    assert frag.url.host == "stackoverflow.com"
    assert frag.is_external is True

    ##### Comment #####
    comment = comments[0]

    # FragLink
    frag = comment.contents.links[0]
    assert frag.title != ''
    assert frag.url.host == "tieba.baidu.com"
    assert frag.is_external is False
    frag = comment.contents.links[1]
    assert frag.url.host == "stackoverflow.com"
    assert frag.is_external is True
