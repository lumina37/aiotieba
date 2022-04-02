# -*- coding:utf-8 -*-
import asyncio
import time
from pathlib import Path

import tiebaBrowser as tb

debug = ''


async def stat_word(tieba_name):
    """
    stat_word 贴吧主题帖、回复、楼中楼词频统计
    """

    import csv

    import jieba

    async with tb.Browser("starry") as brow:

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


async def main():
    await stat_word('asoul')


if __name__ == "__main__":

    asyncio.run(main())
