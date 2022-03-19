# -*- coding:utf-8 -*-
import argparse
import atexit
import re
import sys
import time
import traceback

import tiebaBrowser as tb
import tiebaBrowser.cloud_review as cr


@atexit.register
def exit_hanle():
    review.close()


class CloudReview(cr.CloudReview):

    __slots__ = ['white_kw_exp']

    def __init__(self, BDUSS_key, tieba_name, sleep_time):
        super().__init__(BDUSS_key, tieba_name, sleep_time)
        self.white_kw_exp = re.compile(
            '爬|爪巴|滚|gck|boss|武器|(是|绝对|肯定).?破解|闪退', re.I)

    def close(self):
        super().close()

    def run(self):

        while 1:
            try:
                for thread in self.get_threads(self.tieba_name):
                    # 按回复时间排序获取帖子并逐个检查
                    if self._check_thread(thread):
                        tb.log.info(
                            f"Try to delete thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}")
                        self.del_thread(self.tieba_name, thread.tid)

                tb.log.debug('heartbeat')
                if self.sleep_time:
                    time.sleep(self.sleep_time)

            except KeyboardInterrupt:
                break

            except Exception:
                tb.log.error(
                    f"Unexcepted error:{traceback.format_exc()}")

    def _check_thread(self, thread: tb.Thread):
        """
        检查thread内容
        """

        posts = self.get_posts(thread.tid, 9999)
        if len(posts) == 0:
            return False

        if posts[0].floor == 1:
            # 确定楼主等级
            thread.user.level = posts[0].user.level
            if not thread.text and thread.user.level < 4 and len(thread.imgs) == 1 and re.search('本(吧|帖|贴)|手游|暗号|111|222', thread.title):
                # 手游推广，十天并删帖
                self.block(self.tieba_name, thread.user, day=10,
                           reason=f"line:{sys._getframe().f_lineno}")
                return True

            flag = self._check_text(thread)
            if flag == -1:
                # 白名单直接返回
                pass
            elif flag == 1:
                # 内容违规，删帖
                return True
            elif flag == 0:
                if thread.user.priv_reply == 6:
                    # 如果锁回复，直接删帖
                    return True

        for post in posts:
            flag = self._check_post(post)
            if flag == 0:
                # 内容无问题
                pass
            elif flag == 1:
                # 内容违规，删回复
                tb.log.info(
                    f"Try to delete post {post.text} post by {post.user.log_name}. level:{post.user.level}")
                self.del_post(self.tieba_name, post.tid, post.pid)
            elif flag == 2:
                # 出现淘特引流等关键词，删主楼
                return True

        return False

    def _check_post(self, post: tb.Post):
        """
        检查回复内容
        """

        flag = self._check_text(post)
        if flag == -1:
            # 白名单用户
            return 0
        elif flag == 1:
            # 内容违规，删回复
            return 1
        elif flag == 0:
            # 需要进一步检查
            if post.is_thread_owner and self.expressions.kill_thread_exp.search(post.text):
                # 出现淘特引流等关键词，封十天并删主楼
                self.block(self.tieba_name, post.user, day=10,
                           reason=f"line:{sys._getframe().f_lineno}")
                return 2

            for img_content in post.contents.imgs:
                # 检查回复中的图
                img = self.url2image(img_content.cdn_src)
                if img is None:
                    continue
                if self.has_imghash(img):
                    # 图片的phash在黑名单中，删回复
                    return 1
                if post.user.level < 6:
                    url = self.scan_QRcode(img)
                    if url.startswith('http'):
                        # 图片带网址二维码且用户等级小于6，删回复
                        return 1
        else:
            tb.log.error(f'Wrong flag {flag} in _check_post!')

        self.mysql.add_pid(self.tieba_name, post.pid)
        return 0

    def _check_text(self, obj):

        if self.mysql.has_pid(self.tieba_name, obj.pid):
            # 回复已被检查过且无问题，跳过检查
            return -1

        is_white = self.mysql.is_user_id_white(
            self.tieba_name, obj.user.user_id)
        if is_white == True:
            # 白名单用户
            return -1
        elif is_white == False:
            # 黑名单用户，删回复并封十天
            self.block(self.tieba_name, obj.user, day=10,
                       reason=f"line:{sys._getframe().f_lineno}")
            return 1

        level = obj.user.level
        if level > 4:
            # 用户等级大于4则跳过后续检查
            return 0

        text = obj.text

        # 内容中是否有罕见的联系方式
        has_rare_contact = True if self.expressions.contact_rare_exp.search(
            text) else False
        if has_rare_contact:
            return 1
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
                    self.block(self.tieba_name, obj.user, day=10,
                               reason=f"line:{sys._getframe().f_lineno}")
                    return 1
                if level < 3:
                    # 等级过低则直接十天删帖
                    self.block(self.tieba_name, obj.user, day=10,
                               reason=f"line:{sys._getframe().f_lineno}")
                    return 1
            # 容易造成误判的破解版关键词
            pojie_exp = re.compile(
                '存档|破解|(全|多|各种)(人物|皮肤|角色|英雄|材料|水晶|蓝币|资源)|可联机|内购', re.I)
            if len(pojie_exp.findall(text)) > 2:
                # 包含多于两个关键词
                if level < 3 and not has_white_kw:
                    # 等级太低且没有白名单关键词直接删
                    return 1
                if has_contact:
                    # 有联系方式直接删
                    return 1

        if level < 5:
            if self.expressions.job_nocheck_exp.search(text):
                # 招兼职，十天删帖
                self.block(self.tieba_name, obj.user, day=10,
                           reason=f"line:{sys._getframe().f_lineno}")
                return 1
            if self.expressions.app_nocheck_exp.search(text):
                # app推广，十天删帖
                self.block(self.tieba_name, obj.user, day=10,
                           reason=f"line:{sys._getframe().f_lineno}")
                return 1
            if self.expressions.game_nocheck_exp.search(text):
                # 游戏推广，十天删帖
                self.block(self.tieba_name, obj.user, day=10,
                           reason=f"line:{sys._getframe().f_lineno}")
                return 1

        if level < 4:
            if not has_white_kw and self.expressions.maipian_exp.search(text):
                # 麦片相关
                if has_contact or level < 3:
                    # 有联系方式且等级小于3
                    self.block(self.tieba_name, obj.user, day=10,
                               reason=f"line:{sys._getframe().f_lineno}")
                    return 1
            if obj.user.gender == 2:
                # 性别为女，判断是否钓鱼
                if self.expressions.female_check_exp.search(text):
                    if level == 1:
                        return 1

        if level < 3:
            if self.expressions.business_exp.search(text):
                # 商业推广，删帖
                return 1
            if not has_white_kw:
                # 是否包含易误判的兼职关键词
                has_job = True if self.expressions.job_exp.search(
                    text) else False
                if has_job and level == 1:
                    # 是，且为一级小号，删帖
                    return 1
                if self.expressions.job_check_exp.search(text) and (has_job or has_contact):
                    # 复验
                    return 1
                if self.expressions.app_exp.search(text) and (self.expressions.app_check_exp.search(text) or has_contact):
                    # 易误判的app推广关键词，复验
                    return 1
                if self.expressions.course_exp.search(text) and self.expressions.course_check_exp.search(text):
                    # 易误判的课程推广关键词，复验
                    return 1
                if self.expressions.game_exp.search(text) and self.expressions.game_check_exp.search(text):
                    # 易误判的游戏推广关键词，复验
                    return 1
                if self.expressions.hospital_exp.search(text):
                    # 易误判的医疗推广关键词
                    return 1

        if level == 1:
            if obj.user.user_name:
                if self.expressions.name_nocheck_exp.search(obj.user.user_name):
                    # 用户名包含推广关键词
                    return 1
                if not has_white_kw and self.expressions.name_exp.search(obj.user.user_name):
                    if self.expressions.name_check_exp.search(obj.user.user_name) or has_contact:
                        # 用户名包含易误判的推广关键词，复验
                        return 1
            if obj.user.nick_name:
                if self.expressions.name_nocheck_exp.search(obj.user.nick_name):
                    return 1
                if not has_white_kw and self.expressions.name_exp.search(obj.user.nick_name):
                    if self.expressions.name_check_exp.search(obj.user.nick_name) or has_contact:
                        return 1
            if self.expressions.lv1_exp.search(text):
                # 检查一级号敏感关键词
                return 1

        return 0


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='贴吧云审查', allow_abbrev=False)
    parser.add_argument('--BDUSS_key', '-k',
                        type=str,
                        default='default',
                        help='用于获取BDUSS')

    parser.add_argument('--tieba_name', '-b',
                        type=str,
                        default='元气骑士',
                        help='贴吧名')
    parser.add_argument('--sleep_time', '-st',
                        type=float,
                        default=0,
                        help='每两次云审查的间隔时间')

    review = CloudReview(**vars(parser.parse_args()))
    review.run()
