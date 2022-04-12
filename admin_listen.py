# -*- coding:utf-8 -*-
import asyncio
import functools
import json
import re
import time
from collections.abc import Callable

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

    def __init__(self, shift_sec, post_interval) -> None:

        self.last_post_time = 0
        self.post_interval = post_interval
        self.last_parse_time = time.time() - shift_sec

    def is_inrange(self, check_time) -> bool:
        return self.last_parse_time < check_time

    def allow_execute(self) -> bool:
        current_time = time.time()
        if current_time - self.last_post_time > self.post_interval:
            self.last_post_time = current_time
            return True
        else:
            return False


def _check(need_access: int = 0, need_arg_num: int = 0) -> Callable:
    """
    装饰器实现鉴权

    Args:
        need_access (int, optional): 需要的权限级别
        need_arg_num (bool, optional): 需要的参数数量
    """

    def wrapper(func) -> Callable:

        @functools.wraps(func)
        async def foo(self: "Listener", at: tb.At, *args):
            if len(args) < need_arg_num:
                return
            handler = self.handler_map.get(at.tieba_name, None)
            if not handler:
                return
            if need_access and await handler.admin.database.get_user_id(at.tieba_name, at.user.user_id) < need_access:
                return
            return await func(self, handler, at, *args)

        return foo

    return wrapper


class Handler(object):

    __slots__ = ['tieba_name', 'admin', 'speaker']

    def __init__(self, tieba_config: dict) -> None:
        self.tieba_name = tieba_config['tieba_name']
        self.admin = tb.Reviewer(tieba_config['admin_key'], self.tieba_name)
        self.speaker = tb.Browser(tieba_config['speaker_key'])

    async def close(self):
        await asyncio.gather(self.admin.close(), self.speaker.close(), return_exceptions=True)

    def to_dict(self):
        return {
            'tieba_name': self.tieba_name,
            'admin_key': self.admin.BDUSS_key,
            'speaker_key': self.speaker.BDUSS_key,
        }


