# -*- coding:utf-8 -*-
import tiebaBrowser as tb

for key in ['default', 'backup', 'listener']:
    brow = tb.Browser(key)
    for tb_name in ['asoul', 'v', 'vtuber自由讨论']:
        brow.sign_forum(tb_name)
