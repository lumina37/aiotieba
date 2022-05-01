# -*- coding:utf-8 -*-
import asyncio
import re
import sys
import time
from collections import Counter

import tiebaBrowser as tb


class CloudReview(tb.Reviewer):

    __slots__ = ['white_kw_exp', 'water_restrict_flag']

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
        white_kw_list = [
            '管人|(哪个|什么)v|bv|联动|歌回|杂谈|歌力|企划|切片|前世|毕业|sc|弹幕|同接|二次元|原批|牧场|周边|史书|饭圈|滑坡',
            '(a|b|睿|皇协|批|p)站|b博|海鲜|(v|a)(吧|8)|nga|404|ytb|论坛|字幕组|粉丝群|直播间|魂组|录播',
            'asoul|皮套|纸片人|套皮|嘉然|然然|向晚|晚晚|乃琳|奶琳|贝拉|拉姐|珈乐|羊驼|a(骚|s|手)|向晚|歌姬|乃贝|晚饭|大头',
            '开播|共振|取关|牧场|啊啊啊|麻麻|别急|可爱|sad|感叹|速速|我超|存牌|狠狠|切割|牛牛|一把子|幽默|GNK48|汴京|抱团|别融',
            '嘉心糖|顶碗人|贝极星|奶淇淋|n70|皇(珈|家)|黄嘉琪|泥哥|(a|b|豆|d|抖|快|8|吧)(u|友)|一个魂|粉丝|ylg|mmr|低能|易拉罐|脑弹|铝制品|纯良',
        ]
        self.white_kw_exp = re.compile('|'.join(white_kw_list), re.I)
        self.water_restrict_flag = False

    async def __aenter__(self) -> "CloudReview":
        return await self.enter()

    async def run(self) -> None:

        while 1:
            try:
                start_time = time.perf_counter()

                # 获取限水标记
                self.water_restrict_flag = await self.is_tid_hide(0)

                # 获取主题帖列表
                threads = await self.get_threads(self.tieba_name)
                # 创建异步任务列表 并规定每个任务的延迟时间 避免高并发下的网络阻塞
                coros = [self._handle_thread(thread, idx / 10) for idx, thread in enumerate(threads)]
                # 并发运行协程
                del_flags = await asyncio.gather(*coros)

                def _yield_user_id():
                    for idx, thread in enumerate(threads):
                        if not del_flags[idx] and (user_id := thread.author_id) != 0 and thread.reply_num < 15:
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
                    coros = [
                        self.hide_thread(self.tieba_name, thread.tid)
                        for thread in threads
                        if thread.author_id in water_user_ids
                    ]
                    await asyncio.gather(*coros)

                tb.log.debug(f"Cycle time_cost: {time.perf_counter()-start_time:.4f}")
                # 主动释放CPU 转而运行其他协程
                await asyncio.sleep(30)

            except Exception:
                tb.log.critical("Unexcepted error", exc_info=True)
                return

    async def _handle_thread(self, thread: tb.Thread, delay: float) -> bool:
        """
        处理thread

        Returns:
            del_flag: bool True则帖已删除 False则无操作
        """

        if thread.is_livepost:
            # 置顶话题直接返回
            return False

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
            return True
        elif punish.del_flag == 2:
            # 屏蔽帖
            tb.log.info(
                f"Try to hide thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}. line:{punish.line}"
            )
            await self.hide_thread(self.tieba_name, thread.tid)
            return True

        return False

    async def _check_thread(self, thread: tb.Thread) -> Punish:
        """
        检查主题帖内容

        Returns:
            Punish
        """

        if self.water_restrict_flag:
            # 当前吧处于高峰期限水状态
            if await self.is_tid_hide(thread.tid) is False:
                await self.add_tid(thread.tid, True)
                return self.Punish(2)

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
            for img_content in post.contents.imgs:
                img = await self.get_image(img_content.src)
                if img is None:
                    continue
                permission = await self.get_imghash(img)
                if permission <= -5:
                    return self.Punish(1, 10)
                elif permission == -2:
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

    async def _check_text(self, obj: tb.Thread | tb.Post | tb.Comment) -> Punish:
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

        text = obj.text
        if re.search(
            "((?<![a-z])(v|t)|瞳|梓|罐|豆|鸟|鲨)(÷|/|／|➗|畜|处|除|楚|初|醋|cg)|痛(楚|初|醋)|椰子汁|🥥|东雪莲|莲宝|林忆宁|杨沐|赵若", text, re.I
        ):
            return self.Punish(1)

        level = obj.user.level
        if level > 6:
            # 用户等级大于6则跳过后续检查
            return self.Punish()

        # 内容中是否有白名单关键字
        has_white_kw = True if self.white_kw_exp.search(text) else False
        if has_white_kw:
            return self.Punish()

        # 内容中是否有罕见的联系方式
        has_rare_contact = True if self.expressions.contact_rare_exp.search(text) else False

        if level < 7:
            if self.expressions.job_nocheck_exp.search(text):
                # 招兼职 十天删帖
                return self.Punish(1, 10)

            if self.expressions.business_exp.search(text):
                # 商业推广 十天删帖
                return self.Punish(1)

            has_job = True if self.expressions.job_exp.search(text) else False
            if self.expressions.job_check_exp.search(text) and (has_job or has_rare_contact):
                # 易误判的兼职关键词 二重检验
                return self.Punish(1)

        return self.Punish()


if __name__ == '__main__':

    async def main():
        async with CloudReview('starry', 'asoul') as review:
            await review.run()

    try:
        asyncio.run(main())
    except BaseException:
        pass
