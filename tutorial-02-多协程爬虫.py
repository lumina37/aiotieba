"""
本例中，你将学会如何使用asyncio.Queue实现一个生产者消费者模式下的多协程爬虫
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

    # 使用键名"default"对应的BDUSS创建客户端
    async with tb.Client("default") as brow:

        # 任务队列
        task_queue = asyncio.Queue(maxsize=8)
        is_running = True

        async def producer():
            """
            生产者协程
            """

            for pn in range(32, 0, -1):
                # 生产者不断地将页码pn填入任务队列task_queue
                await task_queue.put(pn)
            nonlocal is_running
            is_running = False

        async def worker(i: int):
            """
            消费者协程

            Args:
                i (int): 协程编号
            """

            while 1:
                try:
                    # 消费者不断地从task_queue中拉取由生产者协程提供的页码pn作为任务
                    # 如果超过1秒未获取到新的页码pn，asyncio.wait_for将抛出asyncio.TimeoutError
                    pn = await asyncio.wait_for(task_queue.get(), timeout=1)
                    tb.log.debug(f"Worker#{i} handling pn:{pn}")
                except asyncio.TimeoutError:
                    # 捕获asyncio.TimeoutError以退出协程
                    nonlocal is_running
                    if is_running is False:
                        tb.log.debug(f"Worker#{i} quit")
                        return
                else:
                    # 执行被分派的任务，即爬取pn页的帖子列表
                    threads = await brow.get_threads(fname, pn)
                    nonlocal thread_list
                    thread_list += threads

        # 创建8个协程
        workers = [worker(i) for i in range(8)]
        # 使用asyncio.gather并发执行
        await asyncio.gather(*workers, producer())

    tb.log.info(f"Spider complete. Time cost:{time.perf_counter()-start_time}")

    # 按主题帖浏览量降序排序
    thread_list.sort(key=lambda thread: thread.view_num, reverse=True)
    # 将浏览量最高的10个主题帖的信息打印到日志
    for i, thread in enumerate(thread_list[0:10], 1):
        tb.log.info(f"Rank#{i} view_num:{thread.view_num} title:{thread.title}")


# 执行协程crawler
asyncio.run(crawler("图拉丁"))
