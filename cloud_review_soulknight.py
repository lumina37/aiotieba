# -*- coding:utf-8 -*-
import asyncio
import re
import sys
import traceback

import tiebaBrowser as tb


class SoulknightCloudReview(tb.CloudReview):

    __slots__ = ['white_kw_exp']

    def __init__(self, BDUSS_key, tieba_name):
        super().__init__(BDUSS_key, tieba_name)
        self.white_kw_exp = re.compile(
            'boss|武器|(是|绝对|肯定).?破解|闪退', re.I)

    async def run(self):

        while 1:
            try:
                # 获取主题帖列表
                threads = await self.get_threads(self.tieba_name)
                # 创建异步任务列表，用idx/10规定每个任务的延迟时间，避免高并发下的网络阻塞
                tasks = [asyncio.create_task(self._handle_thread(
                    thread, idx/3)) for idx, thread in enumerate(threads)]
                # 执行任务
                await asyncio.gather(*tasks)

                tb.log.debug('heartbeat')
                # 主动释放CPU，转而运行其他协程
                await asyncio.sleep(20)

            except Exception:
                tb.log.critical(
                    f"Unexcepted error:{traceback.format_exc()}")
                return

    async def _handle_thread(self, thread: tb.Thread, delay: float):
        """
        处理thread
        """

        await asyncio.sleep(delay)

        del_flag, day, line = await self._check_thread(thread)
        if day:
            await self.block(self.tieba_name, thread.user, day=day, reason=f"line:{line}")
        if del_flag:
            tb.log.info(
                f"Try to delete thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}")
            await self.del_thread(self.tieba_name, thread.tid)

    async def _check_thread(self, thread: tb.Thread):
        """
        检查主题帖内容

        返回值:
            del_flag: int 0则不操作，1则删主题帖
            day: int 封号天数
            line: int 处罚规则所在的行号
        """

        posts = await self.get_posts(thread.tid, 9999)
        if len(posts) == 0:
            return 0, 0, 0

        if posts[0].floor == 1:
            # 确定楼主等级
            thread.user.level = posts[0].user.level
            if not thread.text and thread.user.level < 4 and len(thread.imgs) == 1 and re.search('本(吧|帖|贴)|手游|暗号|111|222', thread.title):
                # 手游推广，十天并删帖
                return 1, 10, sys._getframe().f_lineno

            del_flag, day, line = await self._check_text(thread)
            if del_flag == -1:
                # 白名单不操作
                pass
            elif del_flag == 1:
                # 内容违规，删帖
                return 1, day, line
            elif del_flag == 0:
                if thread.user.priv_reply == 6:
                    # 如果锁回复，直接删帖
                    return 1, 0, 0

        for post in posts:
            del_flag, day, line = await self._check_post(post)
            if day:
                await self.block(self.tieba_name, post.user, day=day, reason=f"line:{line}")
            if del_flag == -1:
                # 白名单，跳过后续检查
                continue
            elif del_flag == 0:
                # 普通
                pass
            elif del_flag == 1:
                # 内容违规，删回复
                tb.log.info(
                    f"Try to delete post {post.text} post by {post.user.log_name}. level:{post.user.level}")
                await self.del_post(self.tieba_name, post.tid, post.pid)
            elif del_flag == 2:
                # 出现淘特引流等关键词，删主楼
                return 1, 0, 0

        return 0, 0, 0

    async def _check_post(self, post: tb.Post):
        """
        检查回复内容

        返回值:
            del_flag: int -1为白名单，0为普通，1为删回复，2为删主题帖
            day: int 封号天数
            line: int 处罚规则所在的行号
        """

        del_flag, day, line = await self._check_text(post)
        if del_flag == -1:
            # 白名单用户
            return -1, 0, 0
        elif del_flag == 1:
            # 内容违规，删回复
            return 1, day, line
        elif del_flag == 0:
            # 需要进一步检查
            if post.is_thread_owner and self.expressions.kill_thread_exp.search(post.text):
                # 出现淘特引流等关键词，封十天并删主楼
                return 2, 10, sys._getframe().f_lineno

            for img_content in post.contents.imgs:
                # 检查回复中的图
                img = await self.url2image(img_content.cdn_src)
                if img is None:
                    continue
                if await self.has_imghash(img):
                    # 图片的phash在黑名单中，删回复
                    return 1, 0, 0
                if post.user.level < 6:
                    url = self.scan_QRcode(img)
                    if url.startswith('http'):
                        # 图片带网址二维码且用户等级小于6，删回复
                        return 1, 0, 0

        await self.mysql.add_pid(self.tieba_name, post.pid)
        return 0, 0, 0

    async def _check_text(self, obj):
        """
        检查文本内容

        返回值:
            del_flag: int -1为白名单，0为普通，1为删帖
            day: int 封号天数
            line: int 处罚规则所在的行号
        """

        if await self.mysql.has_pid(self.tieba_name, obj.pid):
            # 回复已被检查过且无问题，跳过检查
            return -1, 0, 0

        is_white = await self.mysql.is_user_id_white(self.tieba_name, obj.user.user_id)
        if is_white == True:
            # 白名单用户
            return -1, 0, 0
        elif is_white == False:
            # 黑名单用户，删回复并封十天
            return 1, 10, sys._getframe().f_lineno

        level = obj.user.level
        if level > 4:
            # 用户等级大于4则跳过后续检查
            return 0, 0, 0

        text = obj.text

        # 内容中是否有罕见的联系方式
        has_rare_contact = True if self.expressions.contact_rare_exp.search(
            text) else False
        if has_rare_contact:
            return 1, 0, 0
        # 内容中是否有联系方式
        has_contact = True if (
            has_rare_contact or self.expressions.contact_exp.search(text)) else False
        has_white_kw = True if self.white_kw_exp.search(text) else False

        if level < 6:
            # 破解版关键词
            game_exp = re.compile(
                '破解版|(ios|苹果).{0,3}(存档|白嫖|福利)|(卖|分享|求).{0,4}存档|全解锁.*分享|内购免费|福利群|变态版', re.I)
            if game_exp.search(text):
                if has_contact and not has_white_kw:
                    # 兜售破解，十天删帖
                    return 1, 10, sys._getframe().f_lineno
                if level < 3:
                    # 等级过低则直接十天删帖
                    return 1, 10, sys._getframe().f_lineno
            # 容易造成误判的破解版关键词
            pojie_exp = re.compile(
                '存档|破解|(全|多|各种)(人物|皮肤|角色|英雄|材料|水晶|蓝币|资源)|可联机|内购', re.I)
            if len(pojie_exp.findall(text)) > 2:
                # 包含多于两个关键词
                if level < 3 and not has_white_kw:
                    # 等级太低且没有白名单关键词直接删
                    return 1, 0, 0
                if has_contact:
                    # 有联系方式直接删
                    return 1, 0, 0

        if level < 5:
            if self.expressions.job_nocheck_exp.search(text):
                # 招兼职，十天删帖
                return 1, 10, sys._getframe().f_lineno
            if self.expressions.app_nocheck_exp.search(text):
                # app推广，十天删帖
                return 1, 10, sys._getframe().f_lineno
            if self.expressions.game_nocheck_exp.search(text):
                # 游戏推广，十天删帖
                return 1, 10, sys._getframe().f_lineno

        if level < 4:
            if not has_white_kw and self.expressions.maipian_exp.search(text):
                # 麦片相关
                if has_contact or level < 3:
                    # 有联系方式且等级小于3，十天删帖
                    return 1, 10, sys._getframe().f_lineno
            if obj.user.gender == 2:
                # 性别为女，判断是否钓鱼
                if self.expressions.female_check_exp.search(text):
                    if level == 1:
                        return 1, 0, 0

        if level < 3:
            if self.expressions.business_exp.search(text):
                # 商业推广，删帖
                return 1, 0, 0
            if not has_white_kw:
                # 是否包含易误判的兼职关键词
                has_job = True if self.expressions.job_exp.search(
                    text) else False
                if has_job and level == 1:
                    # 是，且为一级小号，删帖
                    return 1, 0, 0
                if self.expressions.job_check_exp.search(text) and (has_job or has_contact):
                    # 复验
                    return 1, 0, 0
                if self.expressions.app_exp.search(text) and (self.expressions.app_check_exp.search(text) or has_contact):
                    # 易误判的app推广关键词，复验
                    return 1, 0, 0
                if self.expressions.course_exp.search(text) and self.expressions.course_check_exp.search(text):
                    # 易误判的课程推广关键词，复验
                    return 1, 0, 0
                if self.expressions.game_exp.search(text) and self.expressions.game_check_exp.search(text):
                    # 易误判的游戏推广关键词，复验
                    return 1, 0, 0
                if self.expressions.hospital_exp.search(text):
                    # 易误判的医疗推广关键词
                    return 1, 0, 0

        if level == 1:
            if obj.user.user_name:
                if self.expressions.name_nocheck_exp.search(obj.user.user_name):
                    # 用户名包含推广关键词
                    return 1, 0, 0
                if not has_white_kw and self.expressions.name_exp.search(obj.user.user_name):
                    if self.expressions.name_check_exp.search(obj.user.user_name) or has_contact:
                        # 用户名包含易误判的推广关键词，复验
                        return 1, 0, 0
            if obj.user.nick_name:
                if self.expressions.name_nocheck_exp.search(obj.user.nick_name):
                    return 1, 0, 0
                if not has_white_kw and self.expressions.name_exp.search(obj.user.nick_name):
                    if self.expressions.name_check_exp.search(obj.user.nick_name) or has_contact:
                        return 1, 0, 0
            if self.expressions.lv1_exp.search(text):
                # 检查一级号敏感关键词
                return 1, 0, 0

        return 0, 0, 0


if __name__ == '__main__':

    async def main():
        async with SoulknightCloudReview('default', '元气骑士') as review:
            await review.run()

    try:
        asyncio.run(main())
    except:
        pass
