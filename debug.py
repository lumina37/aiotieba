# -*- coding:utf-8 -*-
import tiebaBrowser as tb

tieba_name = 'asoul'
brow = tb.Browser("default")

threads=brow.get_threads('asoul')
print(f"thread num:{len(threads)}")
for thread in threads:
    print(thread.title)