class Listener(object):

    __slots__ = ['_config_mtime', 'listener', 'handler_map', '_cmd_map', 'time_recorder']

    def __init__(self) -> None:

        config_path = SCRIPT_PATH.parent / 'config/listen_config.json'
        with config_path.open('r', encoding='utf-8') as _file:
            config = json.load(_file)
        self._config_mtime = config_path.stat().st_mtime

        self.listener = tb.Reviewer(config['listener_key'], '')
        self.handler_map = {(handler := Handler(tieba_config)).tieba_name: handler
                            for tieba_config in config['tieba_configs']}

        self._cmd_map = {
            func_name[4:]: getattr(self, func_name)
            for func_name in dir(self) if func_name.startswith("cmd")
        }
        self.time_recorder = TimerRecorder(3600, 30)

    async def close(self) -> None:
        await asyncio.gather(*[handler.close() for handler in self.handler_map.values()],
                             self.listener.close(),
                             return_exceptions=True)

        config_path = SCRIPT_PATH.parent / 'config/listen_config.json'
        if self._config_mtime != config_path.stat().st_mtime:
            return

        with config_path.open('w', encoding='utf-8') as _file:
            json.dump(self.to_dict(), _file, sort_keys=False, indent=2, separators=(',', ':'), ensure_ascii=False)

    def to_dict(self):
        return {
            'listener_key': self.listener.BDUSS_key,
            'tieba_configs': [handler.to_dict() for handler in self.handler_map.values()]
        }

    async def __aenter__(self) -> "Listener":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def run(self) -> None:

        while 1:
            try:
                asyncio.create_task(self.scan())
                tb.log.debug('heartbeat')
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                break
            except Exception:
                tb.log.critical(f"Unhandled error", exc_info=True)
                return

    async def scan(self) -> None:
        ats = await self.listener.get_ats()
        for end_idx, at in enumerate(ats):
            if not self.time_recorder.is_inrange(at.create_time):
                self.time_recorder.last_parse_time = ats[0].create_time
                ats = ats[:end_idx]
                break

        await asyncio.gather(*[asyncio.wait_for(self._handle_cmd(at), timeout=120) for at in ats],
                             return_exceptions=True)

    @staticmethod
    def _parse_cmd(text: str) -> tuple[str, str]:
        """
        解析指令
        """

        cmd_type = ''
        args = []

        text = text[text.find('@'):]
        first_blank_idx = text.find(' ')
        if (split_start_idx := first_blank_idx + 1) == len(text):
            return cmd_type, args

        cmd = text[split_start_idx:].strip()
        cmds = [arg.lstrip() for arg in cmd.split(' ') if arg]
        cmd_type = cmds[0]
        args = cmds[1:]

        return cmd_type, args

    async def _handle_cmd(self, at: tb.At) -> None:
        cmd_type, args = self._parse_cmd(at.text)
        cmd_func = self._cmd_map.get(cmd_type, self.cmd_default)
        await cmd_func(at, *args)

    async def _arg2user_info(self, arg: str) -> tb.UserInfo:
        if (res := re.search(r'#(\d+)#', arg)):
            tieba_uid = int(res.group(1))
            user = await self.listener.tieba_uid2user_info(tieba_uid)
        else:
            user = await self.listener.get_basic_user_info(arg)

        return user

    @_check(need_access=1, need_arg_num=0)
    async def cmd_recommend(self, handler: Handler, at: tb.At, *args) -> None:
        """
        recommend指令
        对指令所在主题帖执行“大吧主首页推荐”操作
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.admin.recommend(at.tieba_name, at.tid):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=2, need_arg_num=1)
    async def cmd_move(self, handler: Handler, at: tb.At, *args) -> None:
        """
        move指令
        将指令所在主题帖移动至名为tab_name的分区
        """

        if not (threads := await self.listener.get_threads(at.tieba_name)):
            return

        from_tab_id = 0
        for thread in threads:
            if thread.tid == at.tid:
                from_tab_id = thread.tab_id
        to_tab_id = threads.tab_map.get(args[0], 0)

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.admin.move(at.tieba_name, at.tid, to_tab_id, from_tab_id):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=2, need_arg_num=0)
    async def cmd_good(self, handler: Handler, at: tb.At, *args) -> None:
        """
        good指令
        将指令所在主题帖加到以cname为名的精华分区。cname默认为''即不分区
        """

        cname = args[0] if len(args) else ''

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.admin.good(at.tieba_name, at.tid, cname):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=2, need_arg_num=0)
    async def cmd_ungood(self, handler: Handler, at: tb.At, *args) -> None:
        """
        ungood指令
        撤销指令所在主题帖的精华
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.admin.ungood(at.tieba_name, at.tid):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=4, need_arg_num=0)
    async def cmd_top(self, handler: Handler, at: tb.At, *args) -> None:
        """
        top指令
        置顶指令所在主题帖
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.admin.top(at.tieba_name, at.tid):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=4, need_arg_num=0)
    async def cmd_untop(self, handler: Handler, at: tb.At, *args) -> None:
        """
        untop指令
        撤销指令所在主题帖的置顶
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.admin.untop(at.tieba_name, at.tid):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=2, need_arg_num=0)
    async def cmd_hide(self, handler: Handler, at: tb.At, *args) -> None:
        """
        hide指令
        屏蔽指令所在主题帖
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.admin.hide_thread(at.tieba_name, at.tid):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=2, need_arg_num=0)
    async def cmd_unhide(self, handler: Handler, at: tb.At, *args) -> None:
        """
        unhide指令
        解除指令所在主题帖的屏蔽
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.admin.unhide_thread(at.tieba_name, at.tid):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=2, need_arg_num=0)
    async def cmd_delete(self, handler: Handler, at: tb.At, *args) -> None:
        """
        delete指令
        删帖
        """

        await self._del_ops(handler, at)

    @_check(need_access=2, need_arg_num=0)
    async def cmd_drop(self, handler: Handler, at: tb.At, *args) -> None:
        """
        drop指令
        删帖并封10天
        """

        note = args[0] if args else ''
        await self._del_ops(handler, at, 10, note)

    @_check(need_access=2, need_arg_num=0)
    async def cmd_drop3(self, handler: Handler, at: tb.At, *args) -> None:
        """
        drop3指令
        删帖并封3天
        """

        note = args[0] if args else ''
        await self._del_ops(handler, at, 3, note)

    @_check(need_access=4, need_arg_num=0)
    async def cmd_exdrop(self, handler: Handler, at: tb.At, *args) -> None:
        """
        exdrop指令
        删帖并将发帖人加入脚本黑名单+封禁十天
        """

        note = args[0] if args else ''
        await self._del_ops(handler, at, 10, note, blacklist=True)

    async def _del_ops(self, handler: Handler, at: tb.At, block_days: int = 0, note: str = '', blacklist: bool = False):
        """
        各种处罚指令的实现
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        coros = []

        if at.is_floor:
            if not (comments := await self.listener.get_comments(at.tid, at.pid, is_floor=True)):
                return
            target = comments.post
            tb.log.info(f"Try to delete post {target.text} post by {target.user.log_name}")
            coros.append(handler.admin.del_post(at.tieba_name, target.tid, target.pid))

        else:
            if not (posts := await self.listener.get_posts(at.tid, rn=0)):
                return

            if at.is_thread:
                if posts.forum.fid != (target := posts.thread.share_origin).fid:
                    return
                target = posts.thread.share_origin
                if not target.contents.ats:
                    return
                target.user = await self.listener.get_basic_user_info(target.contents.ats[0].user_id)
                tb.log.info(f"Try to delete thread {target.text} post by {target.user.log_name}")
                coros.append(handler.admin.del_thread(at.tieba_name, target.tid))

            else:
                target = posts[0]
                tb.log.info(f"Try to delete thread {target.text} post by {target.user.log_name}")
                coros.append(handler.admin.del_thread(at.tieba_name, target.tid))

        if block_days:
            coros.append(handler.admin.block(at.tieba_name, target.user, block_days, note))
        if blacklist:
            await handler.admin.database.ping()
            tb.log.info(f"Try to sql_black {target.user.log_name} in {at.tieba_name}")
            coros.append(
                handler.admin.database.add_user_id(at.tieba_name, target.user.user_id, -5,
                                                   f"cmd exdrop by {at.user.user_id}"))

        await handler.admin.del_post(at.tieba_name, at.tid, at.pid)
        await asyncio.gather(*coros)

    @_check(need_access=2, need_arg_num=0)
    async def cmd_water(self, handler: Handler, at: tb.At, *args) -> None:
        """
        water指令
        将指令所在主题帖标记为无关水，并临时屏蔽
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if not await handler.admin.database.ping():
            return

        if await handler.admin.database.add_tid(at.tieba_name, at.tid, True) and await handler.admin.hide_thread(
                at.tieba_name, at.tid):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=2, need_arg_num=0)
    async def cmd_unwater(self, handler: Handler, at: tb.At, *args) -> None:
        """
        unwater指令
        清除指令所在主题帖的无关水标记，并立刻解除屏蔽
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if not await handler.admin.database.ping():
            return

        if await handler.admin.database.del_tid(at.tieba_name, at.tid) and await handler.admin.unhide_thread(
                at.tieba_name, at.tid):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=3, need_arg_num=1)
    async def cmd_water_restrict(self, handler: Handler, at: tb.At, *args) -> None:
        """
        water_restrict指令
        控制当前吧的云审查脚本的无关水管控状态
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if not await handler.admin.database.ping():
            return

        if args[0] == "enter":
            if await handler.admin.database.add_tid(at.tieba_name, 0, True):
                await handler.admin.del_post(at.tieba_name, at.tid, at.pid)
        elif args[0] == "exit":
            if await handler.admin.database.add_tid(at.tieba_name, 0, False):
                await handler.admin.del_post(at.tieba_name, at.tid, at.pid)
            async for tid in handler.admin.database.get_tids(at.tieba_name):
                if await handler.admin.unhide_thread(at.tieba_name, tid):
                    await handler.admin.database.add_tid(at.tieba_name, tid, False)

    @_check(need_access=2, need_arg_num=1)
    async def cmd_block(self, handler: Handler, at: tb.At, *args) -> None:
        """
        block指令
        通过id封禁对应用户10天
        """

        await self._block(handler, at, args, 10)

    @_check(need_access=2, need_arg_num=1)
    async def cmd_block3(self, handler: Handler, at: tb.At, *args) -> None:
        """
        block3指令
        通过id封禁对应用户3天
        """

        await self._block(handler, at, args, 3)

    async def _block(self, handler: Handler, at: tb.At, args: list[str], block_days: int) -> None:
        """
        block & block3指令的实现
        """

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = await self._arg2user_info(args[0])
        note = args[1] if len(args) >= 2 else ''

        if await handler.admin.block(at.tieba_name, user, block_days, note):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=2, need_arg_num=1)
    async def cmd_unblock(self, handler: Handler, at: tb.At, *args) -> None:
        """
        unblock指令
        通过id解封用户
        """

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = await self._arg2user_info(args[0])

        if await handler.admin.unblock(at.tieba_name, user):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=4, need_arg_num=1)
    async def cmd_tb_black(self, handler: Handler, at: tb.At, *args) -> None:
        """
        tb_black指令
        将id加入贴吧黑名单
        """

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = await self._arg2user_info(args[0])

        if await handler.admin.blacklist_add(at.tieba_name, user):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=3, need_arg_num=1)
    async def cmd_tb_del(self, handler: Handler, at: tb.At, *args) -> None:
        """
        tb_del指令
        将id移出贴吧黑名单
        """

        tb.log.info(f"{at.user.user_name}: {at.text}")

        user = await self._arg2user_info(args[0])

        if await handler.admin.blacklist_del(at.tieba_name, user):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=3, need_arg_num=1)
    async def cmd_sql_white(self, handler: Handler, at: tb.At, *args) -> None:
        """
        sql_white指令
        将id加入脚本白名单
        """

        tb.log.info(f"{at.user.user_name}: {at.text}")

        if not await handler.admin.database.ping():
            return

        user = await self._arg2user_info(args[0])

        tb.log.info(f"Try to sql_white {user.log_name} in {at.tieba_name}")
        if await handler.admin.database.add_user_id(at.tieba_name, user.user_id, 1,
                                                    f"cmd sql_white by {at.user.user_id}"):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=4, need_arg_num=1)
    async def cmd_sql_black(self, handler: Handler, at: tb.At, *args) -> None:
        """
        sql_black指令
        将id加入脚本黑名单
        """

        tb.log.info(f"{at.user.user_name}: {at.text}")

        if not await handler.admin.database.ping():
            return

        user = await self._arg2user_info(args[0])

        tb.log.info(f"Try to sql_black {user.log_name} in {at.tieba_name}")
        if await handler.admin.database.add_user_id(at.tieba_name, user.user_id, -5,
                                                    f"cmd sql_black by {at.user.user_id}"):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=3, need_arg_num=1)
    async def cmd_sql_del(self, handler: Handler, at: tb.At, *args) -> None:
        """
        sql_del指令
        将id移出脚本名单
        """

        tb.log.info(f"{at.user.user_name}: {at.text}")

        if not await handler.admin.database.ping():
            return

        user = await self._arg2user_info(args[0])

        tb.log.info(f"Try to sql_del {user.log_name} in {at.tieba_name}")
        if await handler.admin.database.del_user_id(at.tieba_name, user.user_id):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=0, need_arg_num=0)
    async def cmd_holyshit(self, handler: Handler, at: tb.At, *args) -> None:
        """
        holyshit指令
        召唤4名活跃吧务，使用参数extra_info来附带额外的召唤需求
        """

        if not self.time_recorder.allow_execute():
            return

        active_admin_list = [
            (await self.listener.get_basic_user_info(user_id)).user_name
            for user_id in await handler.admin.database.get_user_id_list(at.tieba_name, limit=4, permission=2)
        ]
        extra_info = args[0] if len(args) else ''
        content = f"{extra_info}@" + " @".join(active_admin_list)

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.speaker.add_post(at.tieba_name, at.tid, content):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=2, need_arg_num=0)
    async def cmd_refuse_appeals(self, handler: Handler, at: tb.At, *args) -> None:
        """
        refuse_appeals指令
        一键拒绝所有解封申诉
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.admin.refuse_appeals(at.tieba_name):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=1, need_arg_num=0)
    async def cmd_recom_status(self, handler: Handler, at: tb.At, *args) -> None:
        """
        recom_status指令
        获取大吧主推荐功能的月度配额状态
        """

        if not self.time_recorder.allow_execute():
            return

        total_recom_num, used_recom_num = await handler.admin.get_recom_status(at.tieba_name)
        content = f"@{at.user.user_name} \nUsed: {used_recom_num} / {total_recom_num} = {used_recom_num/total_recom_num*100:.2f}%"

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.speaker.add_post(at.tieba_name, at.tid, content):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=1, need_arg_num=2)
    async def cmd_vote_stat(self, handler: Handler, at: tb.At, *args) -> None:
        """
        vote_stat指令
        统计投票结果
        """

        if not args[1].isdigit():
            return
        if not self.time_recorder.allow_execute():
            return

        async def _stat_pn(pn: int) -> None:
            """
            统计主题帖第pn页的投票结果

            Args:
                pn (int): 页码
            """

            posts = await self.listener.get_posts(at.tid,
                                                  pn,
                                                  only_thread_author=True,
                                                  with_comments=True,
                                                  comment_sort_by_agree=True)
            await asyncio.gather(*[_stat_post(post) for post in posts])

        async def _stat_post(post: tb.Post) -> None:
            """
            统计楼层票数

            Args:
                post (tiebaBrowser.Post): 楼层对应的post
            """

            vote_set = set()

            for pn in range(1, 99999):
                comments = await self.listener.get_comments(post.tid, post.pid, pn)
                for comment in comments:
                    text = re.sub('^回复.*?:', '', comment.text)
                    if args[0] in text:
                        vote_set.add(comment.user.user_id)

                if not comments.has_more:
                    break

            if (vote_num := len(vote_set)):
                results.append((post.floor, vote_num))

        results = []
        posts = await self.listener.get_posts(at.tid, 1, with_comments=True, comment_sort_by_agree=False)
        await asyncio.gather(*[_stat_post(post) for post in posts[1:]])

        if (total_page := posts.page.total_page) > 1:
            await asyncio.gather(*[_stat_pn(pn) for pn in range(2, total_page + 1)], return_exceptions=True)

        results.sort(key=lambda result: result[1], reverse=True)
        contents = [f"@{at.user.user_name} "]
        contents.extend([f"floor:{floor} num:{vote_num}" for floor, vote_num in results[:int(args[1])]])
        content = '\n'.join(contents)

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.speaker.add_post(at.tieba_name, at.tid, content):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=5, need_arg_num=1)
    async def cmd_set(self, handler: Handler, at: tb.At, *args) -> None:
        """
        set指令
        设置用户的权限级别
        """

        if len(args) == 1:
            new_access = int(args[0])
            posts = await self.listener.get_posts(at.tid, rn=2)
            user_id = posts.thread.user.user_id
        else:
            new_access = int(args[1])
            user = await self._arg2user_info(args[0])
            user_id = user.user_id

        if not user_id:
            return

        old_access = await handler.admin.database.get_user_id(at.tieba_name, user_id)
        this_access = await handler.admin.database.get_user_id(at.tieba_name, at.user.user_id)
        if old_access >= this_access or new_access >= this_access:
            return

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if await handler.admin.database.add_user_id(at.tieba_name, user_id, new_access,
                                                    f"cmd set by {at.user.user_id}"):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=0, need_arg_num=0)
    async def cmd_register(self, handler: Handler, at: tb.At, *args) -> None:
        """
        register指令
        通过精品帖自助获取1级权限
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        if not handler.access_users.__contains__(at.user.user_name):
            for thread in await self.listener.get_threads(at.tieba_name, is_good=True):
                user_id = at.user.user_id
                if thread.user.user_id == user_id and thread.create_time > time.time(
                ) - 30 * 24 * 3600 and handler.admin.database.get_user_id(at.tieba_name, user_id) == 0:
                    if await handler.admin.database.add_user_id(at.tieba_name, user_id, 1, "cmd register"):
                        await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=2, need_arg_num=0)
    async def cmd_active(self, handler: Handler, at: tb.At, *args) -> None:
        """
        active指令
        将发起指令的吧务移动到活跃吧务队列的最前端，以响应holyshit指令
        """

        tb.log.info(f"{at.user.user_name}: {at.text} in tid:{at.tid}")

        user_id = at.user.user_id
        permission = await handler.admin.database.get_user_id(at.tieba_name, user_id)

        if await handler.admin.database.add_user_id(at.tieba_name, user_id, permission, "cmd active"):
            await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=1, need_arg_num=0)
    async def cmd_ping(self, handler: Handler, at: tb.At, *args) -> None:
        """
        ping指令
        用于测试bot可用性的空指令
        """

        tb.log.info(f"{at.user.user_name}: {at.text}")

        await handler.admin.del_post(at.tieba_name, at.tid, at.pid)

    @_check(need_access=129, need_arg_num=65536)
    async def cmd_default(self, handler: Handler, at: tb.At, *args) -> None:
        """
        default指令
        """

        await handler.speaker.add_post(at.tieba_name, at.tid, "关注嘉然顿顿解馋~")


if __name__ == '__main__':

    async def main():
        async with Listener() as listener:
            await listener.run()

    try:
        asyncio.run(main())
    except:
        pass
