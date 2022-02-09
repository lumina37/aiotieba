# -*- coding:utf-8 -*-
import argparse
import atexit
import re
import time
import traceback

import tiebaBrowser as tb
import tiebaBrowser.cloud_review as cr
from tiebaBrowser.data_structure import BasicUserInfo, UserInfo


@atexit.register
def exit_hanle():
    listener.close()


class TimeRange(object):
    """
    时间范围记录
    TimeRange(shiftpair)

    参数:
        shiftpair: tuple (下界偏移,上界偏移) 用于指示时间范围
    """

    __slots__ = ['shiftpair', 'lower', 'upper']

    def __init__(self, shiftpair):
        if shiftpair[0] >= shiftpair[1]:
            raise ValueError("Invalid shiftpair")

        self.shiftpair = shiftpair
        self.set()

    def set(self):
        """
        用当前时间更新时间范围
        """

        current_time = time.time()
        self.lower = current_time + self.shiftpair[0]
        self.upper = current_time + self.shiftpair[1]

    def is_inrange(self, check_time):
        return self.lower < check_time <= self.upper


class Listener(object):

    access_user = {'Noob_legend': 3,
                   'LIN_S_H': 3,
                   'kk不好玩': 3,
                   '闪打快手丿': 3,
                   '咿呀呼哈啾': 3,
                   '夢野敬二abc': 3,
                   '雷神幻影38535': 3,
                   '帅111哥': 3,
                   '追秒小宝开': 3,
                   '環奈是我的': 3,
                   '风待葬丶乱步': 3,
                   'FGU星耀': 3,
                   'WGD1314sunny': 3,
                   '某宅FZ': 3,
                   'MKal栗子': 3,
                   '瓶水相逢为吴邪': 3,
                   '物理1901': 3,
                   'unlog10x': 3,
                   '1084341337': 3,
                   'Aimersars': 3,
                   '梨木利亚': 3,
                   '魔法少年氢': 3,
                   }

    def __init__(self, admin_BDUSS_key, listener_BDUSS_key, tieba_name, listen_tid):
        self.listener = tb.Browser(listener_BDUSS_key)
        self.admin = cr.CloudReview(admin_BDUSS_key, tieba_name)

        self.tieba_name = tieba_name
        self.listen_tid = listen_tid

        self.time_range = TimeRange((-40, -10))

        self.func_map = {'recommend': self.cmd_recommend,
                         'drop': self.cmd_drop,
                         'delete': self.cmd_delete,
                         'unblock': self.cmd_unblock,
                         'block': self.cmd_block,
                         'recover': self.cmd_recover,
                         'hide': self.cmd_hide,
                         'unhide': self.cmd_unhide,
                         'tmphide': self.cmd_tmphide,
                         'tmpunhide': self.cmd_tmpunhide,
                         'blacklist_add': self.cmd_blacklist_add,
                         'blacklist_cancel': self.cmd_blacklist_cancel,
                         'mysql_white': self.cmd_mysql_white,
                         'mysql_black': self.cmd_mysql_black,
                         'mysql_reset': self.cmd_mysql_reset
                         }

    def close(self):
        self.listener.close()
        self.admin.close()

    def _prase_cmd(self, text):
        """
        解析指令
        """

        if not text.startswith('@'):
            return '', ''

        cmd = re.sub('^@.*? ', '', text).strip()
        cmds = cmd.split(' ', 1)

        if len(cmds) == 1:
            cmd_type = cmds[0]
            arg = ''
        elif len(cmds) == 2:
            cmd_type = cmds[0]
            arg = cmds[1]
        else:
            cmd_type = ''
            arg = ''

        return cmd_type, arg

    @staticmethod
    def get_id(url):
        """
        从指令链接中找出tid和pid
        """

        tid_raw = re.search('(/p/|tid=|thread_id=)(\d+)', url)
        tid = int(tid_raw.group(2)) if tid_raw else 0

        pid_raw = re.search('(pid|post_id)=(\d+)', url)
        pid = int(pid_raw.group(2)) if pid_raw else 0

        return tid, pid

    def scan(self):
        self.time_range.set()
        ats = self.listener.get_ats()

        need_post = False
        if ats:
            for end_index, at in enumerate(ats):
                if not self.time_range.is_inrange(at.create_time):
                    ats = ats[:end_index]
                    break
                if at.tid == self.listen_tid:
                    need_post = True

        if need_post:
            posts = self.listener.get_posts(self.listen_tid, 9999)
            post_map = {post.pid: post for post in posts if post.floor != 1}
        else:
            post_map = {}

        for at in ats:
            obj = post_map.get(at.pid, at)
            flag = self._handle_cmd(obj)
            if flag is True:
                self.admin.del_post(self.tieba_name, obj.tid, obj.pid)
            elif flag is False:
                self.listener.del_post(self.tieba_name, obj.tid, obj.pid)

    def _handle_cmd(self, obj):
        cmd_type, arg = self._prase_cmd(obj.text)
        func = self.func_map.get(cmd_type, self.cmd_default)
        return func(obj, arg)

    def cmd_recommend(self, at, arg):
        """
        recommend指令
        对指令所在主题帖执行“大吧主首页推荐”操作

        权限: 1
        限制: 监听帖禁用
        """

        if at.tid == self.listen_tid:
            return False
        if at.tieba_name != self.tieba_name:
            return None
        if self.access_user.get(at.user.user_name, 0) < 1:
            return None

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if self.admin.recommend(self.tieba_name, at.tid):
            return True
        else:
            return None

    def cmd_drop(self, at, arg):
        """
        drop指令
        删除指令所在主题帖并封禁楼主十天

        权限: 2
        限制: 监听帖禁用
        """

        if at.tid == self.listen_tid:
            return False
        if at.tieba_name != self.tieba_name:
            return None
        if self.access_user.get(at.user.user_name, 0) < 2:
            return None

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        posts = self.listener.get_posts(at.tid)
        if not posts:
            return None

        tb.log.info(
            f"Try to delete thread {posts[0].text} post by {posts[0].user.log_name}")

        self.admin.block(self.tieba_name, posts[0].user, day=10)
        self.admin.del_post(self.tieba_name, at.tid, at.pid)
        self.admin.del_thread(self.tieba_name, at.tid)

        return None

    def cmd_delete(self, at, arg):
        """
        delete指令
        删除指令所在主题帖

        权限: 2
        限制: 监听帖禁用
        """

        if at.tid == self.listen_tid:
            return False
        if at.tieba_name != self.tieba_name:
            return None
        if self.access_user.get(at.user.user_name, 0) < 2:
            return None

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        posts = self.listener.get_posts(at.tid)
        if not posts:
            return None

        tb.log.info(
            f"Try to delete thread {posts[0].text} post by {posts[0].user.log_name}")

        self.admin.del_post(self.tieba_name, at.tid, at.pid)
        self.admin.del_thread(self.tieba_name, at.tid)

        return None

    def cmd_indrop(self, at, arg):
        """
        indrop指令
        将指令所在主题帖加入tid_indroplist，该主题帖将在晚高峰期被临时删除

        权限: 2
        限制: 监听帖禁用
        """

        if at.tid == self.listen_tid:
            return False
        if at.tieba_name != self.tieba_name:
            return None
        if self.access_user.get(at.user.user_name, 0) < 2:
            return None

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        posts = self.listener.get_posts(at.tid)
        if not posts:
            return None

        self.admin.del_post(self.tieba_name, at.tid, at.pid)
        self.admin.mysql.set_tid(self.tieba_name, at.tid)

        return None

    def cmd_unblock(self, post, id):
        """
        unblock指令
        通过id解封用户

        权限: 2
        限制: 仅在监听帖可用
        """

        if post.tid != self.listen_tid:
            return None
        if self.access_user.get(post.user.user_name, 0) < 2:
            return False
        if not id:
            return False

        tb.log.info(f"{post.user.user_name}: {post.text}")

        user = self.listener.get_userinfo(UserInfo(id))

        return self.admin.unblock(self.tieba_name, user)

    def cmd_block(self, post, id):
        """
        block指令
        通过id封禁用户

        权限: 2
        限制: 仅在监听帖可用
        """

        if post.tid != self.listen_tid:
            return None
        if self.access_user.get(post.user.user_name, 0) < 2:
            return False
        if not id:
            return False

        tb.log.info(f"{post.user.user_name}: {post.text}")

        return self.admin.block(self.tieba_name, UserInfo(id), day=10)[0]

    def cmd_recover(self, post, url):
        """
        recover指令
        恢复链接所指向的帖子

        权限: 2
        限制: 仅在监听帖可用
        """

        if post.tid != self.listen_tid:
            return None
        if self.access_user.get(post.user.user_name, 0) < 2:
            return False
        if not url:
            return False

        tb.log.info(f"{post.user.user_name}: {post.text}")

        tid, pid = self.get_id(url)
        if not tid:
            return False

        posts = self.listener.get_posts(tid)
        if not posts:
            pid = 0

        if pid and self.admin.mysql.ping():
            self.admin.mysql.add_pid(pid)

        return self.admin.recover(self.tieba_name, tid, pid)

    def cmd_hide(self, at, arg):
        """
        hide指令
        屏蔽指令所在主题帖

        权限: 2
        限制: 监听帖禁用
        """

        if at.tid == self.listen_tid:
            return False
        if at.tieba_name != self.tieba_name:
            return None
        if self.access_user.get(at.user.user_name, 0) < 2:
            return None

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if self.admin.del_thread(self.tieba_name, at.tid, is_frs_mask=True):
            return True
        else:
            return None

    def cmd_unhide(self, at, arg):
        """
        unhide指令
        解除指令所在主题帖的屏蔽

        权限: 2
        限制: 监听帖禁用
        """

        if at.tid == self.listen_tid:
            return False
        if at.tieba_name != self.tieba_name:
            return None
        if self.access_user.get(at.user.user_name, 0) < 2:
            return None

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if self.admin.recover(self.tieba_name, at.tid, is_frs_mask=True):
            return True
        else:
            return None

    def cmd_tmphide(self, at, arg):
        """
        tmphide指令
        临时屏蔽指令所在主题帖

        权限: 2
        限制: 监听帖禁用
        """

        if at.tid == self.listen_tid:
            return False
        if at.tieba_name != self.tieba_name:
            return None
        if self.access_user.get(at.user.user_name, 0) < 2:
            return None

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        flag = self.admin.mysql.add_tid(self.tieba_name, at.tid)
        flag = flag and self.admin.del_thread(
            self.tieba_name, at.tid, is_frs_mask=True)

        return True if flag else None

    def cmd_tmpunhide(self, at, arg):
        """
        tmpunhide指令
        解除所有被临时屏蔽主题帖的屏蔽

        权限: 2
        限制: 仅在监听帖可用
        """

        if at.tid != self.listen_tid:
            return False
        if self.access_user.get(at.user.user_name, 0) < 2:
            return None

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        for tid in self.admin.mysql.get_tids(self.tieba_name):
            if self.admin.recover(self.tieba_name, tid, is_frs_mask=True):
                self.admin.mysql.del_tid(self.tieba_name, tid)

        return True

    def cmd_blacklist_add(self, post, id):
        """
        blacklist_add指令
        将id加入贴吧黑名单

        权限: 3
        限制: 仅在监听帖可用
        """

        if post.tid != self.listen_tid:
            return None
        if self.access_user.get(post.user.user_name, 0) < 3:
            return False
        if not id:
            return False

        tb.log.info(f"{post.user.user_name}: {post.text}")

        user = self.listener.get_userinfo_weak(BasicUserInfo(id))

        return self.admin.blacklist_add(self.tieba_name, user)

    def cmd_blacklist_cancel(self, post, id):
        """
        blacklist_cancel指令
        将id移出贴吧黑名单

        权限: 3
        限制: 仅在监听帖可用
        """

        if post.tid != self.listen_tid:
            return None
        if self.access_user.get(post.user.user_name, 0) < 3:
            return False
        if not id:
            return False

        tb.log.info(f"{post.user.user_name}: {post.text}")

        return self.admin.blacklist_cancel(self.tieba_name, id)

    def cmd_mysql_white(self, post, id):
        """
        mysql_white指令
        将id加入脚本白名单

        权限: 3
        限制: 仅在监听帖可用
        """

        if post.tid != self.listen_tid:
            return None
        if self.access_user.get(post.user.user_name, 0) < 3:
            return False
        if not id:
            return False

        tb.log.info(f"{post.user.user_name}: {post.text}")

        if not self.admin.mysql.ping():
            tb.log.error("Failed to excute!")
            return False

        return self.admin.update_user_id(id, True)

    def cmd_mysql_black(self, post, id):
        """
        mysql_black指令
        将id加入脚本黑名单

        权限: 3
        限制: 仅在监听帖可用
        """

        if post.tid != self.listen_tid:
            return None
        if self.access_user.get(post.user.user_name, 0) < 3:
            return False
        if not id:
            return False

        tb.log.info(f"{post.user.user_name}: {post.text}")

        if not self.admin.mysql.ping():
            tb.log.error("Failed to excute!")
            return False

        return self.admin.update_user_id(id, False)

    def cmd_mysql_reset(self, post, id):
        """
        mysql_reset指令
        清除id的脚本黑/白名单状态

        权限: 3
        限制: 仅在监听帖可用
        """

        if post.tid != self.listen_tid:
            return None
        if self.access_user.get(post.user.user_name, 0) < 3:
            return False
        if not id:
            return False

        tb.log.info(f"{post.user.user_name}: {post.text}")

        if not self.admin.mysql.ping():
            tb.log.error("Failed to excute!")
            return False

        return self.admin.del_user_id(id)

    def cmd_default(self, obj, arg):
        """
        default指令
        """

        return False if obj.tid == self.listen_tid else None


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='大吧主放权脚本', allow_abbrev=False)
    parser.add_argument('--admin_BDUSS_key', '-ak',
                        type=str,
                        default='noob',
                        help='用于获取BDUSS，该BDUSS为对应吧的大吧主')
    parser.add_argument('--listener_BDUSS_key', '-lk',
                        type=str,
                        default='listener',
                        help='用于获取BDUSS，该BDUSS为监听者')

    parser.add_argument('--tieba_name', '-b',
                        type=str,
                        default='asoul',
                        help='执行大吧主操作的贴吧名')

    parser.add_argument('--listen_tid', '-t',
                        type=int,
                        help='监听帖子的tid',
                        metavar='TID',
                        default=7672050788)

    listener = Listener(**vars(parser.parse_args()))

    while 1:
        try:
            listener.scan()
            tb.log.debug('heartbeat')
            time.sleep(10)
        except Exception as err:
            tb.log.error(f"Unhandled error:{traceback.format_exc()}")
