import pytest

import aiotieba as tb
from aiotieba.helper.crypto import APP_SALT, compute_sign, enuid, rc4_42

ENUID_CASES = [
    (
        "A3ED2D7B9CFC28E8934A3FBD3A9579C7|VZ5FKB5XS",
        "luHTu_ii2ajm8SuE_OHNtjaxvu_j8HuZgiBgigOQSi8-9L8TltSx8VHwA",
    ),
    (
        "06C7F37D41256F25FABA97B885DB6EFB|VAPUDW7TA",
        "_uSb8luR2ag0av8T_8vF8l8WSaj4aHfSjaH9ag8iHa8BkHMgJi3yiH_aA",
    ),
    (
        "00000000000000000000000000000000|V00000000",
        "_a2q8_aq28_qa28q_a2q8_aq28_qa28q_a2q8_aq288j928g_a2q8ALqA",
    ),
    (
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF|VZZZZZZZZ",
        "08H-a08-Ha0-8Ha-08H-a08-Ha0-8Ha-08H-a08-Ha8-9DhxyIDmh27mA",
    ),
]


@pytest.mark.parametrize(("cuid_galaxy2", "expected"), ENUID_CASES)
def test_enuid(cuid_galaxy2: str, expected: str):
    result = enuid(cuid_galaxy2)

    assert result == expected
    assert len(result) == 57
    assert result.isascii()
    assert result[-1] == "A"


@pytest.mark.asyncio
async def test_clib(client: tb.Client):
    # await client._Client__init_zid()
    # assert client.account.zid != ''

    account = client.account
    account.android_id = "6723280942424242"
    account.uuid = "67232809-3407-3442-4207-672346917aaa"
    assert account.cuid_galaxy2 == "06C7F37D41256F25FABA97B885DB6EFB|VAPUDW7TA"
    assert account.c3_aid == "A00-OGBA33NRAQASXI6FDZ4YAJFTK75EF4Y5-YVOG764X"

    data = [
        ("reverse", 1999),
        ("hello_cosmic", "你好42"),
    ]
    assert compute_sign(data, salt=APP_SALT) == "0be9991d2f8371952ab0b9cb14363bc2"

    query_key = rc4_42("d0337b3b3d597c5f87a1c0c37139d87b", b"6723280942424242")
    assert query_key == b"\x9f\xabU\x14\xa7\x0e\xb6k\xc4wV\xf2HN+."
