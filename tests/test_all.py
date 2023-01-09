import asyncio

import httpx
import pytest
import pytest_asyncio

import aiotieba as tb


@pytest.fixture(scope="session")
def event_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()


@pytest_asyncio.fixture(scope="module")
async def client():
    async with tb.Client('starry_xh') as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def db():
    async with tb.MySQLDB('starry') as db:
        yield db


def check_UserInfo(user: tb.UserInfo):
    assert isinstance(user.user_id, int)
    assert user.user_id != 0
    assert isinstance(user.portrait, str)
    assert user.portrait != ""
    assert isinstance(user.user_name, str)


@pytest.mark.asyncio
async def test_BasicUserInfo(client: tb.Client):
    user = await client.get_self_info()
    check_UserInfo(user)

    user_id = user.user_id

    user = await client.get_user_info(user.portrait, tb.ReqUInfo.BASIC)
    assert user_id == user.user_id
    check_UserInfo(user)

    user = await client.get_user_info(user.user_id, tb.ReqUInfo.BASIC)
    assert user_id == user.user_id
    check_UserInfo(user)

    user = await client.get_user_info(user.portrait)
    assert user_id == user.user_id
    check_UserInfo(user)

    user = await client.get_user_info(user.user_id)
    assert user_id == user.user_id
    check_UserInfo(user)


@pytest.mark.asyncio
async def test_Posts_and_Fragments(client: tb.Client):
    posts = await client.get_posts(8211419000, with_comments=True)

    # Test Post
    post = posts[1]
    assert isinstance(post.text, str)
    assert post.text != ""

    assert post.fid > 0
    assert post.fname != ""
    assert post.tid > 0
    assert post.pid > 0
    check_UserInfo(post.user)
    assert post.author_id == post.user.user_id

    assert post.floor > 0
    assert post.reply_num > 0
    assert post.create_time > 0
    assert post.is_thread_author == (post.author_id == posts.thread.author_id)

    # Test FragText
    for frag in post.contents.texts:
        assert frag.text != ""

    # Test FragAt
    frag = post.contents.ats[0]
    assert frag.text != ""
    assert frag.user_id > 0

    # Test FragVoice
    assert post.contents.has_voice is True

    # Test FragImage
    frag = post.contents.imgs[0]
    assert frag.src != ""
    assert frag.big_src != ""
    assert frag.origin_src != ""
    assert len(frag.hash) == 40
    assert frag.show_width > 0
    assert frag.show_height > 0

    # Test FragEmoji
    frag = post.contents.emojis[0]
    assert frag.desc != ""

    # Test FragTiebaplus
    frag = post.contents.tiebapluses[0]
    assert frag.text != ""
    assert frag.url != ""
    frag = post.contents.tiebapluses[1]
    assert frag.text != ""
    assert frag.url != ""

    # Test FragLink
    post = posts[2]
    frag = post.contents.links[0]
    assert frag.title != ""
    assert frag.url.host != ""
    assert frag.title != ""
    frag = post.contents.links[1]
    assert frag.is_external is True


def check_ShareThread(thread: tb.ShareThread):
    # Test FragText
    frag = thread.contents.texts[0]
    assert isinstance(frag.text, str)
    assert frag.text != ""

    # Test FragAt
    for frag in thread.contents.ats:
        assert isinstance(frag.text, str)
        assert frag.text != ""
        assert isinstance(frag.user_id, int)
        assert frag.user_id != 0

    # Test FragLink
    frag = thread.contents.links[0]
    assert isinstance(frag.title, str)
    assert frag.title != ""
    assert isinstance(frag.url, httpx.URL)
    assert isinstance(frag.title, str)
    assert frag.title != ""
    assert isinstance(frag.is_external, bool)

    # Test FragVoice
    assert thread.contents.has_voice is True

    # Test FragImage
    frag = thread.contents.imgs[0]
    assert isinstance(frag.src, str)
    assert frag.src != ""
    assert isinstance(frag.origin_src, str)
    assert frag.origin_src != ""
    assert isinstance(frag.hash, str)
    assert len(frag.hash) == 40

    # Test VoteInfo
    vote_info = thread.vote_info
    assert isinstance(vote_info.title, str)
    assert vote_info.title != ""
    assert isinstance(vote_info.total_vote, int)
    assert isinstance(vote_info.total_user, int)
    for option in vote_info.options:
        assert isinstance(option.vote_num, int)
        assert isinstance(option.text, str)
        assert option.text != ""


@pytest.mark.asyncio
async def test_Thread(client: tb.Client):
    fname = "starry"
    threads, fid = await asyncio.gather(client.get_threads(fname), client.get_fid(fname))

    assert len(threads) > 0
    assert isinstance(fid, int)
    assert fid > 0

    for thread in threads:

        # Test Normal Thread
        if thread.tid == 7817885777:
            assert isinstance(thread.text, str)
            assert thread.text != ""
            assert isinstance(thread.title, str)
            assert thread.title != ""

            assert thread.fid == fid
            assert thread.fname == fname
            assert isinstance(thread.pid, int)
            assert thread.pid > 0
            check_UserInfo(thread.user)
            assert thread.author_id == thread.user.user_id

            assert isinstance(thread.view_num, int)
            assert thread.view_num > 0
            assert isinstance(thread.reply_num, int)
            assert thread.reply_num > 0
            assert isinstance(thread.create_time, int)
            assert thread.create_time > 0
            assert isinstance(thread.last_time, int)
            assert thread.last_time > 0

        # Test Vote Thread
        elif thread.tid == 7763555471:
            assert isinstance(thread.vote_info.title, str)
            assert isinstance(thread.vote_info.total_vote, int)
            assert isinstance(thread.vote_info.total_user, int)
            for option in thread.vote_info.options:
                assert isinstance(option.vote_num, int)
                assert isinstance(option.text, str)

        # Test Share Thread
        elif thread.tid == 7905926315:
            check_ShareThread(thread.share_origin)


@pytest.mark.asyncio
async def test_Comment(client: tb.Client):
    comments = await client.get_comments(7763274602, 143550881510)
    comment = comments[0]

    assert isinstance(comment.text, str)
    assert comment.text != ""

    assert isinstance(comment.fid, int)
    assert comment.fid > 0
    assert isinstance(comment.fname, str)
    assert comment.fname != ""
    assert isinstance(comment.tid, int)
    assert comment.tid > 0
    assert isinstance(comment.pid, int)
    assert comment.pid > 0
    check_UserInfo(comment.user)
    assert comment.author_id == comment.user.user_id

    assert comment.create_time > 0


@pytest.mark.asyncio
async def test_Ats(client: tb.Client):
    ats = await client.get_ats()
    at = ats[0]
    assert isinstance(at.text, str)
    assert at.text != ""
    assert isinstance(at.fname, str)
    assert at.fname != ""
    assert isinstance(at.tid, int)
    assert at.tid > 0
    assert isinstance(at.pid, int)
    assert at.pid > 0
    assert isinstance(at.author_id, int)
    assert at.author_id != 0
    assert at.author_id == at.user.user_id
    assert isinstance(at.create_time, int)
    assert at.create_time > 0


@pytest.mark.asyncio
async def test_Database(db: tb.MySQLDB):
    fname = db.fname
    fid = await db.get_fid(fname)
    assert fname == await db.get_fname(fid)
    await asyncio.gather(
        *[
            db.get_userinfo("v_guard"),
            db.get_tid(7763274602),
            db.get_user_id_list(),
            db.get_tid_list(limit=3),
        ]
    )
