# -*- coding:utf-8 -*-
import atexit
import json
import re
import time
import traceback

import tiebaBrowser as tb
import tiebaBrowser.cloud_review as cr
from tiebaBrowser.config import SCRIPT_DIR
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

    def __init__(self):

        config_path = SCRIPT_DIR.parent.joinpath('config/listen_config.json')
        with config_path.open('r', encoding='utf-8') as file:
            config = json.load(file)
        self.listener = tb.Browser(config['listener'])
        self.tieba = config['tieba_list']

        for tieba_name, tieba_dict in self.tieba.items():
            admin_key = tieba_dict['admin']
            self.tieba[tieba_name]['admin'] = cr.CloudReview(
                admin_key, tieba_name)

        self.func_map = {func_name[4:]: getattr(self, func_name) for func_name in dir(
            self) if func_name.startswith("cmd")}
        self.time_range = TimeRange((-30, 0))

    def close(self):
        self.listener.close()
        for tieba_dict in self.tieba.values():
            tieba_dict['admin'].close()

    def scan(self):
        self.time_range.set()
        ats = self.listener.get_ats()

        if ats:
            for end_index, at in enumerate(ats):
                if not self.time_range.is_inrange(at.create_time):
                    ats = ats[:end_index]
                    break

        for at in ats:
            self._handle_cmd(at)

    def _handle_cmd(self, at):
        cmd_type, arg = self._prase_cmd(at.text)
        func = self.func_map.get(cmd_type, self.cmd_default)
        func(at, arg)

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

    def cmd_recommend(self, at, arg):
        """
        recommend指令
        对指令所在主题帖执行“大吧主首页推荐”操作
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if tieba_dict['admin'].recommend(at.tieba_name, at.tid):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_good(self, at, cname):
        """
        good指令
        将指令所在主题帖加到以cname为名的精华分区。cname默认为''即不分区
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return
        if not cname:
            cname = ''

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if tieba_dict['admin'].good(at.tieba_name, at.tid, cname):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_ungood(self, at, arg):
        """
        ungood指令
        撤销指令所在主题帖的精华
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if tieba_dict['admin'].ungood(at.tieba_name, at.tid):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_top(self, at, arg):
        """
        top指令
        置顶指令所在主题帖
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if tieba_dict['admin'].top(at.tieba_name, at.tid):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_untop(self, at, arg):
        """
        untop指令
        撤销指令所在主题帖的置顶
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if tieba_dict['admin'].untop(at.tieba_name, at.tid):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_hide(self, at, arg):
        """
        hide指令
        屏蔽指令所在主题帖
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if tieba_dict['admin'].del_thread(at.tieba_name, at.tid, is_frs_mask=True):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_unhide(self, at, arg):
        """
        unhide指令
        解除指令所在主题帖的屏蔽
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if tieba_dict['admin'].recover(at.tieba_name, at.tid, is_frs_mask=True):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_drop(self, at, arg):
        """
        drop指令
        删除指令所在主题帖并封禁楼主十天
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        posts = self.listener.get_posts(at.tid)
        if not posts:
            return

        tb.log.info(
            f"Try to delete thread {posts[0].text} post by {posts[0].user.log_name}")

        tieba_dict['admin'].block(at.tieba_name, posts[0].user, day=10)
        tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)
        tieba_dict['admin'].del_thread(at.tieba_name, at.tid)

    def cmd_exdrop(self, at, arg):
        """
        exdrop指令
        删除指令所在主题帖并将楼主加入脚本黑名单+封禁十天
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if not tieba_dict['admin'].mysql.ping():
            tb.log.error("Failed to ping:{at.tieba_name}")
            return

        posts = self.listener.get_posts(at.tid)
        if not posts:
            return

        tb.log.info(
            f"Try to delete thread {posts[0].text} post by {posts[0].user.log_name}")

        if tieba_dict['admin'].block(at.tieba_name, posts[0].user, day=10) and tieba_dict['admin'].mysql.update_user_id(at.tieba_name, posts[0].user.user_id, False):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)
        tieba_dict['admin'].del_thread(at.tieba_name, at.tid)

    def cmd_delete(self, at, arg):
        """
        delete指令
        删除指令所在主题帖
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        posts = self.listener.get_posts(at.tid)
        if not posts:
            return

        tb.log.info(
            f"Try to delete thread {posts[0].text} post by {posts[0].user.log_name}")

        tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)
        tieba_dict['admin'].del_thread(at.tieba_name, at.tid)

    def cmd_tmphide(self, at, arg):
        """
        tmphide指令
        暂时屏蔽指令所在主题帖
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if not tieba_dict['admin'].mysql.ping():
            tb.log.error("Failed to ping:{at.tieba_name}")
            return

        tieba_dict['admin'].mysql.add_tid(at.tieba_name, at.tid)
        if tieba_dict['admin'].del_thread(at.tieba_name, at.tid, is_frs_mask=True):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_tmpunhide(self, at, arg):
        """
        tmpunhide指令
        解除指令所在主题帖的屏蔽
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if not tieba_dict['admin'].mysql.ping():
            tb.log.error("Failed to ping:{at.tieba_name}")
            return

        tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)
        for tid in tieba_dict['admin'].mysql.get_tids(at.tieba_name):
            if tieba_dict['admin'].recover(at.tieba_name, tid, is_frs_mask=True):
                tieba_dict['admin'].mysql.del_tid(at.tieba_name, tid)

    def cmd_block(self, at, id):
        """
        block指令
        通过id封禁对应用户十天
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = self.listener.get_userinfo(UserInfo(id))

        if tieba_dict['admin'].block(at.tieba_name, user, day=10):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_block3(self, at, id):
        """
        block指令
        通过id封禁对应用户三天
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = self.listener.get_userinfo(UserInfo(id))

        if tieba_dict['admin'].block(at.tieba_name, user, day=3):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_unblock(self, at, id):
        """
        unblock指令
        通过id解封用户
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = self.listener.get_userinfo(UserInfo(id))

        if tieba_dict['admin'].unblock(at.tieba_name, user):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_blacklist_add(self, at, id):
        """
        blacklist_add指令
        将id加入贴吧黑名单
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = self.listener.get_userinfo_weak(BasicUserInfo(id))

        if tieba_dict['admin'].blacklist_add(at.tieba_name, user):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_blacklist_cancel(self, at, id):
        """
        blacklist_cancel指令
        将id移出贴吧黑名单
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = self.listener.get_userinfo_weak(BasicUserInfo(id))

        if tieba_dict['admin'].blacklist_cancel(at.tieba_name, user):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_mysql_white(self, at, id):
        """
        mysql_white指令
        将id加入脚本白名单
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        if not tieba_dict['admin'].mysql.ping():
            tb.log.error("Failed to ping:{at.tieba_name}")
            return

        if tieba_dict['admin'].update_user_id(id, True):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_mysql_black(self, at, id):
        """
        mysql_black指令
        将id加入脚本黑名单
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        if not tieba_dict['admin'].mysql.ping():
            tb.log.error("Failed to ping:{at.tieba_name}")
            return

        if tieba_dict['admin'].update_user_id(id, False):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_mysql_reset(self, at, id):
        """
        mysql_reset指令
        清除id的脚本黑/白名单状态
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        if not tieba_dict['admin'].mysql.ping():
            tb.log.error("Failed to ping:{at.tieba_name}")
            return

        if tieba_dict['admin'].del_user_id(id):
            tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_ping(self, at, arg):
        """
        ping指令
        用于测试bot可用性的空指令
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if at.user.user_name not in tieba_dict['access_user']:
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    def cmd_default(self, at, arg):
        """
        default指令
        """

        return


if __name__ == '__main__':

    listener = Listener()

    while 1:
        try:
            listener.scan()
            tb.log.debug('heartbeat')
            time.sleep(5)
        except Exception as err:
            tb.log.error(f"Unhandled error:{traceback.format_exc()}")
