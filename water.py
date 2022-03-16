# -*- coding:utf-8 -*-
import time
import tiebaBrowser as tb

brow = tb.Browser("default")
for tb_name, tid in [('元气骑士', 5074946575), ('lol半价', 2986143112), ('asoul', 7230587602)]:
    for i in range(6):
        brow.add_post(tb_name, tid, str(i))
        time.sleep(300)
brow.add_post('soulknight', 6128818144, '0')
brow.add_post('starry', 6154402005, '0')
