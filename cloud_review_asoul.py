# -*- coding:utf-8 -*-
import asyncio
import re
import sys
import time
import traceback
from collections import Counter

import tiebaBrowser as tb


class AsoulCloudReview(tb.Reviewer):

    __slots__ = ['white_kw_exp', 'water_restrict_flag']

    def __init__(self, BDUSS_key, tieba_name) -> None:
        super().__init__(BDUSS_key, tieba_name)
        white_kw_list = ['管人|(哪个|什么)v|bv|联动|歌回|杂谈|歌力|企划|切片|前世|毕业|sc|弹幕|同接|二次元|原批|牧场|周边|史书|饭圈|滑坡',
                         '(a|b|睿|皇协|批|p)站|b博|海鲜|(v|a)(吧|8)|nga|404|ytb|论坛|字幕组|粉丝群|直播间|魂组|录播',
                         'asoul|皮套|纸片人|套皮|嘉然|然然|向晚|晚晚|乃琳|奶琳|贝拉|拉姐|珈乐|羊驼|a(骚|s|手)|向晚|歌姬|乃贝|晚饭|大头',
                         '开播|共振|取关|牧场|啊啊啊|麻麻|别急|可爱|sad|感叹|速速|我超|存牌|狠狠|切割|牛牛|一把子|幽默|GNK48|汴京|抱团|别融',
                         '嘉心糖|顶碗人|贝极星|奶淇淋|n70|皇(珈|家)|黄嘉琪|泥哥|(a|b|豆|d|抖|快|8|吧)(u|友)|一个魂|粉丝|ylg|mmr|低能|易拉罐|脑弹|铝制品|纯良']
        self.white_kw_exp = re.compile('|'.join(white_kw_list), re.I)
        self.water_restrict_flag = False

    async def run(self) -> None:

        while 1:
            try:
                start_time = time.perf_counter()

                # 获取限水标记
                self.water_restrict_flag = await self.database.is_tid_hide(self.tieba_name, 0)

                # 获取主题帖列表
                threads = await self.get_threads(self.tieba_name)
                # 创建异步任务列表 并规定每个任务的延迟时间 避免高并发下的网络阻塞
                coros = [self._handle_thread(thread, idx/5)
                         for idx, thread in enumerate(threads)]
                # 并发运行协程
                del_flags = await asyncio.gather(*coros)

                def _yield_user_id():
                    for idx, thread in enumerate(threads):
                        if not del_flags[idx] and (user_id := thread.author_id) != 0 and thread.reply_num < 15 and not self.white_kw_exp.search(thread.text):
                            yield user_id
                # 为每个user_id统计无关水帖数
                water_stat = Counter(_yield_user_id())

                water_user_ids = []
                for user_id, count in water_stat.items():
                    # 无关水数量大于等于5 则屏蔽该用户在版面上的所有无关水
                    if count >= 5:
                        tb.log.info(f"Clear Water {user_id}")
                        water_user_ids.append(user_id)

                if water_user_ids:
                    # 因为治水功能很少被触发 所以采用int计数+二次遍历而不是列表计数的设计来提升性能
                    coros = [self.hide_thread(self.tieba_name, thread.tid)
                             for thread in threads if thread.author_id in water_user_ids]
                    await asyncio.gather(*coros)

                tb.log.debug(
                    f"Cycle time_cost: {time.perf_counter()-start_time:.4f}")
                # 主动释放CPU 转而运行其他协程
                await asyncio.sleep(30)

            except Exception:
                tb.log.critical(
                    f"Unexcepted error:{traceback.format_exc()}")
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
                f"Try to delete thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}. line:{line}")
            await self.del_thread(self.tieba_name, thread.tid)
            return True
        elif del_flag == 2:
            # 屏蔽帖
            tb.log.info(
                f"Try to hide thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}. line:{line}")
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

        if self.water_restrict_flag:
            # 当前吧处于高峰期限水状态
            if await self.database.is_tid_hide(self.tieba_name, thread.tid) == False:
                await self.database.update_tid(self.tieba_name, thread.tid, True)
                return 2, 0, sys._getframe().f_lineno

        # 该帖子里的内容没有发生任何变化 直接跳过所有后续检查
        if thread.last_time <= await self.database.get_id(self.tieba_name, thread.tid):
            return 0, 0, 0

        # 回复数>50且点赞数>回复数的两倍则判断为热帖
        is_hot_thread = thread.reply_num >= 50 and thread.agree > thread.reply_num*2
        if is_hot_thread:
            # 同时拉取热门序和时间倒序的回复列表
            posts, reverse_posts = await asyncio.gather(self.get_posts(thread.tid, sort=2, with_comments=True), self.get_posts(thread.tid, sort=1, with_comments=True))
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
        await self.database.update_id(self.tieba_name, thread.tid, thread.last_time)
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
            await self.database.update_id(self.tieba_name, post.pid, post.reply_num)
            return -1, 0, 0

        del_flag, block_days, line = await self._check_text(post)
        if del_flag == -1:
            pass
        elif del_flag == 1:
            # 向上层函数传递封禁请求
            return 1, block_days, line
        elif del_flag == 0:
            # 无异常 继续检查
            for img_content in post.contents.imgs:
                img = await self.url2image(img_content.src)
                if img is None:
                    continue
                if await self.has_imghash(img):
                    return 1, 0, sys._getframe().f_lineno

        if post.comments:
            # 并发检查楼中楼内容 因为是CPU密集任务所以不需要设计delay
            coros = [self._handle_comment(comment)
                     for comment in post.comments]
            await asyncio.gather(*coros)

        # 缓存该pid的子结点编辑状态
        await self.database.update_id(self.tieba_name, post.pid, post.reply_num)
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
                f"Try to delete post {comment.text} post by {comment.user.log_name}. level:{comment.user.level}. line:{line}")
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
            if isinstance(comment.contents[0], tb._types.FragLink):
                # 楼中楼一级号发链接 删
                return 1, 0, sys._getframe().f_lineno

        # 缓存该pid
        await self.database.update_id(self.tieba_name, comment.pid)
        return 0, 0, 0

    async def _check_text(self, obj):
        """
        检查文本内容

        Returns:
            del_flag: int -1为白名单 0为普通 1为删帖
            day: int 封号天数
            line: int 处罚规则所在的行号
        """

        is_white = await self.database.is_user_id_white(self.tieba_name, obj.user.user_id)
        if is_white == True:
            # 白名单用户
            return -1, 0, 0
        elif is_white == False:
            # 黑名单用户 删回复并封十天
            return 1, 10, sys._getframe().f_lineno

        text = obj.text
        if re.search("((?<![a-z])v|瞳|梓|罐|豆|鸟|鲨)(÷|/|／|➗|畜|处|除|初|醋)|椰子汁|🥥|东雪莲|莲宝", text, re.I):
            return 1, 0, sys._getframe().f_lineno

        level = obj.user.level
        if level > 6:
            # 用户等级大于6则跳过后续检查
            return 0, 0, 0

        # 内容中是否有白名单关键字
        has_white_kw = True if self.white_kw_exp.search(text) else False
        if has_white_kw:
            return 0, 0, 0

        # 内容中是否有罕见的联系方式
        has_rare_contact = True if self.expressions.contact_rare_exp.search(
            text) else False
        # 内容中是否有联系方式
        has_contact = True if (
            has_rare_contact or self.expressions.contact_exp.search(text)) else False

        if level < 7:
            if self.expressions.job_nocheck_exp.search(text):
                # 招兼职 十天删帖
                return 1, 10, sys._getframe().f_lineno

            if self.expressions.business_exp.search(text):
                # 商业推广 十天删帖
                return 1, 0, 0

            has_job = True if self.expressions.job_exp.search(text) else False
            if self.expressions.job_check_exp.search(text) and (has_job or has_contact):
                # 易误判的兼职关键词 二重检验
                return 1, 0, 0
            if self.expressions.course_exp.search(text) and self.expressions.course_check_exp.search(text):
                # 易误判的课程推广关键词 二重检验
                return 1, 0, 0

        return 0, 0, 0


if __name__ == '__main__':

    async def main():
        async with AsoulCloudReview('starry', 'asoul') as review:
            await review.run()

    try:
        asyncio.run(main())
    except:
        pass
