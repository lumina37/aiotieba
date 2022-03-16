# -*- coding:utf-8 -*-
import csv
import time
import tiebaBrowser as tb

_file = open(f'test.txt', 'r', encoding='utf-8')
tb_names = {row.rstrip('\n') for row in _file.readlines()}
brow_big = tb.Browser("default")
tb_names_big = {row[0] for row in brow_big.get_self_forumlist()}
brow_small = tb.Browser("backup")
tb_names_small = {row[0] for row in brow_small.get_self_forumlist()}

for tb_name in (tb_names-tb_names_big):
    if not brow_big.get_fid(tb_name):
        continue
    if not brow_big.like_forum(tb_name):
        break

for tb_name in (tb_names-tb_names_small):
    if not brow_small.get_fid(tb_name):
        continue
    if not brow_small.like_forum(tb_name):
        break
