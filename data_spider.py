# -*- coding:utf-8 -*-
import asyncio
import re
import time
from pathlib import Path

import StatDatabase_pb2
import tiebaBrowser as tb

debug = ''


async def stat_word(tieba_name):
    """
    stat_word 贴吧主题帖、回复、楼中楼词频统计
    """

    import csv

    import jieba

    async with tb.Browser("default") as brow:

        def _stopword_iter(dir):
            for txt_filepath in Path(dir).glob("*.txt"):
                with txt_filepath.open('r', encoding='utf-8') as txt_file:
                    for line in txt_file.readlines():
                        yield line.rstrip('\n')

        stopwords_set = set(_stopword_iter("stopwords"))

        def _check_word(word):
            return len(word) != 1 and word not in stopwords_set

        def _yield_words_from_posts(posts):
            for post in posts:
                for word in jieba.cut(post.text):
                    if _check_word(word):
                        yield word
                for comment in post.comments:
                    for word in jieba.cut(comment.text):
                        if _check_word(word):
                            yield word

        from collections import Counter
        word_counter = Counter()
        for thread_pn in range(333, 0, -1):
            tb.log.info(f"Thread pn: {thread_pn}")
            for thread in await brow.get_threads(tieba_name, thread_pn):

                if thread.reply_num > 300:
                    continue
                tb.log.debug(f"Thread tid: {thread.tid}")

                for post_pn in range(1, 9999):
                    posts = await brow.get_posts(thread.tid, post_pn, with_comments=True, comment_sort_by_agree=True, comment_rn=30)
                    word_counter.update(_yield_words_from_posts(posts))
                    if not posts.has_more:
                        break

        with open(f'{tieba_name}_word_freq_stat_{int(time.time())}.csv', 'w', encoding='utf-8-sig', newline='') as csv_write_file:
            csv_writer = csv.writer(csv_write_file)
            csv_writer.writerow(['word', 'freq'])
            csv_writer.writerows(word_counter.items())


async def stat_rank(tieba_name):
    """
    stat_rank 贴吧等级排行榜爬虫
    """

    start_time = time.perf_counter()
    tb.log.info(f"Spider start")

    async with tb.Browser("default") as brow:

        rank_db_proto = StatDatabase_pb2.RankUserDatabase()
        total_pn = 3700
        worker_num = 4
        task_per_worker = int(total_pn/worker_num)+1

        async def _worker(i):
            for pn in range(start := i*task_per_worker, start+task_per_worker):
                tb.log.debug(f"Worker:{i}. Handling pn:{pn}")
                res_list, has_more = await brow.get_rank_list(tieba_name, pn)
                for user_name, level, exp, is_vip in res_list:
                    user = rank_db_proto.users.add()
                    user.user_name = user_name
                    user.level = level
                    user.exp = exp
                    user.is_vip = is_vip
                if not has_more:
                    break
            tb.log.debug(f"Worker:{i} quit")

        workers = [_worker(i) for i in range(worker_num)]
        await asyncio.gather(*workers, return_exceptions=True)

    tb.log.info(
        f"Spider complete. Time cost:{time.perf_counter()-start_time}")

    start_time = time.perf_counter()
    tb.log.info(f"Serialize start")

    with open(f'{tieba_name}_rank_stat{debug}.bin', 'wb') as proto_file:
        proto_file.write(rank_db_proto.SerializeToString())

    tb.log.info(
        f"Serialize complete. Time cost:{time.perf_counter()-start_time}")


async def stat_risk_user(tieba_name):

    async with tb.CloudReview("default", tieba_name) as brow:

        start_time = time.perf_counter()
        tb.log.info(f"Spider start")

        risk_db_proto = StatDatabase_pb2.RiskUserDatabase()
        fid2fname = {}

        task_queue = asyncio.Queue(maxsize=4)
        running_flag = True

        async def _producer():
            with open(f'{tieba_name}_rank_stat{debug}.bin', 'rb') as proto_file:
                rank_db_proto = StatDatabase_pb2.RankUserDatabase()
                rank_db_proto.ParseFromString(proto_file.read())
                for idx, user_proto in enumerate(rank_db_proto.users, 1):
                    await task_queue.put((idx, user_proto))
            nonlocal running_flag
            running_flag = False

        async def _worker(i):

            await asyncio.sleep(i/2)

            while 1:
                try:
                    idx, rank_user_proto = await asyncio.wait_for(task_queue.get(), timeout=1)
                except asyncio.TimeoutError:
                    nonlocal running_flag
                    if running_flag == False:
                        tb.log.debug(f"Worker:{i} quit")
                        return

                user_name = rank_user_proto.user_name
                if not user_name or re.search('[*.#]', user_name):
                    continue
                user = await brow.get_user_info(user_name)
                if user.user_id <= 0:
                    continue

                user_proto = risk_db_proto.users.add()

                # 收集用户信息和头像哈希
                user_proto.user_id = user.user_id
                user_proto.portrait = user.portrait
                image = await brow.url2image(f"http://tb.himg.baidu.com/sys/portraitn/item/{user.portrait}")
                user_proto.portrait_hash = brow.get_imghash(image)

                # 收集用户首页发帖
                tb.log.info(
                    f"{idx}. User:{user_name} / level:{rank_user_proto.level} / target:homepage")
                user, threads = await brow.get_homepage(user.portrait)
                for thread in threads:
                    thread_proto = user_proto.threads.add()

                    thread_proto.fid = thread.fid
                    thread_proto.tid = thread.tid
                    thread_proto.agree = thread.agree
                    thread_proto.view_num = thread.view_num
                    thread_proto.reply_num = thread.reply_num
                    thread_proto.text = thread.text

                # 收集用户关注吧
                if 3 != user.priv_like:
                    tb.log.info(
                        f"{idx}. User:{user_name} / level:{rank_user_proto.level} / target:forumlist")
                    async for fname, fid, level, exp in brow.get_forums(user.user_id):
                        fid2fname[fid] = fname
                        forum_proto = user_proto.forums.add()
                        forum_proto.fid = fid
                        forum_proto.level = level
                        forum_proto.exp = exp

        workers = [_worker(i) for i in range(4)]
        await asyncio.gather(*workers, _producer(), return_exceptions=True)

    tb.log.info(
        f"Spider complete. Time cost:{time.perf_counter()-start_time}")

    start_time = time.perf_counter()
    tb.log.info(f"Serialize start")

    with open(f'{tieba_name}_risk_user_stat{debug}.bin', 'wb') as proto_file:
        proto_file.write(risk_db_proto.SerializeToString())

    forum_list_proto = StatDatabase_pb2.ForumList()
    for fid, fname in fid2fname.items():
        forum_map_proto = forum_list_proto.forums.add()
        forum_map_proto.fid = fid
        forum_map_proto.fname = fname
    with open(f'{tieba_name}_forum_map_list{debug}.bin', 'wb') as proto_file:
        proto_file.write(forum_list_proto.SerializeToString())

    tb.log.info(
        f"Serialize complete. Time cost:{time.perf_counter()-start_time}")


async def main():
    await stat_word('v')
    # await stat_risk_user('asoul')


if __name__ == "__main__":

    asyncio.run(main())
