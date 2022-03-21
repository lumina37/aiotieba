# -*- coding:utf-8 -*-
import asyncio

import tiebaBrowser as tb


async def main():

    for key in ['default', 'backup', 'listener']:
        async with tb.Browser(key) as brow:
            for tb_name in ['asoul', 'v', 'vtuber自由讨论']:
                await brow.sign_forum(tb_name)

asyncio.run(main())
