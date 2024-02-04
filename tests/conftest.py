import os

import pytest_asyncio

import aiotieba as tb


@pytest_asyncio.fixture(scope="session")
async def client():
    account = tb.core.Account(os.getenv('TB_BDUSS'), os.getenv('TB_STOKEN', ''))
    async with tb.Client(account, try_ws=True) as client:
        yield client
