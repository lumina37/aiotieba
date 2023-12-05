import pytest_asyncio

import aiotieba as tb


@pytest_asyncio.fixture(scope="session")
async def client():
    async with tb.Client('starry_xh', try_ws=True) as client:
        yield client
