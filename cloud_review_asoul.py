# -*- coding:utf-8 -*-
import os
import sys
import time
import datetime as dt
import argparse

import re
import tiebaBrowser

import atexit


@atexit.register
def exit_hanle():
    review.close()


class CloudReview(tiebaBrowser.CloudReview):

    __slots__ = ('white_kw_exp')

    def __init__(self, BDUSS_key, tieba_name, sleep_time):
        super().__init__(BDUSS_key, tieba_name, sleep_time)

        white_kw_list = ['vup|管人|(哪个|什么)v',
                         '(a|b|睿|皇协|批|p)站|b博|海鲜|(v|a)(吧|8)|nga|404|ytb|论坛|字幕组|粉丝群|直播间',
                         '4v|樱花妹|中之人|国v|个人势|holo|虹|🌈|2434|杏|vr|木口|猴楼|皮套|纸片人|套皮|主播|小红|团长|嘉然|然然|向晚|晚晚|乃琳|奶琳|贝拉|拉姐|珈乐|p\+|p家|帕里|爬犁|a(骚|s)|向晚|梓|(海|孩)子姐|七海|爱丽丝',
                         '联动|歌回|杂谈|歌力|企划|前世|sc|弹幕|二次元|开播|取关|bv',
                         '谜语|拉胯|虚无|成分|黑屁|黑料|破防|真可怜|开团|(好|烂)活|干碎|对线|整活|乐了|乐子|橄榄|罢了|可爱|钓鱼|梁木|节奏|冲锋|yygq|芜狐|别尬|阴间|泪目|图一乐|差不多得了',
                         '懂哥|孝子|懂哥|mmr|gachi|anti|粉丝|太监|天狗|crew|杏奴|贵物|沙口|小鬼|后浪|人(↑|上)人|仌|鼠人|幻官|宦官|幻士|(a|\+|嘉|加)(畜|÷|/|友)|嘉心糖|顶碗人|贝极星|奶淇淋|皇珈|泥哥|小兔子']
        self.white_kw_exp = re.compile('|'.join(white_kw_list), re.I)

    def close(self):
        super().close()

    def run(self):
        while True:
            try:
                threads = self.get_threads(self.tieba_name)
                for thread in threads:
                    if self._check_thread(thread):
                        tiebaBrowser.log.info(f"Try to delete thread {thread.text} post by {thread.user.logname}")
                        self.del_thread(self.tieba_name, thread.tid)

                if self.sleep_time:
                    time.sleep(self.sleep_time)
            except Exception as err:
                tiebaBrowser.log.error(f"Unexcepted error:{err}")

    def _check_thread(self, thread: tiebaBrowser.Thread):
        """
        检查thread内容
        """

        posts = self.get_posts(thread.tid, 9999)
        if posts and posts[0].floor == 1:
            thread.user.level = posts[0].user.level
            flag = self._check_text(thread)
            if flag == -1:
                pass
            elif flag == 1:
                return True
            elif flag == 0:
                pass
            else:
                tiebaBrowser.log.error(f'Wrong flag {flag} in _check_thread!')
                pass

        for post in posts:
            flag = self._check_post(post)
            if flag == 0:
                pass
            elif flag == 1:
                if post.floor == 1:
                    return True
                else:
                    tiebaBrowser.log.info(f"Try to delete post {post.text} post by {post.user.logname}")
                    self.del_post(self.tieba_name, post.tid, post.pid)
            elif flag == 2:
                return True
            else:
                tiebaBrowser.log.error('Wrong flag {flag} in _check_thread!'.format(flag=flag))

        return False

    def _check_post(self, post: tiebaBrowser.Post):
        """
        检查回复内容
        """

        flag = self._check_text(post)
        if flag == -1:
            return 0
        elif flag == 1:
            return 1
        elif flag == 0:
            if post.is_thread_owner and post.user.level < 6 and self.exp.kill_thread_exp.search(post.text):
                return 2
            if post.imgs:
                if len(post.imgs) == 1 and post.imgs[0].endswith('.gif'):
                    return 1
                if post.user.level < 3 and not self.white_kw_exp.search(post.text):
                    for img in post.imgs:
                        url = self._scan_QRcode(img)
                        if url and url.startswith('http'):
                            return 1
        else:
            tiebaBrowser.log.error(f'Wrong flag {flag} in _check_post!')

        self.mysql.add_pid(self.tieba_name, post.pid)
        return 0

    def _check_text(self, obj, level=None):

        if self.mysql.has_pid(self.tieba_name, obj.pid):
            return -1

        is_white = self.mysql.iswhite_portrait(self.tieba_name, obj.user.portrait)
        if is_white is True:
            return -1
        elif is_white is False:
            self.block(obj.user, self.tieba_name, day=10)
            return 1
        else:
            pass

        level = obj.user.level
        if level > 2:
            return -1
        text = obj.text

        has_rare_contact = True if self.exp.contact_rare_exp.search(text) else False
        has_contact = True if (has_rare_contact or self.exp.contact_exp.search(text)) else False
        has_white_kw = True if self.white_kw_exp.search(text) else False

        if has_white_kw:
            return 0

        if level < 3:
            if self.exp.job_nocheck_exp.search(text):
                self.block(obj.user, self.tieba_name, day=10)
                return 1
            if self.exp.app_nocheck_exp.search(text):
                self.block(obj.user, self.tieba_name, day=10)
                return 1
            if self.exp.game_nocheck_exp.search(text):
                self.block(obj.user, self.tieba_name, day=10)
                return 1

            if self.exp.maipian_exp.search(text):
                if has_contact or level < 3:
                    return 1
            if obj.user.gender == 2:
                if self.exp.female_check_exp.search(text):
                    if level == 1:
                        return 1
                    elif not has_white_kw:
                        return 1
                if obj.has_audio:
                    return 1

            if self.exp.business_exp.search(text):
                return 1

            has_job = True if self.exp.job_exp.search(text) else False
            if has_job and level == 1:
                return 1
            if self.exp.job_check_exp.search(text) and (has_job or has_contact):
                return 1
            if self.exp.app_exp.search(text) and (self.exp.app_check_exp.search(text) or has_contact):
                return 1
            if self.exp.course_exp.search(text) and self.exp.course_check_exp.search(text):
                return 1
            if self.exp.game_exp.search(text) and self.exp.game_check_exp.search(text):
                return 1
            if self.exp.hospital_exp.search(text):
                return 1

        if level == 1:
            if obj.user.user_name:
                if self.exp.name_nocheck_exp.search(obj.user.user_name):
                    self.block(obj.user, self.tieba_name, day=10)
                    return 1
                if self.exp.name_exp.search(obj.user.user_name):
                    if self.exp.name_check_exp.search(obj.user.user_name) or has_contact:
                        return 1
            if obj.user.nick_name:
                if self.exp.name_nocheck_exp.search(obj.user.nick_name):
                    return 1
                if self.exp.name_exp.search(obj.user.nick_name):
                    if self.exp.name_check_exp.search(obj.user.nick_name) or has_contact:
                        return 1
            if self.exp.lv1_exp.search(text):
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
                        default='asoul',
                        help='贴吧名')
    parser.add_argument('--sleep_time', '-st',
                        type=float,
                        default=0,
                        help='每两次云审查的间隔时间')

    review = CloudReview(**vars(parser.parse_args()))
    review.run()
