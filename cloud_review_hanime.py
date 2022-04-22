# -*- coding:utf-8 -*-
import asyncio
import re
import sys
import time

import tiebaBrowser as tb


class CloudReview(tb.Reviewer):

    __slots__ = ['white_kw_exp']

    class Punish(object):
        """
        惩罚操作

        Fields:
            del_flag (int, optional): -1白名单 0普通 1删帖 2屏蔽帖
            block_days (int, optional): 封禁天数
            line (int): 处罚产生的行号 默认生成
        """

        __slots__ = ['del_flag', 'block_days', 'line']

        def __init__(self, del_flag: int = 0, block_days: int = 0):
            self.del_flag: int = del_flag
            self.block_days: int = block_days
            self.line: int = sys._getframe(1).f_lineno if del_flag > 0 else 0

    def __init__(self, BDUSS_key, tieba_name) -> None:
        super().__init__(BDUSS_key, tieba_name)
        self.white_kw_exp = re.compile('default默认', re.I)

    async def __aenter__(self) -> "CloudReview":
        await self._init()
        return self

    async def run(self) -> None:

        while 1:
            try:
                start_time = time.perf_counter()

                # 获取主题帖列表
                threads = await self.get_threads(self.tieba_name)
                # 创建异步任务列表 并规定每个任务的延迟时间 避免高并发下的网络阻塞
                coros = [self._handle_thread(thread, idx / 10) for idx, thread in enumerate(threads)]
                # 并发运行协程
                await asyncio.gather(*coros)

                tb.log.debug(f"Cycle time_cost: {time.perf_counter()-start_time:.4f}")
                # 主动释放CPU 转而运行其他协程
                await asyncio.sleep(60)

            except Exception:
                tb.log.critical("Unexcepted error", exc_info=True)
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
            await self.block(self.tieba_name, thread.user, day=punish.block_days, reason=f"line:{punish.line}")
        if punish.del_flag == 0:
            pass
        elif punish.del_flag == 1:
            # 删帖
            tb.log.info(
                f"Try to delete thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}. line:{punish.line}"
            )
            await self.del_thread(self.tieba_name, thread.tid)
            return
        elif punish.del_flag == 2:
            # 屏蔽帖
            tb.log.info(
                f"Try to hide thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}. line:{punish.line}"
            )
            await self.hide_thread(self.tieba_name, thread.tid)
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
            return self.Punish()

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
            return self.Punish()

        # 没有该步骤则thread.user不包含等级 影响判断
        thread.user = posts.thread.user

        punish = await self._check_text(thread)
        if punish.del_flag == -1:
            pass
        elif punish.del_flag == 1:
            # 向上层函数传递封禁请求
            return punish
        elif punish.del_flag == 0:
            # 无异常 继续检查
            if thread.user.priv_reply == 6:
                # 楼主锁回复 直接删帖
                return self.Punish(1)

        # 并发检查回复内容 因为是CPU密集任务所以不需要设计delay
        coros = [self._handle_post(post) for post in posts]
        if is_hot_thread:
            coros.extend([self._handle_post(post) for post in hot_posts])
        await asyncio.gather(*coros)

        # 缓存该tid的子孙结点编辑状态
        await self.add_id(thread.tid, thread.last_time)
        return self.Punish()

    async def _handle_post(self, post: tb.Post) -> None:
        """
        处理post
        """

        punish = await self._check_post(post)
        if punish.block_days:
            await self.block(self.tieba_name, post.user, day=punish.block_days, reason=f"line:{punish.line}")
        if punish.del_flag <= 0:
            pass
        elif punish.del_flag == 1:
            # 内容违规 删回复
            tb.log.info(
                f"Try to delete post {post.text} post by {post.user.log_name}. level:{post.user.level}. line:{punish.line}"
            )
            await self.del_post(self.tieba_name, post.tid, post.pid)
            return

    async def _check_post(self, post: tb.Post) -> Punish:
        """
        检查回复内容

        Returns:
            Punish
        """

        # 该回复下的楼中楼大概率没有发生任何变化 直接跳过所有后续检查
        if post.reply_num == (id_last_edit := await self.get_id(post.pid)):
            return self.Punish(-1)
        # 该回复下的楼中楼可能被抽 需要缓存抽楼后的reply_num
        elif post.reply_num < id_last_edit:
            await self.add_id(post.pid, post.reply_num)
            return self.Punish(-1)

        punish = await self._check_text(post)
        if punish.del_flag == -1:
            pass
        elif punish.del_flag == 1:
            # 向上层函数传递封禁请求
            return punish
        elif punish.del_flag == 0:
            # 无异常 继续检查
            for img_frag in post.contents.imgs:
                img = await self.url2image(img_frag.src)
                if img is None:
                    continue
                if await self.has_imghash(img):
                    return self.Punish(1)

        if post.comments:
            # 并发检查楼中楼内容 因为是CPU密集任务所以不需要设计delay
            coros = [self._handle_comment(comment) for comment in post.comments]
            await asyncio.gather(*coros)

        # 缓存该pid的子结点编辑状态
        await self.add_id(post.pid, post.reply_num)
        return self.Punish()

    async def _handle_comment(self, comment: tb.Comment) -> None:
        """
        处理comment
        """

        punish = await self._check_comment(comment)
        if punish.block_days:
            await self.block(self.tieba_name, comment.user, day=punish.block_days, reason=f"line:{punish.line}")
        if punish.del_flag <= 0:
            pass
        elif punish.del_flag == 1:
            # 内容违规 删楼中楼
            tb.log.info(
                f"Try to delete post {comment.text} post by {comment.user.log_name}. level:{comment.user.level}. line:{punish.line}"
            )
            await self.del_post(self.tieba_name, comment.tid, comment.pid)
            return

    async def _check_comment(self, comment: tb.Comment) -> Punish:
        """
        检查楼中楼内容

        Returns:
            Punish
        """

        if await self.get_id(comment.pid) != -1:
            return self.Punish(-1)

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
        return self.Punish()

    async def _check_text(self, obj):
        """
        检查文本内容

        Returns:
            Punish
        """

        permission = await self.get_user_id(obj.user.user_id)
        if permission >= 1:
            # 白名单用户
            return self.Punish(-1)
        elif permission <= -5:
            # 黑名单用户 删回复并封十天
            return self.Punish(1, 10)

        level = obj.user.level
        if level > 6:
            # 用户等级大于6则跳过后续检查
            return self.Punish()

        text = obj.text
        if re.search("魅.?魔.{0,5}(】|斯黛拉)|足硿笨", text, re.I):
            return self.Punish(1, 1)

        return self.Punish()


if __name__ == '__main__':

    async def main():
        async with CloudReview('starry', '宫漫') as review:
            await review.run()

    try:
        asyncio.run(main())
    except BaseException:
        pass
