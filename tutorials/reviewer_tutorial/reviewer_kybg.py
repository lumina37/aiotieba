import argparse
import asyncio
import re
from collections.abc import Callable
from typing import Optional, Union

import aiotieba as tb


class MyReviewer(tb.Reviewer):
    def __init__(self, BDUSS_key: str, fname: str):
        super().__init__(BDUSS_key, fname)

        self.thread_checkers = [self.check_thread]
        self.post_checkers = [self.check_post, self.check_text]
        self.comment_checkers = [self.check_comment, self.check_text]

    def time_interval(self) -> Callable[[], float]:
        def _() -> float:
            return 12.0

        return _

    async def check_thread(self, thread: tb.Thread) -> Optional[tb.Punish]:

        if not (user := thread.user):
            return

        if thread.share_origin.vote_info:
            # 转发来源包含投票
            if user.level <= 9:
                return tb.Punish(tb.DelFlag.DELETE, 10, note="广告 申诉可解")

        # 帖子文本内容警告
        if re.search('\\.cc|п|⒏|㏄|荬', thread.text):
            return tb.Punish(tb.DelFlag.DELETE, 10, note="广告 申诉可解")

    async def check_post(self, post: tb.Post) -> Optional[tb.Punish]:

        for img_content in post.contents.imgs:
            img = await self.client.get_image(img_content.src)
            if img.size == 0:
                continue
            permission = await self.get_imghash(img)
            if permission <= -5:
                return tb.Punish(tb.DelFlag.DELETE, 10, '广告 申诉可解')
            if permission == -3:
                return tb.Punish(tb.DelFlag.DELETE, 1, "违规图片-3")
            if permission == -2:
                return tb.Punish(tb.DelFlag.DELETE)

    async def check_comment(self, comment: tb.Comment) -> Optional[tb.Punish]:

        if comment.user.level >= 7:
            return

        if comment.contents.links:
            for link in comment.contents.links:
                if link.url.host.endswith(
                    (
                        "mr.baidu.com",
                        "mbd.baidu.com",
                        ".online",
                        "dwz.cn",
                        "t.cn",
                    )
                ):
                    return tb.Punish(tb.DelFlag.DELETE, 10, note="广告 申诉可解")

    async def check_text(self, obj: Union[tb.Thread, tb.Post, tb.Comment]) -> Optional[tb.Punish]:

        if obj.user.level >= 7:
            return

        for at in obj.contents.ats:
            if at.user_id == 2093991357:
                return tb.Punish(tb.DelFlag.DELETE, 10, note="广告 申诉可解")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no_dbg",
        help="调试模式默认开启以避免误操作 生产环境下使用该选项将其关闭",
        action="store_true",
    )
    args = parser.parse_args()

    async def main():
        async with MyReviewer('kybg', '抗压背锅') as reviewer:
            if args.no_dbg:
                await reviewer.review_loop()
            else:
                await reviewer.review_debug()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
