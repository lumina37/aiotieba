import pytest

import aiotieba as tb


@pytest.mark.flaky(reruns=0, reruns_delay=2.0)
@pytest.mark.asyncio(scope="session")
async def test_Image(client: tb.Client):
    image = await client.get_portrait("tb.1.8277e641.gUE2cTq4A4z5fi2EHn5k3Q")

    ##### Image #####
    image.img.size > 0
