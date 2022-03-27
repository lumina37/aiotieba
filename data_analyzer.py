# -*- coding:utf-8 -*-
import csv
import re
from collections import Counter
from pathlib import Path

import numpy as np

import StatDatabase_pb2
from tiebaBrowser.cloud_review import RegularExp

debug = ''

tieba_name = 'asoul'

warn_words = ['潮鞋', '莆田', '会员', '创业', '项目', '致富', '手工活', '微商', '货源', '代理', '批发',
              '客源', '副业', '地推', '赚钱', '宝妈', '配音', '播音', '录音', '义工', '有声', '兼职', '羊毛', '搞钱', '贷']
warn_exp = re.compile('|'.join(warn_words))

white_kw_list = ['管人|(哪个|什么)v|bv|联动|歌回|杂谈|歌力|企划|切片|前世|毕业|sc|弹幕|同接|二次元|原批|牧场|周边|史书|饭圈|滑坡',
                 '(a|b|睿|皇协|批|p)站|b博|海鲜|(v|a)(吧|8)|nga|404|ytb|论坛|字幕组|粉丝群|魂组|录播',
                 'asoul|皮套|纸片人|套皮|嘉然|然然|向晚|晚晚|乃琳|奶琳|贝拉|拉姐|珈乐|羊驼|a(骚|s|手)|向晚|歌姬|乃贝|晚饭',
                 '共振|取关|牧场|啊啊啊|麻麻|别急|可爱|sad|感叹|速速|我超|存牌|狠狠|切割|牛牛|一把子|幽默|GNK48|汴京|抱团|别融',
                 '嘉心糖|顶碗人|贝极星|奶淇淋|n70|皇(珈|家)|黄嘉琪|泥哥|(a|b|豆|d|抖|快|8|吧)(u|友)|一个魂|粉丝|ylg|mmr|低能|易拉罐|脑弹|铝制品|纯良']
white_kw_exp = re.compile('|'.join(white_kw_list), re.I)

with open(f'{tieba_name}_forum_map_list{debug}.bin', 'rb') as proto_file:
    forum_list = StatDatabase_pb2.ForumList()
    forum_list.ParseFromString(proto_file.read())
    fid2fname = {forum.fid: forum.fname for forum in forum_list.forums}
    fname2fid = {forum.fname: forum.fid for forum in forum_list.forums}
    warn_fids = {
        forum.fid for forum in forum_list.forums if warn_exp.search(forum.fname)}
    white_tiebas = ['asoul', 'asoul一个魂', '原神', 'bilibili',
                    '嘉然', '向晚', '贝拉', '珈乐', '乃琳', 'v', 'steam', '战斗吧歌姬']
    white_fids = [fname2fid[fname] for fname in white_tiebas]

with open(f'{tieba_name}_risk_user_stat{debug}.bin', 'rb') as proto_file:
    risk_user_proto = StatDatabase_pb2.RiskUserDatabase()
    risk_user_proto.ParseFromString(proto_file.read())


def anal_risk_forum():
    forum_counter = Counter()

    for user in risk_user_proto.users:
        for forum in user.forums:
            if forum.fid in warn_fids:
                for forum in user.forums:
                    if forum.fid not in white_fids:
                        forum_counter[fid2fname.get(forum.fid, '')] += 1

    most_common = forum_counter.most_common(2000)
    with open(f'{tieba_name}_risk_forum{debug}.csv', 'w', encoding='utf-8-sig', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(most_common)

    import jieba

    def _stopword_iter(dir):
        for txt_filepath in Path(dir).glob("*.txt"):
            with txt_filepath.open('r', encoding='utf-8-sig') as txt_file:
                for line in txt_file.readlines():
                    yield line.rstrip('\n')
    stopwords_set = set(_stopword_iter("stopwords"))

    word_counter = Counter()
    for fname, count in most_common:
        for word in jieba.cut(fname):
            if word not in stopwords_set:
                word_counter[word] += count

    with open(f'{tieba_name}_risk_forum_kw{debug}.csv', 'w', encoding='utf-8-sig', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(word_counter.most_common())


def anal_user():

    def _iter_user():
        for user in risk_user_proto.users:
            if forum_len := len(user.forums):
                warn_count = 0
                for forum in user.forums:
                    if forum.fid in warn_fids:
                        warn_count += 1
                f_risk_ratio = warn_count/forum_len
            else:
                f_risk_ratio = np.NaN

            if forum_len > 12:
                exps = [forum.exp for forum in user.forums]
                exp_array = np.asarray(exps[:8], dtype=np.int32)
                f_exp_coefvar = np.std(exp_array)/np.mean(exp_array)
            else:
                f_exp_coefvar = np.NaN

            thread_len = len(user.threads)
            if thread_len:
                t_forum_white_count = 0
                for thread in user.threads:
                    if thread.fid in white_fids:
                        t_forum_white_count += 1
                t_forum_white_ratio = t_forum_white_count/thread_len
            else:
                t_forum_white_ratio = np.NaN

            if thread_len >= 5:
                t_risk_count = 0
                t_white_count = 0
                for thread in user.threads:
                    if white_kw_exp.search(thread.text):
                        t_white_count += 1
                    else:
                        if RegularExp.app_nocheck_exp.search(thread.text) or (RegularExp.app_exp.search(thread.text) or RegularExp.app_check_exp.search(thread.text)):
                            t_risk_count += 1
                        elif RegularExp.game_nocheck_exp.search(thread.text) or (RegularExp.game_exp.search(thread.text) or RegularExp.game_check_exp.search(thread.text)):
                            t_risk_count += 1
                        elif RegularExp.job_nocheck_exp.search(thread.text) or (RegularExp.job_exp.search(thread.text) or RegularExp.job_check_exp.search(thread.text)):
                            t_risk_count += 1
                t_risk_ratio = t_risk_count/thread_len
                t_white_ratio = t_white_count/thread_len
            else:
                t_risk_ratio = np.NaN
                t_white_ratio = np.NaN

            yield user.user_id, user.portrait, user.portrait_hash, t_risk_ratio, t_white_ratio, t_forum_white_ratio, f_risk_ratio, f_exp_coefvar

    with open(f'{tieba_name}_risk_user{debug}.csv', 'w', encoding='utf-8-sig', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['user_id', 'portrait', '头像哈希', '帖子内容异常比例',
                            '帖子内容白名单比例', '帖子所在吧白名单比例', '关注吧异常比例', '关注吧前8位的经验值变异系数'])
        csv_writer.writerows(_iter_user())


if __name__ == "__main__":

    anal_user()
