# -*- coding:utf-8 -*-
import asyncio
import re
import sys
import time
from typing import Union

import aiotieba as tb


class Punish(object):
    """
    处罚操作

    Fields:
        del_flag (int, optional): -1白名单 0普通 1删帖 2屏蔽帖. Defaults to 0.
        block_days (int, optional): 封禁天数. Defaults to 0.
        note (str, optional): 处罚理由. Defaults to ''.
    """

    __slots__ = ['del_flag', 'block_days', 'note']

    def __init__(self, del_flag: int = 0, block_days: int = 0, note: str = ''):
        self.del_flag: int = del_flag
        self.block_days: int = block_days
        if del_flag > 0:
            line = sys._getframe(1).f_lineno
            self.note = f"line:{line} {note}" if note else f"line:{line}"
        else:
            self.note = note


class CloudReview(tb.Reviewer):

    __slots__ = []

    def __init__(self, BDUSS_key, fname) -> None:
        super().__init__(BDUSS_key, fname)

    async def __aenter__(self) -> "CloudReview":
        return await self.enter()

    async def run(self) -> None:

        while 1:
            try:
                asyncio.create_task(self.check_threads())
                # 主动释放CPU 转而运行其他协程
                await asyncio.sleep(45)

            except Exception:
                tb.LOG.critical("Unexcepted error", exc_info=True)
                return

    async def check_threads(self, pn: int = 1) -> None:
        start_time = time.perf_counter()
        # 获取主题帖列表
        threads = await self.get_threads(pn)
        # 并发运行协程检查主题帖内的违规内容
        await asyncio.gather(*[self._handle_thread(thread) for thread in threads])

        tb.LOG.debug(f"Cycle time_cost={time.perf_counter()-start_time:.4f}")

    async def _handle_thread(self, thread: tb.Thread) -> None:
        """
        处理thread
        """

        if thread.is_livepost:
            # 置顶话题直接返回
            return

        # 检查帖子内容
        punish = await self._check_thread(thread)
        if punish.block_days:
            # 封禁
            await self.block(thread.user.portrait, day=punish.block_days, reason=punish.note)
        if punish.del_flag == 0:
            pass
        elif punish.del_flag == 1:
            # 删帖
            tb.LOG.info(
                f"Try to del. text={thread.text} user={thread.user} level={thread.user.level} note={punish.note}"
            )
            await self.del_thread(thread.tid)
            return
        elif punish.del_flag == 2:
            # 屏蔽帖
            tb.LOG.info(
                f"Try to hide. text={thread.text} user={thread.user} level={thread.user.level} note={punish.note}"
            )
            await self.hide_thread(thread.tid)
            return

        return

    async def _check_thread(self, thread: tb.Thread) -> Punish:
        """
        检查主题帖内容

        Returns:
            Punish
        """

        # 该帖子里的内容没有发生任何变化 直接跳过所有后续检查
        if thread.last_time <= await self.get_id(thread.tid):
            return Punish()

        posts = await self.get_posts(thread.tid, pn=99999, with_comments=True)

        if len(posts) == 0:
            return Punish()

        # 没有该步骤则thread.user不包含等级 影响判断
        thread._user = posts.thread.user

        punish = await self._check_text(thread)
        if punish.del_flag == -1:
            pass
        elif punish.del_flag == 1:
            # 向上层函数传递封禁请求
            return punish
        elif punish.del_flag == 0:
            # 无异常 继续检查
            pass

        if thread.last_time - thread.create_time > 365 * 24 * 3600 and thread.last_time > 1657702000:
            for post, next_post in zip(posts, posts[1:]):
                if next_post.create_time - post.create_time > 90 * 24 * 3600:
                    await self.block(thread.fid, next_post.user.portrait, day=1, note="挖坟")
                    await self.del_post(next_post.tid, next_post.pid)

        # 并发检查回复内容 因为是CPU密集任务所以不需要设计delay
        coros = [self._handle_post(post) for post in posts]
        await asyncio.gather(*coros)

        # 缓存该tid的子孙结点编辑状态
        await self.add_id(thread.tid, id_last_edit=thread.last_time)
        return Punish()

    async def _handle_post(self, post: tb.Post) -> None:
        """
        处理post
        """

        punish = await self._check_post(post)
        if punish.block_days:
            await self.block(post.user.portrait, day=punish.block_days, reason=punish.note)
        if punish.del_flag <= 0:
            pass
        elif punish.del_flag == 1:
            # 内容违规 删回复
            tb.LOG.info(f"Try to del. text={post.text} user={post.user} level={post.user.level} note={punish.note}")
            await self.del_post(post.tid, post.pid)
            return

    async def _check_post(self, post: tb.Post) -> Punish:
        """
        检查回复内容

        Returns:
            Punish
        """

        # 该回复下的楼中楼大概率没有发生任何变化 直接跳过所有后续检查
        if post.reply_num == (id_last_edit := await self.get_id(post.pid)):
            return Punish(-1)
        # 该回复下的楼中楼可能被抽 需要缓存抽楼后的reply_num
        elif post.reply_num < id_last_edit:
            await self.add_id(post.pid, id_last_edit=post.reply_num)
            return Punish(-1)

        punish = await self._check_text(post)
        if punish.del_flag == -1:
            pass
        elif punish.del_flag == 1:
            # 向上层函数传递封禁请求
            return punish
        elif punish.del_flag == 0:
            # 无异常 继续检查
            pass

        text = post.text
        if text.count('\n') > 128:
            # 闪光弹
            return Punish(1, 0, note="闪光弹")

        if post.comments:
            # 并发检查楼中楼内容 因为是CPU密集任务所以不需要设计delay
            coros = [self._handle_comment(comment) for comment in post.comments]
            await asyncio.gather(*coros)

        # 缓存该pid的子结点编辑状态
        await self.add_id(post.pid, id_last_edit=post.reply_num)
        return Punish()

    async def _handle_comment(self, comment: tb.Comment) -> None:
        """
        处理comment
        """

        punish = await self._check_comment(comment)
        if punish.block_days:
            await self.block(comment.user.portrait, day=punish.block_days, reason=punish.note)
        if punish.del_flag <= 0:
            pass
        elif punish.del_flag == 1:
            # 内容违规 删楼中楼
            tb.LOG.info(
                f"Try to del. text={comment.text} user={comment.user} level={comment.user.level} note={punish.note}"
            )
            await self.del_post(comment.tid, comment.pid)
            return

    async def _check_comment(self, comment: tb.Comment) -> Punish:
        """
        检查楼中楼内容

        Returns:
            Punish
        """

        if await self.get_id(comment.pid) != -1:
            return Punish(-1)

        punish = await self._check_text(comment)
        if punish.del_flag == -1:
            # 白名单 跳过后续检查
            return punish
        elif punish.del_flag == 1:
            # 向上层函数传递封禁请求
            return punish
        elif punish.del_flag == 0:
            # 无异常 继续检查
            pass

        # 缓存该pid
        await self.add_id(comment.pid)
        return Punish()

    async def _check_text(self, obj: Union[tb.Thread, tb.Post, tb.Comment]):
        """
        检查文本内容

        Returns:
            Punish
        """

        # 查数据库获取用户权限级别
        permission = await self.get_user_id(obj.user.user_id)
        if permission >= 1:
            # 白名单用户
            return Punish(-1)
        elif permission <= -5:
            # 黑名单用户 删回复并封十天
            return Punish(1, 10, note="黑名单")

        level = obj.user.level
        if level > 6:
            # 用户等级大于6则跳过后续检查
            return Punish()

        text = obj.text
        if re.search("蜘蛛", text):
            return Punish(1)

        return Punish()


if __name__ == '__main__':

    async def main():
        async with CloudReview('listener', 'vtuber') as review:
            await review.run()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
