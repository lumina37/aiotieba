import os

import pytest_asyncio

import aiotieba as tb


@pytest_asyncio.fixture(loop_scope="session")
async def client():
    async with tb.Client(os.getenv("TB_BDUSS"), os.getenv("TB_STOKEN", ""), try_ws=True, proxy=True) as client:
        yield client
