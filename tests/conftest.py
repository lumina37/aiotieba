import os

import pytest
import pytest_asyncio

import aiotieba as tb


@pytest_asyncio.fixture(loop_scope="session")
async def client():
    bduss = os.getenv("TB_BDUSS")
    if not bduss:
        pytest.skip("TB_BDUSS未设置")

    stoken = os.getenv("TB_STOKEN", "")

    async with tb.Client(bduss, stoken, try_ws=True, proxy=True) as client:
        yield client
