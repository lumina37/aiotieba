# -*- coding:utf-8 -*-
import re
import csv
import time

import tiebaBrowser as tb

brow = tb.Browser("default")
tb_name = 'asoul'
tid = 7744822759

csv_file = open(f'{tb_name}吧吧务竞选统计{time.time()}.csv',
                'w', encoding='utf-8-sig', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['floor', 'user_name', 'vote_num'])

for post in brow.get_posts(tid):
    if not post.is_thread_owner or post.reply_num == 0 or post.floor == 1:
        continue
    vote_stat = set()
    user_name = re.search('@(.*)',post.text).group(1)
    for pn in range(1, 0xffff):
        comments = brow.get_comments(tid, post.pid, pn)
        for comment in comments:
            if '支持' in comment.text:
                vote_stat.add(comment.user.user_id)
        if not comments.has_next:
            break

    res = [post.floor, user_name, len(vote_stat)]
    print(res)
    csv_writer.writerow(res)
