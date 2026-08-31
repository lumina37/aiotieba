import pytest

import aiotieba as tb
from aiotieba.enums import GlobalSearchSortType


@pytest.mark.flaky(reruns=2, reruns_delay=5.0)
@pytest.mark.asyncio(loop_scope="session")
async def test_search_global(client: tb.Client):
    word = "贴吧"

    ##### 主题帖 #####
    searches = await client.search_global(word, rn=10)
    assert searches.err is None
    assert len(searches) > 0

    for post in searches:
        assert isinstance(post.tid, int)
        assert post.tid > 0
        assert isinstance(post.pid, int)
        assert post.pid > 0
        assert post.forum_name != ""

    ##### 翻页 #####
    page2 = await client.search_global(word, pn=2, rn=10, sort=GlobalSearchSortType.DESC)
    assert page2.err is None
    assert page2.current_page == 2
