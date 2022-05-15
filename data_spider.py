# -*- coding:utf-8 -*-
import asyncio
import time
from collections import Counter

import tiebaBrowser as tb


async def stat_active_user(tieba_name):
    import csv

    start_time = time.perf_counter()
    tb.log.info("Spider start")

    user_counter = Counter()

    async with tb.Browser("starry") as brow:

        ts_thre = int(time.time()) - 3 * 24 * 3600
        task_queue = asyncio.Queue(maxsize=4)
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

                for thread in await brow.get_threads(tieba_name, pn):
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

        workers = [_worker(i) for i in range(6)]
        await asyncio.gather(*workers, _producer(), return_exceptions=True)

    tb.log.info(f"Spider complete. Time cost:{time.perf_counter()-start_time}")

    def _user_iter():
        for user, post_num in user_counter.most_common():
            yield user.user_id, user.log_name, post_num

    with open(f'{tieba_name}_post_user_stat_{ts_thre}.csv', 'w', encoding='utf-8-sig', newline='') as csv_write_file:
        csv_writer = csv.writer(csv_write_file)
        csv_writer.writerow(['user_id', 'log_name', 'post_num'])
        csv_writer.writerows(_user_iter())


async def main():
    await stat_active_user('asoul')


if __name__ == "__main__":

    asyncio.run(main())
