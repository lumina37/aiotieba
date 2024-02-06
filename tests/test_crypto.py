import pytest

import aiotieba as tb
from aiotieba.helper.crypto import _sign, rc4_42


@pytest.mark.asyncio(scope="session")
async def test_clib(client: tb.Client):
    # await client._Client__init_z_id()
    # assert client.account.z_id != ''

    account = client.account
    account.android_id = "6723280942424242"
    account.uuid = "67232809-3407-3442-4207-672346917aaa"
    assert account.cuid_galaxy2 == '06C7F37D41256F25FABA97B885DB6EFB|VAPUDW7TA'
    assert account.c3_aid == 'A00-OGBA33NRAQASXI6FDZ4YAJFTK75EF4Y5-YVOG764X'

    data = [
        ('diana', 672328094),
        ('hello_cosmic', '你好42'),
    ]
    assert _sign(data) == 'd0337b3b3d597c5f87a1c0c37139d87b'

    query_key = rc4_42('d0337b3b3d597c5f87a1c0c37139d87b', b'6723280942424242')
    assert query_key == b'\x9f\xabU\x14\xa7\x0e\xb6k\xc4wV\xf2HN+.'
