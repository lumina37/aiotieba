import asyncio

import pytest
import pytest_asyncio

import aiotieba as tb


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="package")
async def client():
    async with tb.Client('starry_xh', try_ws=True) as client:
        yield client
