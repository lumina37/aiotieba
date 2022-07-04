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
                start_time = time.perf_counter()

                # 获取主题帖列表
                threads = await self.get_threads(self.fname)
                # 创建异步任务列表 并规定每个任务的延迟时间 避免高并发下的网络阻塞
                coros = [self._handle_thread(thread, idx / 10) for idx, thread in enumerate(threads)]
                # 并发运行协程
                await asyncio.gather(*coros)

                tb.LOG.debug(f"Cycle time_cost: {time.perf_counter()-start_time:.4f}")
                # 主动释放CPU 转而运行其他协程
                await asyncio.sleep(60)

            except Exception:
                tb.LOG.critical("Unexcepted error", exc_info=True)
                return

    async def _handle_thread(self, thread: tb.Thread, delay: float) -> None:
        """
        处理thread
        """

        if thread.is_livepost:
            # 置顶话题直接返回
            return

        if delay:
            # 无延迟则不使用await 避免不必要的切换开销
            await asyncio.sleep(delay)

        # 检查帖子内容
        punish = await self._check_thread(thread)
        if punish.block_days:
            # 封禁
            await self.block(self.fname, thread.user, day=punish.block_days, reason=punish.note)
        if punish.del_flag == 0:
            pass
        elif punish.del_flag == 1:
            # 删帖
            tb.LOG.info(
                f"Try to delete thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}. {punish.note}"
            )
            await self.del_thread(thread.fid, thread.tid)
            return
        elif punish.del_flag == 2:
            # 屏蔽帖
            tb.LOG.info(
                f"Try to hide thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}. {punish.note}"
            )
            await self.hide_thread(thread.fid, thread.tid)
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

        # 回复数>50且点赞数>回复数的两倍则判断为热帖
        is_hot_thread = thread.reply_num >= 50 and thread.agree > thread.reply_num * 2
        if is_hot_thread:
            # 同时拉取热门序和最后一页的回复列表
            hot_posts, posts = await asyncio.gather(
                self.get_posts(thread.tid, sort=2, with_comments=True),
                self.get_posts(thread.tid, pn=99999, with_comments=True),
            )
        else:
            # 仅拉取最后一页的回复列表
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

        # 并发检查回复内容 因为是CPU密集任务所以不需要设计delay
        coros = [self._handle_post(post) for post in posts]
        if is_hot_thread:
            coros.extend([self._handle_post(post) for post in hot_posts])
        await asyncio.gather(*coros)

        # 缓存该tid的子孙结点编辑状态
        await self.add_id(thread.tid, thread.last_time)
        return Punish()

    async def _handle_post(self, post: tb.Post) -> None:
        """
        处理post
        """

        punish = await self._check_post(post)
        if punish.block_days:
            await self.block(self.fname, post.user, day=punish.block_days, reason=punish.note)
        if punish.del_flag <= 0:
            pass
        elif punish.del_flag == 1:
            # 内容违规 删回复
            tb.LOG.info(
                f"Try to delete post {post.text} post by {post.user.log_name}. level:{post.user.level}. {punish.note}"
            )
            await self.del_post(post.fid, post.tid, post.pid)
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
            await self.add_id(post.pid, post.reply_num)
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

        if post.comments:
            # 并发检查楼中楼内容 因为是CPU密集任务所以不需要设计delay
            coros = [self._handle_comment(comment) for comment in post.comments]
            await asyncio.gather(*coros)

        # 缓存该pid的子结点编辑状态
        await self.add_id(post.pid, post.reply_num)
        return Punish()

    async def _handle_comment(self, comment: tb.Comment) -> None:
        """
        处理comment
        """

        punish = await self._check_comment(comment)
        if punish.block_days:
            await self.block(self.fname, comment.user, day=punish.block_days, reason=punish.note)
        if punish.del_flag <= 0:
            pass
        elif punish.del_flag == 1:
            # 内容违规 删楼中楼
            tb.LOG.info(
                f"Try to delete post {comment.text} post by {comment.user.log_name}. level:{comment.user.level}. {punish.note}"
            )
            await self.del_post(comment.fid, comment.tid, comment.pid)
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
        if re.search("\u05af|足硿笨|𝒂𝒋|𝒗|𝒍𝒊𝒌𝒆", text, re.I):
            return Punish(1, 1)

        return Punish()


if __name__ == '__main__':

    async def main():
        async with CloudReview('starry', '宫漫') as review:
            await review.run()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
