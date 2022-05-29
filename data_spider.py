# -*- coding:utf-8 -*-
import asyncio
import csv
import time
from collections import Counter

import aiotieba as tb


async def statistic(fname: str):
    """
    统计发帖信息
    """

    start_time = time.perf_counter()
    tb.log.info("Spider start")

    user_counter = Counter()

    async with tb.Client("starry") as brow:

        ts_thre = int(time.time()) - 3 * 24 * 3600
        task_queue = asyncio.Queue(maxsize=8)
        running_flag = True

        async def _producer():
            for pn in range(333, 0, -1):
                await task_queue.put(pn)
            nonlocal running_flag
            running_flag = False

        async def _worker(i):
            def append_posts(posts: tb.Posts):
                for post in posts:
                    if post.create_time < ts_thre:
                        raise StopIteration
                    user_counter[post.user] += 1

            while 1:
                try:
                    pn = await asyncio.wait_for(task_queue.get(), timeout=1)
                except asyncio.TimeoutError:
                    nonlocal running_flag
                    if running_flag is False:
                        tb.log.debug(f"Worker:{i} quit")
                        return

                for thread in await brow.get_threads(fname, pn):
                    if thread.last_time < ts_thre:
                        continue
                    tb.log.debug(f"Worker:{i} handling pn:{pn} tid:{thread.tid}")
                    try:
                        posts = await brow.get_posts(thread.tid, 99999, sort=1)
                        append_posts(posts)
                        start_pn = posts.page.total_page - 1
                        if start_pn == 0:
                            continue
                        for post_pn in range(start_pn, 0, -1):
                            posts = await brow.get_posts(thread.tid, post_pn, sort=1)
                            append_posts(posts)
                    except StopIteration:
                        pass

        workers = [_worker(i) for i in range(8)]
        await asyncio.gather(*workers, _producer())

    tb.log.info(f"Spider complete. Time cost:{time.perf_counter()-start_time}")

    def _row_iter():
        for user, post_num in user_counter.most_common():
            yield user.user_id, post_num, user.ip

    file_name = f'{fname}_post_stat.csv'
    with open(file_name, 'w', encoding='utf-8-sig', newline='') as csv_write_file:
        csv_writer = csv.writer(csv_write_file)
        csv_writer.writerows(_row_iter())


def analyze(fname: str):
    """
    数据分析
    """

    rfile_name = f'{fname}_post_stat.csv'
    with open(rfile_name, 'r', encoding='utf-8-sig', newline='') as csv_read_file:
        csv_reader = csv.reader(csv_read_file)

        user_counter = Counter()  # 统计ip属地的8u人数
        post_counter = Counter()  # 统计ip属地的发帖量
        for _, post_num, ip in csv_reader:
            post_num = int(post_num)
            user_counter[ip] += 1
            post_counter[ip] += post_num

    def _row_iter():
        for ip, user_num in user_counter.most_common():
            yield ip, user_num, post_counter[ip]

    wfile_name = f'{fname}_post_analyze.csv'
    with open(wfile_name, 'w', encoding='utf-8-sig', newline='') as csv_write_file:
        csv_writer = csv.writer(csv_write_file)
        csv_writer.writerow(['ip归属地', '8u人数', '发帖量'])
        csv_writer.writerows(_row_iter())


async def main():
    fname = '孙笑川'
    # await statistic(fname)
    analyze(fname)


if __name__ == "__main__":

    asyncio.run(main())
