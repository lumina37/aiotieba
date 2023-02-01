import pytest

import aiotieba as tb


@pytest.mark.asyncio
async def test_clib(client: tb.Client):
    await client._Client__init_zid()
    assert client.core.z_id != ''

    core = client.core
    core._android_id = "6723280942424242"
    core._uuid = "67232809-3407-3442-4207-672346917aaa"
    assert core.cuid_galaxy2 == '06C7F37D41256F25FABA97B885DB6EFB|VAPUDW7TA'
    assert core.c3_aid == 'A00-OGBA33NRAQASXI6FDZ4YAJFTK75EF4Y5-YVOG764X'
