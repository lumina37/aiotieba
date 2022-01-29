# -*- coding:utf-8 -*-
import tiebaBrowser as tb
import csv

score_stat = {}
fid2fname = {}
level_exp = {1: 1, 10: 2000,
             2: 5, 11: 3000,
             3: 15, 12: 6000,
             4: 30, 13: 10000,
             5: 50, 14: 18000,
             6: 100, 15: 30000,
             7: 200, 16: 60000,
             8: 500, 17: 100000,
             9: 1000, 18: 300000}
level2exp = {i: (level_exp[i]+level_exp[i+1])/2/100 for i in range(1, 18)}

brow = tb.Browser("default")
csv_read_file = open(f'asoul吧排行榜统计.csv', 'r', encoding='utf-8-sig', newline='')
csv_reader = csv.DictReader(csv_read_file)

for row in csv_reader:
    user_name = row['user_name']
    if not user_name or '*' in user_name:
        continue

    local_exp_100 = int(row['exp'])/100
    user = brow.get_userinfo_weak(tb.BasicUserInfo(user_name=user_name))

    tb.log.debug(f"Homepage user:{user_name} level:{row['level']}")
    user, threads = brow.get_homepage(user.portrait)
    for thread in threads:
        score_stat[thread.fid] = score_stat.get(
            thread.fid, 0)+local_exp_100*thread.reply_num/100

    tb.log.debug(f"ForumList user:{user_name} level:{row['level']}")
    for forum_info in brow.get_forumlist(user.user_id):
        fid = int(forum_info[1])
        fid2fname[fid] = forum_info[0]

csv_write_file = open(f'asoul吧关联性统计.csv', 'w',
                      encoding='utf-8-sig', newline='')
csv_writer = csv.writer(csv_write_file)
csv_writer.writerow(['fid', 'fname', 'score'])
csv_writer.writerows([[fid, fid2fname.get(fid, ''), score] for fid, score in score_stat.items()])
