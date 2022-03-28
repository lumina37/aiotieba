# -*- coding:utf-8 -*-
import asyncio
import json
import re
import time
import traceback
from collections import OrderedDict
from types import TracebackType
from typing import Optional, Type

import tiebaBrowser as tb
from tiebaBrowser._config import SCRIPT_PATH


class TimerRecorder(object):
    """
    时间记录器

    Args:
        shift_sec: float 启动时允许解析shift_sec秒之前的at
        post_interval: float 两次post_add之间需要的时间间隔

    Fields:
        last_parse_time: float 上次解析at信息的时间(以百度服务器为准)
        last_post_time: float 上次发送回复的时间(以百度服务器为准)
        post_interval: float 两次post_add之间需要的时间间隔
    """

    __slots__ = ['last_parse_time', 'last_post_time', 'post_interval']

    def __init__(self, shift_sec, post_interval):

        self.last_post_time = 0
        self.post_interval = post_interval
        self.last_parse_time = time.time() - shift_sec

    def is_inrange(self, check_time):
        return self.last_parse_time < check_time

    def allow_execute(self):
        current_time = time.time()
        if current_time-self.last_post_time > self.post_interval:
            self.last_post_time = current_time
            return True
        else:
            return False


class Listener(object):

    def __init__(self):

        self.config_path = SCRIPT_PATH.parent / 'config/listen_config.json'
        with self.config_path.open('r', encoding='utf-8') as _file:
            self.config = json.load(_file)

        self.listener = tb.Browser(self.config['listener'])
        self.speaker = tb.Browser(self.config['speaker'])
        self.tieba = self.config['tieba_list']

        for tieba_name, tieba_dict in self.tieba.items():
            admin_key = tieba_dict['admin']
            tieba_dict['admin'] = tb.CloudReview(
                admin_key, tieba_name)
            tieba_dict['access_user'] = OrderedDict.fromkeys(
                tieba_dict['access_user'])

        self.func_map = {func_name[4:]: getattr(self, func_name) for func_name in dir(
            self) if func_name.startswith("cmd")}
        self.time_recorder = TimerRecorder(600, 30)

    async def close(self) -> None:
        coros = [tieba_dict['admin'].close()
                 for tieba_dict in self.tieba.values()]
        coros.append(self.listener.close())
        coros.append(self.speaker.close())
        await asyncio.gather(*coros, return_exceptions=True)

        for tieba_dict in self.tieba.values():
            tieba_dict['admin'] = tieba_dict['admin'].BDUSS_key
            tieba_dict['access_user'] = list(
                tieba_dict['access_user'].keys())

        with self.config_path.open('w', encoding='utf-8') as _file:
            json.dump(self.config, _file, sort_keys=False,
                      indent=1, separators=(',', ':'), ensure_ascii=False)

    async def __aenter__(self) -> "Listener":
        return self

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        await self.close()

    async def run(self):

        while 1:
            try:
                asyncio.create_task(self.scan())
                tb.log.debug('heartbeat')
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                break
            except Exception as err:
                tb.log.critical(f"Unhandled error:{traceback.format_exc()}")
                return

    async def scan(self) -> None:
        ats = await self.listener.get_ats()
        for end_idx, at in enumerate(ats):
            if not self.time_recorder.is_inrange(at.create_time):
                self.time_recorder.last_parse_time = ats[0].create_time
                ats = ats[:end_idx]
                break

        await asyncio.gather(*[asyncio.wait_for(self._handle_cmd(at), timeout=120) for at in ats], return_exceptions=True)

    async def _handle_cmd(self, at) -> None:
        cmd_type, arg = self._parse_cmd(at.text)
        func = self.func_map.get(cmd_type, self.cmd_default)
        await func(at, arg)

    @staticmethod
    def _parse_cmd(text) -> tuple[str, str]:
        """
        解析指令
        """

        cmd_type = ''
        arg = ''

        if not text.startswith('@'):
            return cmd_type, arg

        first_blank_idx = text.find(' ')
        if (split_start_idx := first_blank_idx+1) == len(text):
            return cmd_type, arg

        cmd = text[split_start_idx:].strip()
        cmds = cmd.split(' ', 1)

        if len(cmds) == 1:
            cmd_type = cmds[0]
        else:
            cmd_type = cmds[0]
            arg = cmds[1]

        return cmd_type, arg

    async def cmd_recommend(self, at, arg):
        """
        recommend指令
        对指令所在主题帖执行“大吧主首页推荐”操作
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await tieba_dict['admin'].recommend(at.tieba_name, at.tid):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_move(self, at, tab_name):
        """
        move指令
        将指令所在主题帖移动至名为tab_name的分区
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        if not (threads := await self.listener.get_threads(at.tieba_name)):
            return

        from_tab_id = 0
        for thread in threads:
            if thread.tid == at.tid:
                from_tab_id = thread.tab_id
        to_tab_id = threads.tab_map.get(tab_name, 0)

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await tieba_dict['admin'].move(at.tieba_name, at.tid, to_tab_id, from_tab_id):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_good(self, at, cname):
        """
        good指令
        将指令所在主题帖加到以cname为名的精华分区。cname默认为''即不分区
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return
        if not cname:
            cname = ''

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await tieba_dict['admin'].good(at.tieba_name, at.tid, cname):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_ungood(self, at, arg):
        """
        ungood指令
        撤销指令所在主题帖的精华
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await tieba_dict['admin'].ungood(at.tieba_name, at.tid):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_top(self, at, arg):
        """
        top指令
        置顶指令所在主题帖
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await tieba_dict['admin'].top(at.tieba_name, at.tid):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_untop(self, at, arg):
        """
        untop指令
        撤销指令所在主题帖的置顶
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await tieba_dict['admin'].untop(at.tieba_name, at.tid):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_hide(self, at, arg):
        """
        hide指令
        屏蔽指令所在主题帖
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await tieba_dict['admin'].hide_thread(at.tieba_name, at.tid):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_unhide(self, at, arg):
        """
        unhide指令
        解除指令所在主题帖的屏蔽
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await tieba_dict['admin'].unhide_thread(at.tieba_name, at.tid):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_drop(self, at, arg):
        """
        drop指令
        删除指令所在主题帖并封禁楼主十天
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        if not (posts := await self.listener.get_posts(at.tid)):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        tb.log.info(
            f"Try to delete thread {posts[0].text} post by {posts[0].user.log_name}")

        await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)
        await asyncio.gather(tieba_dict['admin'].block(at.tieba_name, posts[0].user, day=10), tieba_dict['admin'].del_thread(at.tieba_name, at.tid))

    async def cmd_exdrop(self, at, arg):
        """
        exdrop指令
        删除指令所在主题帖并将楼主加入脚本黑名单+封禁十天
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        if not (posts := await self.listener.get_posts(at.tid)):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if not await tieba_dict['admin'].mysql.ping():
            tb.log.warning("Failed to ping:{at.tieba_name}")
            return

        tb.log.info(
            f"Try to delete thread {posts[0].text} post by {posts[0].user.log_name}")

        results = await asyncio.gather(tieba_dict['admin'].block(at.tieba_name, posts[0].user, day=10), tieba_dict['admin'].mysql.update_user_id(at.tieba_name, posts[0].user.user_id, False))
        if results[0] and results[1]:
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)
        await tieba_dict['admin'].del_thread(at.tieba_name, at.tid)

    async def cmd_delete(self, at, arg):
        """
        delete指令
        删除指令所在主题帖
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if (posts := await self.listener.get_posts(at.tid)):
            tb.log.info(
                f"Try to delete thread {posts[0].text} post by {posts[0].user.log_name}")

        await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)
        await tieba_dict['admin'].del_thread(at.tieba_name, at.tid)

    async def cmd_water(self, at, arg):
        """
        water指令
        将指令所在主题帖标记为无关水，并临时屏蔽
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if not await tieba_dict['admin'].mysql.ping():
            tb.log.warning("Failed to ping:{at.tieba_name}")
            return

        if await tieba_dict['admin'].mysql.update_tid(at.tieba_name, at.tid, True) and await tieba_dict['admin'].hide_thread(at.tieba_name, at.tid):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_unwater(self, at, arg):
        """
        unwater指令
        清除指令所在主题帖的无关水标记，并立刻解除屏蔽
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if not await tieba_dict['admin'].mysql.ping():
            tb.log.warning("Failed to ping:{at.tieba_name}")
            return

        if await tieba_dict['admin'].mysql.del_tid(at.tieba_name, at.tid) and await tieba_dict['admin'].unhide_thread(at.tieba_name, at.tid):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_water_restrict(self, at, mode):
        """
        water_restrict指令
        控制当前吧的云审查脚本的无关水管控状态
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if not await tieba_dict['admin'].mysql.ping():
            tb.log.warning("Failed to ping:{at.tieba_name}")
            return

        if mode == "enter":
            if await tieba_dict['admin'].mysql.update_tid(at.tieba_name, 0, True):
                await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)
        elif mode == "exit":
            if await tieba_dict['admin'].mysql.update_tid(at.tieba_name, 0, False):
                await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)
            async for tid in tieba_dict['admin'].mysql.get_tids(at.tieba_name):
                if await tieba_dict['admin'].unhide_thread(at.tieba_name, tid):
                    await tieba_dict['admin'].mysql.update_tid(at.tieba_name, tid, False)

    async def cmd_block(self, at, id):
        """
        block指令
        通过id封禁对应用户十天
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = await self.listener.get_user_info(id)

        if await tieba_dict['admin'].block(at.tieba_name, user, day=10):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_block3(self, at, id):
        """
        block指令
        通过id封禁对应用户三天
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = await self.listener.get_user_info(id)

        if await tieba_dict['admin'].block(at.tieba_name, user, day=3):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_unblock(self, at, id):
        """
        unblock指令
        通过id解封用户
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = await self.listener.get_user_info(id)

        if await tieba_dict['admin'].unblock(at.tieba_name, user):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_blacklist_add(self, at, id):
        """
        blacklist_add指令
        将id加入贴吧黑名单
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = await self.listener.get_basic_user_info(id)

        if await tieba_dict['admin'].blacklist_add(at.tieba_name, user):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_blacklist_cancel(self, at, id):
        """
        blacklist_cancel指令
        将id移出贴吧黑名单
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = await self.listener.get_basic_user_info(id)

        if await tieba_dict['admin'].blacklist_cancel(at.tieba_name, user):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_mysql_white(self, at, id):
        """
        mysql_white指令
        将id加入脚本白名单
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        if not await tieba_dict['admin'].mysql.ping():
            tb.log.warning("Failed to ping:{at.tieba_name}")
            return

        if await tieba_dict['admin'].update_user_id(id, True):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_mysql_black(self, at, id):
        """
        mysql_black指令
        将id加入脚本黑名单
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        if not await tieba_dict['admin'].mysql.ping():
            tb.log.warning("Failed to ping:{at.tieba_name}")
            return

        if await tieba_dict['admin'].update_user_id(id, False):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_mysql_reset(self, at, id):
        """
        mysql_reset指令
        清除id的脚本黑/白名单状态
        """

        if not id:
            return
        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        if not await tieba_dict['admin'].mysql.ping():
            tb.log.warning("Failed to ping:{at.tieba_name}")
            return

        if await tieba_dict['admin'].del_user_id(id):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_holyshit(self, at, extra_info):
        """
        holyshit指令
        召唤五名活跃吧务，使用参数extra_info来附带额外的召唤需求
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not self.time_recorder.allow_execute():
            return

        active_admin_list = list(tieba_dict['access_user'].keys())[:5]
        content = f"{extra_info}@"+" @".join(active_admin_list)

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await self.speaker.add_post(at.tieba_name, at.tid, content):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_refuse_appeals(self, at, arg):
        """
        refuse_appeals指令
        一键拒绝所有解封申诉
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await tieba_dict['admin'].refuse_appeals(at.tieba_name):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_recom_status(self, at, arg):
        """
        recom_status指令
        获取大吧主推荐功能的月度配额状态
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not self.time_recorder.allow_execute():
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        total_recom_num, used_recom_num = await tieba_dict['admin'].get_recom_status(at.tieba_name)
        content = f"@{at.user.user_name} \nUsed: {used_recom_num} / {total_recom_num} = {used_recom_num/total_recom_num*100:.2f}%"

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await self.speaker.add_post(at.tieba_name, at.tid, content):
            await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_register(self, at, arg):
        """
        register指令
        将发起指令的吧务移动到活跃吧务队列的最前端，以响应holyshit指令
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        tieba_dict['access_user'].move_to_end(at.user.user_name, last=False)

        await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_ping(self, at, arg):
        """
        ping指令
        用于测试bot可用性的空指令
        """

        tieba_dict = self.tieba.get(at.tieba_name, None)
        if not tieba_dict:
            return
        if not tieba_dict['access_user'].__contains__(at.user.user_name):
            return

        tb.log.info(f"{at.user.user_name}: {at.text}")

        await tieba_dict['admin'].del_post(at.tieba_name, at.tid, at.pid)

    async def cmd_default(self, at, arg):
        """
        default指令
        """

        return


if __name__ == '__main__':

    async def main():
        async with Listener() as listener:
            await listener.run()

    try:
        asyncio.run(main())
    except:
        pass
