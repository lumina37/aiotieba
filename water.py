# -*- coding:utf-8 -*-
import asyncio
import time

import tiebaBrowser as tb


async def main():
    async with tb.Browser("default") as brow:
        for tb_name, tid in [('元气骑士', 5074946575), ('lol半价', 2986143112), ('asoul', 7230587602)]:
            for i in range(6):
                await brow.add_post(tb_name, tid, str(i))
                time.sleep(300)
        await brow.add_post('soulknight', 6128818144, '0')
        await brow.add_post('starry', 6154402005, '0')

asyncio.run(main())
