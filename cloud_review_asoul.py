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

        white_kw_list = ['vup|管人|(哪个|什么)v',
                         '(a|b|睿|皇协|批|p)站|b博|海鲜|(v|a)(吧|8)|nga|404|ytb|论坛|字幕组|粉丝群|直播间',
                         '4v|樱花妹|中之人|国v|个人势|holo|asoul|2434|vr|木口|猴楼|皮套|纸片人|套皮|嘉然|然然|向晚|晚晚|乃琳|奶琳|贝拉|拉姐|珈乐|羊驼|p\+|p家|a(骚|s|手)|向晚|梓|(海|孩)子姐|七海|爱丽丝',
                         '联动|歌回|杂谈|歌力|企划|前世|sc|弹幕|二次元|开播|取关|bv',
                         '谜语|拉胯|虚无|成分|黑屁|黑料|破防|真可怜|开团|(好|烂)活|干碎|对线|整活|乐了|乐子|橄榄|罢了|钓鱼|梁木|节奏|冲锋|yygq|阴间|泪目|图一乐|晚安',
                         '懂哥|孝子|mmr|粉丝|天狗|crew|杏奴|幻官|宦官|幻士|嘉心糖|顶碗人|贝极星|奶淇淋|n70|皇(珈|家)|泥哥|小兔子|(a|b)u|一个魂']
        self.white_kw_exp = re.compile('|'.join(white_kw_list), re.I)

    def close(self):
        super().close()

    def run(self):
        while True:
            try:
                _threads = self.get_threads(self.tieba_name)
                users = {}
                for thread in _threads:
                    if self._check_thread(thread):
                        tb.log.info(
                            f"Try to delete thread {thread.text} post by {thread.user.log_name}. level:{thread.user.level}")
                        self.del_thread(self.tieba_name, thread.tid)
                        continue
                    if thread.like < 30 and thread.reply_num < 20:
                        user_threads = users.get(thread.user.user_id, [])
                        user_threads.append(thread)
                        users[thread.user.user_id] = user_threads
                for user_id, _threads in users.items():
                    if user_id and len(_threads) >= 5 and not self.mysql.is_user_id_white(self.tieba_name, user_id):
                        tb.log.info(
                            f"Clear Water {user_id}")
                        #self.block(self.tieba_name, _threads[0].user, 1, reason=f"line:{sys._getframe().f_lineno}")
                        for thread in _threads:
                            self.del_thread(self.tieba_name,
                                            thread.tid, is_frs_mask=True)
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

        posts = self.get_posts(thread.tid)
        if len(posts) == 0:
            return False

        thread.user.level = posts[0].user.level
        flag = self._check_text(thread)
        if flag == -1:
            pass
        elif flag == 1:
            return True
        elif flag == 0:
            if thread.user.priv_reply == 6:
                return True
        else:
            tb.log.error(f'Wrong flag {flag} in _check_thread!')
            pass

        if len(posts) > 1:
            second_floor = posts[1]
            if second_floor.reply_num > 0:
                for comment in self.get_comments(second_floor.tid, second_floor.pid):
                    if comment.user.level < 6 and re.search('免費|[𝟙-𝟡]|仓井空在等尼', comment.text):
                        self.block(self.tieba_name, comment.user, 10)
                        self.del_post(self.tieba_name,
                                      comment.tid, comment.pid)

        if posts.total_pn > 1:
            posts = self.get_posts(thread.tid, 9999)

        for post in posts:
            flag = self._check_post(post)
            if flag == 0:
                pass
            elif flag == 1:
                tb.log.info(
                    f"Try to delete post {post.text} post by {post.user.log_name}. level:{post.user.level}")
                self.del_post(self.tieba_name, post.tid, post.pid)
            elif flag == 2:
                return True
            else:
                tb.log.error(f'Wrong flag {flag} in _check_thread!')

        return False

    def _check_post(self, post: tb.Post):
        """
        检查回复内容
        """

        flag = self._check_text(post)
        if flag == -1:
            return 0
        elif flag == 1:
            return 1
        elif flag == 0:
            if post.is_thread_owner and self.expressions.kill_thread_exp.search(post.text):
                return 2
            for img_url in post.imgs:
                img = self.url2image(img_url)
                if img is None:
                    continue
                if self.has_imghash(img):
                    return 1
                if post.user.level < 6:
                    url = self.scan_QRcode(img)
                    if url.startswith('http'):
                        return 1
        else:
            tb.log.error(f'Wrong flag {flag} in _check_post!')

        self.mysql.add_pid(self.tieba_name, post.pid)
        return 0

    def _check_text(self, obj):

        if self.mysql.has_pid(self.tieba_name, obj.pid):
            return -1

        is_white = self.mysql.is_user_id_white(
            self.tieba_name, obj.user.user_id)
        if is_white == True:
            return -1
        elif is_white == False:
            self.block(self.tieba_name, obj.user, day=10,
                       reason=f"line:{sys._getframe().f_lineno}")
            return 1

        text = obj.text
        if re.search("李奕|读物配音|有声书", text, re.I) is not None:
            self.block(self.tieba_name, obj.user, day=10,
                       reason=f"line:{sys._getframe().f_lineno}")
            return 1
        if re.search("((?<![a-z])v|瞳|梓|罐|豆|鸟|鲨)(÷|/|／|➗|畜|处|除|初|醋)|椰子汁|🥥|东雪莲|莲宝", text, re.I) is not None:
            return 1

        level = obj.user.level
        if level > 6:
            return 0
        if obj.user.is_vip or obj.user.is_god:
            return -1

        has_white_kw = True if self.white_kw_exp.search(text) else False
        if has_white_kw:
            return 0

        has_rare_contact = True if self.expressions.contact_rare_exp.search(
            text) else False
        has_contact = True if (
            has_rare_contact or self.expressions.contact_exp.search(text)) else False

        if level < 7:
            if self.expressions.job_nocheck_exp.search(text):
                self.block(self.tieba_name, obj.user, day=10,
                           reason=f"line:{sys._getframe().f_lineno}")
                return 1

            if self.expressions.business_exp.search(text):
                return 1

            has_job = True if self.expressions.job_exp.search(text) else False
            if self.expressions.job_check_exp.search(text) and (has_job or has_contact):
                return 1
            if self.expressions.course_exp.search(text) and self.expressions.course_check_exp.search(text):
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
