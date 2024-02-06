import os

import pytest_asyncio

import aiotieba as tb


@pytest_asyncio.fixture(scope="session")
async def client():
    async with tb.Client(os.getenv('TB_BDUSS'), os.getenv('TB_STOKEN', ''), try_ws=True) as client:
        yield client
