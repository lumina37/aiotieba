# -*- coding:utf-8 -*-
import asyncio
import csv
import re
import time
from pathlib import Path

import StatDatabase_pb2
import tiebaBrowser as tb
import tiebaBrowser.cloud_review as cr

tieba_name = 'asoul'
debug = ''


async def main():

    async with cr.CloudReview("default", tieba_name) as brow:

        async def stat_word():
            import jieba

            def _stopword_iter(dir):
                for txt_filepath in Path(dir).glob("*.txt"):
                    with txt_filepath.open('r', encoding='utf-8') as txt_file:
                        for line in txt_file.readlines():
                            yield line.rstrip('\n')

            stopwords_set = set(_stopword_iter("stopwords"))

            def _check_word(word):
                return len(word) != 1 and word not in stopwords_set

            async def _word_iter(tieba_name):
                for thread_pn in range(333, 0):
                    tb.log.info(f"Thread pn: {thread_pn}")
                    for thread in await brow.get_threads(tieba_name, thread_pn):

                        if thread.reply_num > 300:
                            continue
                        tb.log.debug(f"Thread tid: {thread.tid}")

                        for post_pn in range(1, 9999):
                            posts = await brow.get_posts(thread.tid, post_pn, with_comments=True, comment_sort_by_agree=True, comment_rn=30)
                            for post in posts:
                                for word in jieba.cut(post.text):
                                    if _check_word(word):
                                        yield word
                                for comment in post.comments:
                                    for word in jieba.cut(comment.text):
                                        if _check_word(word):
                                            yield word

                            if not posts.has_next:
                                break

            from collections import Counter
            word_counter = Counter(_word_iter(tieba_name))

            with open(f'{tieba_name}_word_freq_stat_{int(time.time())}.csv', 'w', encoding='utf-8-sig', newline='') as csv_write_file:
                csv_writer = csv.writer(csv_write_file)
                csv_writer.writerow(['word', 'freq'])
                csv_writer.writerows(word_counter.items())

        async def collect_risk_user():

            csv_read_file = open(f'{tieba_name}_rank_stat{debug}.csv',
                                 'r', encoding='utf-8-sig', newline='')
            csv_reader = csv.DictReader(csv_read_file)

            start_time = time.time()
            tb.log.info("user_stat start")

            fid2fname = {}
            database_proto = StatDatabase_pb2.StatDatabase()
            for idx, row in enumerate(csv_reader, 1):
                user_name = row['user_name']
                if not user_name or re.search('[*.#]', user_name):
                    continue
                user = await brow.get_userinfo(user_name)
                if user.user_id <= 0:
                    continue
                user_proto = database_proto.user.add()

                # 收集用户user_id和头像哈希
                user_proto.user_id = user.user_id
                image = await brow.url2image(f"http://tb.himg.baidu.com/sys/portrait/item/{user.portrait}")
                user_proto.portrait_hash = brow.get_imghash(image)

                # 收集用户首页发帖
                tb.log.info(
                    f"{idx}. User:{user_name} / level:{row['level']} / target:homepage")
                user, threads = await brow.get_homepage(user.portrait)
                for thread in threads:
                    thread_proto = user_proto.thread.add()
                    thread_proto.fid = thread.fid
                    thread_proto.tid = thread.tid

                # 收集用户关注吧
                if 3 != user.priv_like:
                    tb.log.info(
                        f"{idx}. User:{user_name} / level:{row['level']} / target:forumlist")
                    async for forum_info in brow.get_forum_list(user.user_id):
                        fid2fname[forum_info[1]] = forum_info[0]
                        forum_proto = user_proto.forum.add()
                        forum_proto.fid = forum_info[1]
                        forum_proto.level = forum_info[2]
                        forum_proto.exp = forum_info[3]

            csv_read_file.close()
            tb.log.info(f"user_stat time cost:{time.time()-start_time}")

            with open(f'{tieba_name}_risk_user_stat{debug}.bin', 'wb') as proto_file:
                proto_file.write(database_proto.SerializeToString())

            forum_map_list_proto = StatDatabase_pb2.ForumMapList()
            for fid, fname in fid2fname.items():
                forum_map_proto = forum_map_list_proto.forum_map.add()
                forum_map_proto.fid = fid
                forum_map_proto.fname = fname
            with open(f'{tieba_name}_forum_map_list{debug}.bin', 'wb') as proto_file:
                proto_file.write(forum_map_list_proto.SerializeToString())
            tb.log.info("all complete")

        await stat_word()


if __name__ == "__main__":

    asyncio.run(main())
