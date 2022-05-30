"""
本例中，你将学会如何使用多个协程并发执行爬虫任务
请认真阅读注释
"""

import asyncio
import time
from typing import List

import aiotieba as tb


async def crawler(fname: str):
    """
    获取贴吧名为fname的贴吧的前32页中浏览量最高的10个主题帖

    Args:
        fname (str): 贴吧名
    """

    start_time = time.perf_counter()
    tb.log.info("Spider start")

    thread_list: List[tb.Thread] = []

    async with tb.Client("default") as brow:

        task_queue = asyncio.Queue(maxsize=8)
        is_running = True

        async def _producer():
            for pn in range(32, 0, -1):
                # 通过task_queue向worker分派页码作为任务
                await task_queue.put(pn)
            nonlocal is_running
            is_running = False

        async def _worker(i):
            while 1:
                try:
                    # 获取在task_queue中由producer协程分派的页码
                    # 如果超过1秒未获取到任务，则触发TimeoutError退出协程
                    pn = await asyncio.wait_for(task_queue.get(), timeout=1)
                    tb.log.debug(f"Worker#{i} handling pn:{pn}")
                except asyncio.TimeoutError:
                    nonlocal is_running
                    if is_running is False:
                        tb.log.debug(f"Worker#{i} quit")
                        return
                else:
                    # 爬取pn页的帖子列表
                    threads = await brow.get_threads(fname, pn)
                    nonlocal thread_list
                    thread_list += threads

        # 创建8个协程
        workers = [_worker(i) for i in range(8)]
        # 并发执行
        await asyncio.gather(*workers, _producer())

    tb.log.info(f"Spider complete. Time cost:{time.perf_counter()-start_time}")

    thread_list.sort(key=lambda thread: thread.view_num, reverse=True)
    for i, thread in enumerate(thread_list[0:10], 1):
        tb.log.info(f"Rank#{i} view_num:{thread.view_num} title:{thread.title}")


asyncio.run(crawler("图拉丁"))
