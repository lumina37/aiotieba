# -*- coding:utf-8 -*-
import asyncio
import re
import sys
import time
import traceback

import tiebaBrowser as tb


class HanimeCloudReview(tb.Reviewer):

    __slots__ = ['white_kw_exp']

    def __init__(self, BDUSS_key, tieba_name) -> None:
        super().__init__(BDUSS_key, tieba_name)
        self.white_kw_exp = re.compile('default默认', re.I)

    async def run(self) -> None:

        while 1:
            try:
                start_time = time.perf_counter()

                # 获取主题帖列表
                threads = await self.get_threads(self.tieba_name)
                # 创建异步任务列表 并规定每个任务的延迟时间 避免高并发下的网络阻塞
                coros = [self._handle_thread(thread, idx / 5) for idx, thread in enumerate(threads)]
                # 并发运行协程
                await asyncio.gather(*coros)

                tb.log.debug(f"Cycle time_cost: {time.perf_counter()-start_time:.4f}")
                # 主动释放CPU 转而运行其他协程
                await asyncio.sleep(20)

            except Exception:
                tb.log.critical(f"Unexcepted error:{traceback.format_exc()}")
                return

    async def _handle_thread(self, thread: tb.Thread, delay: float) -> None:
        """
        处理thread

        Returns:
            del_flag: bool True则帖已删除 False则无操作
        """

        if thread.is_livepost:
            # 置顶话题直接返回
            return

        if delay:
            # 无延迟则不使用await 避免不必要的切换开销
            await asyncio.sleep(delay)

        # 检查帖子内容
        del_flag, block_days, line = await self._check_thread(thread)
        if block_days:
            # 封禁
            await self.block(self.tieba_name, thread.user, day=block_days, reason=f"line:{line}")
        if del_flag == 0:
            pass
        elif del_flag == 1:
            # 删帖
            tb.log.info(
                f"Try to delete thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}. line:{line}"
            )
            await self.del_thread(self.tieba_name, thread.tid)
            return True
        elif del_flag == 2:
            # 屏蔽帖
            tb.log.info(
                f"Try to hide thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}. line:{line}"
            )
            await self.hide_thread(self.tieba_name, thread.tid)
            return True

        return False

    async def _check_thread(self, thread: tb.Thread) -> tuple[int, int, int]:
        """
        检查主题帖内容

        Returns:
            del_flag: int 0则不操作 1则删主题帖 2则屏蔽主题帖
            block_days: int 封号天数
            line: int 处罚规则所在的行号
        """

        # 该帖子里的内容没有发生任何变化 直接跳过所有后续检查
        if thread.last_time <= await self.database.get_id(self.tieba_name, thread.tid):
            return 0, 0, 0

        # 回复数>50且点赞数>回复数的两倍则判断为热帖
        is_hot_thread = thread.reply_num >= 50 and thread.agree > thread.reply_num * 2
        if is_hot_thread:
            # 同时拉取热门序和时间倒序的回复列表
            posts, reverse_posts = await asyncio.gather(self.get_posts(thread.tid, sort=2, with_comments=True),
                                                        self.get_posts(thread.tid, sort=1, with_comments=True))
        else:
            # 仅拉取时间倒序的回复列表
            posts = await self.get_posts(thread.tid, sort=1, with_comments=True)

        if len(posts) == 0:
            return 0, 0, 0

        # 没有该步骤则thread.user不包含等级 影响判断
        thread.user = posts.thread.user

        del_flag, block_days, line = await self._check_text(thread)
        if del_flag == -1:
            pass
        elif del_flag == 1:
            # 向上层函数传递封禁请求
            return 1, block_days, line
        elif del_flag == 0:
            # 无异常 继续检查
            if thread.user.priv_reply == 6:
                # 楼主锁回复 直接删帖
                return 1, 0, sys._getframe().f_lineno

        # 并发检查回复内容 因为是CPU密集任务所以不需要设计delay
        coros = [self._handle_post(post) for post in posts]
        if is_hot_thread:
            coros.extend([self._handle_post(post) for post in reverse_posts])
        await asyncio.gather(*coros)

        # 缓存该tid的子孙结点编辑状态
        await self.database.add_id(self.tieba_name, thread.tid, thread.last_time)
        return 0, 0, 0

    async def _handle_post(self, post: tb.Post) -> None:
        """
        处理post
        """

        del_flag, block_days, line = await self._check_post(post)
        if block_days:
            await self.block(self.tieba_name, post.user, day=block_days, reason=f"line:{line}")
        if del_flag <= 0:
            pass
        elif del_flag == 1:
            # 内容违规 删回复
            tb.log.info(
                f"Try to delete post {post.text} post by {post.user.log_name}. level:{post.user.level}. line:{line}")
            await self.del_post(self.tieba_name, post.tid, post.pid)
            return

    async def _check_post(self, post: tb.Post) -> tuple[int, int, int]:
        """
        检查回复内容

        Returns:
            del_flag: int -1为白名单 0为普通 1为删回复
            block_days: int 封号天数
            line: int 处罚规则所在的行号
        """

        # 该回复下的楼中楼大概率没有发生任何变化 直接跳过所有后续检查
        if post.reply_num == (id_last_edit := await self.database.get_id(self.tieba_name, post.pid)):
            return -1, 0, 0
        # 该回复下的楼中楼可能被抽 需要缓存抽楼后的reply_num
        elif post.reply_num < id_last_edit:
            await self.database.add_id(self.tieba_name, post.pid, post.reply_num)
            return -1, 0, 0

        del_flag, block_days, line = await self._check_text(post)
        if del_flag == -1:
            pass
        elif del_flag == 1:
            # 向上层函数传递封禁请求
            return 1, block_days, line
        elif del_flag == 0:
            # 无异常 继续检查
            for img_frag in post.contents.imgs:
                img = await self.url2image(img_frag.src)
                if img is None:
                    continue
                if await self.has_imghash(img):
                    return 1, 0, sys._getframe().f_lineno

        if post.comments:
            # 并发检查楼中楼内容 因为是CPU密集任务所以不需要设计delay
            coros = [self._handle_comment(comment) for comment in post.comments]
            await asyncio.gather(*coros)

        # 缓存该pid的子结点编辑状态
        await self.database.add_id(self.tieba_name, post.pid, post.reply_num)
        return 0, 0, 0

    async def _handle_comment(self, comment: tb.Comment) -> None:
        """
        处理comment
        """

        del_flag, block_days, line = await self._check_comment(comment)
        if block_days:
            await self.block(self.tieba_name, comment.user, day=block_days, reason=f"line:{line}")
        if del_flag <= 0:
            pass
        elif del_flag == 1:
            # 内容违规 删楼中楼
            tb.log.info(
                f"Try to delete post {comment.text} post by {comment.user.log_name}. level:{comment.user.level}. line:{line}"
            )
            await self.del_post(self.tieba_name, comment.tid, comment.pid)
            return

    async def _check_comment(self, comment: tb.Comment) -> tuple[int, int, int]:
        """
        检查楼中楼内容

        Returns:
            del_flag: int -1为白名单 0为普通 1为删回复
            block_days: int 封号天数
            line: int 处罚规则所在的行号
        """

        if await self.database.get_id(self.tieba_name, comment.pid) != -1:
            return -1, 0, 0

        del_flag, day, line = await self._check_text(comment)
        if del_flag == -1:
            # 白名单 跳过后续检查
            return -1, 0, 0
        elif del_flag == 1:
            # 向上层函数传递封禁请求
            return 1, day, line
        elif del_flag == 0:
            # 无异常 继续检查
            pass

        # 缓存该pid
        await self.database.add_id(self.tieba_name, comment.pid)
        return 0, 0, 0

    async def _check_text(self, obj):
        """
        检查文本内容

        Returns:
            del_flag: int -1为白名单 0为普通 1为删帖
            day: int 封号天数
            line: int 处罚规则所在的行号
        """

        permission = await self.database.get_user_id(self.tieba_name, obj.user.user_id)
        if permission >= 1:
            # 白名单用户
            return -1, 0, 0
        elif permission <= -5:
            # 黑名单用户 删回复并封十天
            return 1, 10, sys._getframe().f_lineno

        level = obj.user.level
        if level > 6:
            # 用户等级大于6则跳过后续检查
            return 0, 0, 0

        text = obj.text
        if re.search("魅.?魔.{0,5}(】|斯黛拉)|足硿笨", text, re.I):
            return 1, 1, sys._getframe().f_lineno

        return 0, 0, 0


if __name__ == '__main__':

    async def main():
        async with HanimeCloudReview('starry', '宫漫') as review:
            await review.run()

    try:
        asyncio.run(main())
    except:
        pass
