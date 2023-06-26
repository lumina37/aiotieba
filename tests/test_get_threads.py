import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=3, reruns_delay=2.0)
@pytest.mark.asyncio
async def test_Threads(client: tb.Client):
    fname = "starry"
    threads = await client.get_threads(fname)

    ##### Forum_t #####
    forum = threads.forum
    assert forum.fid == 37574
    assert forum.fname == fname
    assert forum.member_num > 0
    assert forum.post_num > 0
    assert forum.thread_num > 0
    assert forum.has_bawu is True
    assert forum.has_rule is False

    ##### Thread #####
    assert len(threads) >= 2
    for thread in threads:
        # Normal Thread
        if thread.tid == 8211419000:
            # UserInfo_t
            user = thread.user
            assert user.user_id > 0
            assert user.portrait != ''
            assert user.user_name != ''
            assert user.nick_name_new != ''
            assert user.nick_name == user.nick_name_new
            assert user.show_name == user.nick_name_new
            assert user.level > 0
            assert user.glevel > 0
            assert user.priv_like != 0
            assert user.priv_reply != 0

            # VoteInfo
            vote_info = thread.vote_info
            assert vote_info.title != ''
            option = vote_info.options[0]
            assert option.vote_num > 0
            assert option.text != ''

            # Thread
            assert thread.text != ""
            assert thread.title != ''
            assert thread.fid > 0
            assert thread.fname != ''
            assert thread.pid > 0
            assert thread.author_id == user.user_id
            assert thread.view_num > 0
            assert thread.reply_num > 0
            assert thread.create_time > 0
            assert thread.last_time > 0

            # FragText
            frag = thread.contents.texts[0]
            assert frag.text != ''

            # FragAt
            frag = thread.contents.ats[0]
            assert frag.text != ''
            assert frag.user_id > 0

            # FragVoice
            assert thread.contents.has_voice is True

            # FragImage
            frag = thread.contents.imgs[0]
            assert frag.src != ''
            assert frag.big_src != ''
            assert frag.origin_src != ''
            assert len(frag.hash) == 40
            assert frag.show_width > 0
            assert frag.show_height > 0

            # FragEmoji
            frag = thread.contents.emojis[0]
            assert frag.desc != ''

            # FragTiebaplus
            frag = thread.contents.tiebapluses[0]
            assert frag.text != ''
            assert frag.url != ''
            frag = thread.contents.tiebapluses[1]
            assert frag.text != ''
            assert frag.url != ''

            # FragLink
            frag = thread.contents.links[0]
            assert frag.title != ''
            assert frag.url.host == "tieba.baidu.com"
            assert frag.is_external is False
            frag = thread.contents.links[1]
            assert frag.url.host == "stackoverflow.com"
            assert frag.is_external is True

        # Share Thread
        elif thread.tid == 7905926315:
            sthread = thread.share_origin

            # FragText
            frag = sthread.contents.texts[0]
            assert frag.text != ''

            # FragAt
            frag = sthread.contents.ats[0]
            assert frag.text != ''
            assert frag.user_id != 0

            # FragLink
            frag = sthread.contents.links[0]
            assert frag.title != ''
            assert frag.url.host == "tieba.baidu.com"
            assert frag.is_external is False

            # FragVoice
            assert sthread.contents.has_voice is True

            # FragImage
            frag = sthread.contents.imgs[0]
            assert frag.src != ''
            assert frag.big_src != ''
            assert frag.origin_src != ''
            assert len(frag.hash) == 40
            assert frag.show_width > 0
            assert frag.show_height > 0

            # VoteInfo
            vote_info = sthread.vote_info
            assert vote_info.title != ''
            option = vote_info.options[0]
            assert option.vote_num > 0
            assert option.text != ''
