# -*- coding:utf-8 -*-
import tiebaBrowser as tb

tieba_name = '好听的歌'
brow = tb.Browser("default")

res=brow.get_posts(7573068114,with_comments=True)
pass
