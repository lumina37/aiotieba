# -*- coding:utf-8 -*-
import asyncio
import datetime
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


class Context(object):

    __slots__ = ['handler', 'at', 'this_permission', 'args', 'note']

    def __init__(self, handler: "Handler", at: tb.At, this_permission: int, args: list[str], note: str = '') -> None:
        self.handler = handler
        self.at = at
        self.this_permission = this_permission
        self.args = args
        self.note = note

    @property
    def tieba_name(self):
        return self.handler.tieba_name

    @property
    def tid(self):
        return self.at.tid

    @property
    def pid(self):
        return self.at.pid

    @property
    def text(self):
        return self.at.text

    @property
    def user_id(self):
        return self.at.user.user_id

    @property
    def log_name(self):
        return self.at.user.log_name


def check_permission(need_permission: int = 0, need_arg_num: int = 0) -> Callable:
    """
    装饰器实现鉴权和上下文包装

    Args:
        need_permission (int, optional): 需要的权限级别
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
            if not await handler.admin.database.ping():
                return
            if (this_permission := await handler.get_user_id(at.user.user_id)) < need_permission:
                return
            ctx = Context(handler, at, this_permission, args)
            return await func(self, ctx)

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

    async def add_user_id(self, user_id: int, permission: int, note: str) -> bool:
        """
        添加user_id

        Args:
            user_id (int): 用户的user_id
            permission (int): 权限级别
            note (str): 备注

        Returns:
            bool: 操作是否成功
        """

        return await self.admin.database.add_user_id(self.tieba_name, user_id, permission, note)

    async def del_user_id(self, user_id: int) -> bool:
        """
        删除user_id

        Args:
            user_id (int): 用户的user_id

        Returns:
            bool: 操作是否成功
        """

        return await self.admin.database.del_user_id(self.tieba_name, user_id)

    async def get_user_id(self, user_id: int) -> int:
        """
        获取user_id的权限级别

        Args:
            user_id (int): 用户的user_id

        Returns:
            int: 权限级别
        """

        return await self.admin.database.get_user_id(self.tieba_name, user_id)

    async def get_user_id_full(self, user_id: int) -> tuple[int, str, datetime.datetime]:
        """
        获取user_id的完整信息

        Args:
            user_id (int): 用户的user_id

        Returns:
            int: 权限级别
            str: 备注
            datetime.datetime: 记录时间
        """

        return await self.admin.database.get_user_id_full(self.tieba_name, user_id)


class Listener(object):

    __slots__ = ['listener', 'handler_map', '_cmd_map', 'time_recorder']

    def __init__(self) -> None:

        config_path = SCRIPT_PATH.parent / 'config/listen_config.json'
        with config_path.open('r', encoding='utf-8') as _file:
            config = json.load(_file)

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
                tb.log.critical("Unhandled error", exc_info=True)
                return

    async def scan(self) -> None:
        ats = await self.listener.get_ats()
        for end_idx, at in enumerate(ats):
            if not self.time_recorder.is_inrange(at.create_time):
                self.time_recorder.last_parse_time = ats[0].create_time
                ats = ats[:end_idx]
                break

        await asyncio.gather(*[asyncio.wait_for(self._handle_cmd(at), timeout=120) for at in ats],
                             return_exceptions=False)

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

        def _get_number(_str: str, _sign: str) -> int:
            if (first_sign := _str.find(_sign)) == -1:
                return 0
            if (last_sign := _str.rfind(_sign)) == -1:
                return 0
            sub_str = _str[first_sign + 1:last_sign]
            if not sub_str.isdigit():
                return 0
            return int(sub_str)

        if tieba_uid := _get_number(arg, '#'):
            user = await self.listener.tieba_uid2user_info(tieba_uid)
        elif user_id := _get_number(arg, '/'):
            user = await self.listener.get_basic_user_info(user_id)
        else:
            user = await self.listener.get_basic_user_info(arg)

        return user

    @check_permission(need_permission=0, need_arg_num=0)
    async def cmd_holyshit(self, ctx: Context) -> None:
        """
        holyshit指令
        召唤4名活跃吧务，使用参数extra_info来附带额外的召唤需求
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if not self.time_recorder.allow_execute():
            return

        active_admin_list = [
            (await self.listener.get_basic_user_info(user_id)).user_name
            for user_id in await ctx.handler.admin.database.get_user_id_list(ctx.tieba_name, limit=4, permission=2)
        ]
        extra_info = ctx.args[0] if len(ctx.args) else '无'
        content = f"该回复为吧务召唤指令@.v_guard holyshit的自动响应\n召唤人诉求：{extra_info}@" + " @".join(active_admin_list)

        if await ctx.handler.speaker.add_post(ctx.tieba_name, ctx.tid, content):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=1, need_arg_num=0)
    async def cmd_recommend(self, ctx: Context) -> None:
        """
        recommend指令
        对指令所在主题帖执行“大吧主首页推荐”操作
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.admin.recommend(ctx.tieba_name, ctx.tid):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=2, need_arg_num=1)
    async def cmd_move(self, ctx: Context) -> None:
        """
        move指令
        将指令所在主题帖移动至名为tab_name的分区
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if not (threads := await self.listener.get_threads(ctx.tieba_name)):
            return

        from_tab_id = 0
        for thread in threads:
            if thread.tid == ctx.tid:
                from_tab_id = thread.tab_id
        to_tab_id = threads.tab_map.get(ctx.args[0], 0)

        if await ctx.handler.admin.move(ctx.tieba_name, ctx.tid, to_tab_id, from_tab_id):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_good(self, ctx: Context) -> None:
        """
        good指令
        将指令所在主题帖加到以cname为名的精华分区。cname默认为''即不分区
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        cname = ctx.args[0] if len(ctx.args) else ''

        if await ctx.handler.admin.good(ctx.tieba_name, ctx.tid, cname):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_ungood(self, ctx: Context) -> None:
        """
        ungood指令
        撤销指令所在主题帖的精华
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.admin.ungood(ctx.tieba_name, ctx.tid):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=4, need_arg_num=0)
    async def cmd_top(self, ctx: Context) -> None:
        """
        top指令
        置顶指令所在主题帖
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.admin.top(ctx.tieba_name, ctx.tid):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=4, need_arg_num=0)
    async def cmd_untop(self, ctx: Context) -> None:
        """
        untop指令
        撤销指令所在主题帖的置顶
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.admin.untop(ctx.tieba_name, ctx.tid):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_hide(self, ctx: Context) -> None:
        """
        hide指令
        屏蔽指令所在主题帖
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.admin.hide_thread(ctx.tieba_name, ctx.tid):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_unhide(self, ctx: Context) -> None:
        """
        unhide指令
        解除指令所在主题帖的屏蔽
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.admin.unhide_thread(ctx.tieba_name, ctx.tid):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_delete(self, ctx: Context) -> None:
        """
        delete指令
        删帖
        """

        await self._delete(ctx)

    @check_permission(need_permission=2, need_arg_num=1)
    async def cmd_block(self, ctx: Context) -> None:
        """
        block指令
        通过id封禁对应用户10天
        """

        ctx.note = ctx.args[1] if len(ctx.args) >= 2 else f"cmd block by {ctx.user_id}"
        await self._block(ctx, 10)

    @check_permission(need_permission=2, need_arg_num=1)
    async def cmd_block3(self, ctx: Context) -> None:
        """
        block3指令
        通过id封禁对应用户3天
        """

        ctx.note = ctx.args[1] if len(ctx.args) >= 2 else f"cmd block3 by {ctx.user_id}"
        await self._block(ctx, 3)

    @check_permission(need_permission=2, need_arg_num=1)
    async def cmd_block1(self, ctx: Context) -> None:
        """
        block1指令
        通过id封禁对应用户1天
        """

        ctx.note = ctx.args[1] if len(ctx.args) >= 2 else f"cmd block1 by {ctx.user_id}"
        await self._block(ctx, 1)

    async def _block(self, ctx: Context, block_days: int) -> None:
        """
        block & block3指令的实现
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        user = await self._arg2user_info(ctx.args[0])

        if await ctx.handler.admin.block(ctx.tieba_name, user, block_days, ctx.note):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=2, need_arg_num=1)
    async def cmd_unblock(self, ctx: Context) -> None:
        """
        unblock指令
        通过id解封用户
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        user = await self._arg2user_info(ctx.args[0])

        if await ctx.handler.admin.unblock(ctx.tieba_name, user):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_drop(self, ctx: Context) -> None:
        """
        drop指令
        删帖并封10天
        """

        ctx.note = ctx.args[0] if len(ctx.args) >= 1 else f"cmd drop by {ctx.user_id}"
        await self._delete(ctx, 10)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_drop3(self, ctx: Context) -> None:
        """
        drop3指令
        删帖并封3天
        """

        ctx.note = ctx.args[0] if len(ctx.args) >= 1 else f"cmd drop3 by {ctx.user_id}"
        await self._delete(ctx, 3)

    @check_permission(need_permission=4, need_arg_num=1)
    async def cmd_black(self, ctx: Context) -> None:
        """
        black指令
        将id加入脚本黑名单
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        user = await self._arg2user_info(ctx.args[0])
        if await ctx.handler.get_user_id(user.user_id) >= ctx.this_permission:
            return
        ctx.note = ctx.args[1] if len(ctx.args) >= 2 else f"cmd black by {ctx.user_id}"

        tb.log.info(f"Try to black {user.log_name} in {ctx.tieba_name}")

        if await ctx.handler.add_user_id(user.user_id, -5, ctx.note):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=3, need_arg_num=1)
    async def cmd_white(self, ctx: Context) -> None:
        """
        white指令
        将id加入脚本白名单
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        user = await self._arg2user_info(ctx.args[0])
        if await ctx.handler.get_user_id(user.user_id) >= ctx.this_permission:
            return
        ctx.note = ctx.args[1] if len(ctx.args) >= 2 else f"cmd white by {ctx.user_id}"

        tb.log.info(f"Try to white {user.log_name} in {ctx.tieba_name}")

        if await ctx.handler.add_user_id(user.user_id, 1, ctx.note):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=3, need_arg_num=1)
    async def cmd_reset(self, ctx: Context) -> None:
        """
        reset指令
        将id移出脚本名单
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        user = await self._arg2user_info(ctx.args[0])
        if await ctx.handler.get_user_id(user.user_id) >= ctx.this_permission:
            return

        tb.log.info(f"Try to reset {user.log_name} in {ctx.tieba_name}")

        if await ctx.handler.del_user_id(user.user_id):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=4, need_arg_num=0)
    async def cmd_exdrop(self, ctx: Context) -> None:
        """
        exdrop指令
        删帖并将发帖人加入脚本黑名单+封禁十天
        """

        ctx.note = ctx.args[0] if len(ctx.args) >= 1 else f"cmd exdrop by {ctx.user_id}"
        await self._delete(ctx, 10, blacklist=True)

    async def _delete(self, ctx: Context, block_days: int = 0, blacklist: bool = False):
        """
        各种处罚指令的实现
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        coros = []

        if ctx.at.is_floor:
            if not (comments := await self.listener.get_comments(ctx.tid, ctx.pid, is_floor=True)):
                return
            target = comments.post
            tb.log.info(f"Try to delete post {target.text} post by {target.user.log_name}")
            coros.append(ctx.handler.admin.del_post(ctx.tieba_name, target.tid, target.pid))

        else:
            if not (posts := await self.listener.get_posts(ctx.tid, rn=0)):
                return

            if ctx.at.is_thread:
                if posts.forum.fid != (target := posts.thread.share_origin).fid:
                    return
                target = posts.thread.share_origin
                if not target.contents.ats:
                    return
                target.user = await self.listener.get_basic_user_info(target.contents.ats[0].user_id)
                tb.log.info(f"Try to delete thread {target.text} post by {target.user.log_name}")
                coros.append(ctx.handler.admin.del_thread(ctx.tieba_name, target.tid))

            else:
                target = posts[0]
                tb.log.info(f"Try to delete thread {target.text} post by {target.user.log_name}")
                coros.append(ctx.handler.admin.del_thread(ctx.tieba_name, target.tid))

        if block_days:
            coros.append(ctx.handler.admin.block(ctx.tieba_name, target.user, block_days, ctx.note))
        if blacklist:
            if await ctx.handler.get_user_id(target.user.user_id) < ctx.this_permission:
                tb.log.info(f"Try to black {target.user.log_name} in {ctx.tieba_name}")
                coros.append(ctx.handler.add_user_id(target.user.user_id, -5, ctx.note))

        await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)
        await asyncio.gather(*coros)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_refuse_appeals(self, ctx: Context) -> None:
        """
        refuse_appeals指令
        一键拒绝所有解封申诉
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.admin.refuse_appeals(ctx.tieba_name):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=4, need_arg_num=2)
    async def cmd_set(self, ctx: Context) -> None:
        """
        set指令
        设置用户的权限级别
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        user = await self._arg2user_info(ctx.args[0])
        if not user.user_id:
            return
        new_permission = int(ctx.args[1])
        ctx.note = ctx.args[2] if len(ctx.args) >= 3 else f"cmd set by {ctx.user_id}"

        old_permission = await ctx.handler.get_user_id(user.user_id)
        if old_permission >= ctx.this_permission or new_permission >= ctx.this_permission:
            return

        if await ctx.handler.add_user_id(user.user_id, new_permission, ctx.note):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=1, need_arg_num=1)
    async def cmd_get(self, ctx: Context) -> None:
        """
        get指令
        获取用户的个人信息与标记信息
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        user = await self._arg2user_info(ctx.args[0])
        if not user.user_id:
            return

        permission, note, record_time = await ctx.handler.get_user_id_full(user.user_id)
        content = f"""@{ctx.at.user.user_name} \nuser_name: {user.user_name}\nuser_id: {user.user_id}\nportrait: {user.portrait}\npermission: {permission}\nnote: {note}\nrecord_time: {record_time.strftime("%Y-%m-%d %H:%M:%S")}"""

        if await ctx.handler.speaker.add_post(ctx.tieba_name, ctx.tid, content):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=0, need_arg_num=0)
    async def cmd_register(self, ctx: Context) -> None:
        """
        register指令
        通过精品帖自助获取1级权限
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if ctx.this_permission == 0:
            for thread in await self.listener.get_threads(ctx.tieba_name, is_good=True):
                if thread.user.user_id == ctx.user_id and thread.create_time > time.time() - 30 * 24 * 3600:
                    if await ctx.handler.add_user_id(ctx.user_id, 1, "cmd register"):
                        await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=1, need_arg_num=0)
    async def cmd_recom_status(self, ctx: Context) -> None:
        """
        recom_status指令
        获取大吧主推荐功能的月度配额状态
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if not self.time_recorder.allow_execute():
            return

        total_recom_num, used_recom_num = await ctx.handler.admin.get_recom_status(ctx.tieba_name)
        content = f"@{ctx.at.user.user_name} \nUsed: {used_recom_num} / {total_recom_num} = {used_recom_num/total_recom_num*100:.2f}%"

        if await ctx.handler.speaker.add_post(ctx.tieba_name, ctx.tid, content):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=1, need_arg_num=2)
    async def cmd_vote_stat(self, ctx: Context) -> None:
        """
        vote_stat指令
        统计投票结果
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if not ctx.args[1].isdigit():
            return
        if not self.time_recorder.allow_execute():
            return

        async def _stat_pn(pn: int) -> None:
            """
            统计主题帖第pn页的投票结果

            Args:
                pn (int): 页码
            """

            posts = await self.listener.get_posts(ctx.tid,
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
                    if ctx.args[0] in text:
                        vote_set.add(comment.user.user_id)

                if not comments.has_more:
                    break

            if (vote_num := len(vote_set)):
                results.append((post.floor, vote_num))

        results = []
        posts = await self.listener.get_posts(ctx.tid, 1, with_comments=True, comment_sort_by_agree=False)
        await asyncio.gather(*[_stat_post(post) for post in posts[1:]])

        if (total_page := posts.page.total_page) > 1:
            await asyncio.gather(*[_stat_pn(pn) for pn in range(2, total_page + 1)], return_exceptions=True)

        results.sort(key=lambda result: result[1], reverse=True)
        contents = [f"@{ctx.at.user.user_name} "]
        contents.extend([f"floor:{floor} num:{vote_num}" for floor, vote_num in results[:int(ctx.args[1])]])
        content = '\n'.join(contents)

        if await ctx.handler.speaker.add_post(ctx.tieba_name, ctx.tid, content):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=4, need_arg_num=1)
    async def cmd_tb_black(self, ctx: Context) -> None:
        """
        tb_black指令
        将id加入贴吧黑名单
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        user = await self._arg2user_info(ctx.args[0])

        if await ctx.handler.admin.blacklist_add(ctx.tieba_name, user):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=3, need_arg_num=1)
    async def cmd_tb_reset(self, ctx: Context) -> None:
        """
        tb_reset指令
        将id移出贴吧黑名单
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        user = await self._arg2user_info(ctx.args[0])

        if await ctx.handler.admin.blacklist_del(ctx.tieba_name, user):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_water(self, ctx: Context) -> None:
        """
        water指令
        将指令所在主题帖标记为无关水，并临时屏蔽
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.admin.database.add_tid(
                ctx.tieba_name, ctx.tid, True) and await ctx.handler.admin.hide_thread(ctx.tieba_name, ctx.tid):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_unwater(self, ctx: Context) -> None:
        """
        unwater指令
        清除指令所在主题帖的无关水标记，并立刻解除屏蔽
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.admin.database.del_tid(ctx.tieba_name, ctx.tid) and await ctx.handler.admin.unhide_thread(
                ctx.tieba_name, ctx.tid):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=3, need_arg_num=1)
    async def cmd_water_restrict(self, ctx: Context) -> None:
        """
        water_restrict指令
        控制当前吧的云审查脚本的无关水管控状态
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if ctx.args[0] == "enter":
            if await ctx.handler.admin.database.add_tid(ctx.tieba_name, 0, True):
                await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)
        elif ctx.args[0] == "exit":
            if await ctx.handler.admin.database.add_tid(ctx.tieba_name, 0, False):
                await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)
            async for tid in ctx.handler.admin.database.get_tids(ctx.tieba_name):
                if await ctx.handler.admin.unhide_thread(ctx.tieba_name, tid):
                    await ctx.handler.admin.database.add_tid(ctx.tieba_name, tid, False)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_active(self, ctx: Context) -> None:
        """
        active指令
        将发起指令的吧务移动到活跃吧务队列的最前端，以响应holyshit指令
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.add_user_id(ctx.user_id, ctx.this_permission, "cmd active"):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=1, need_arg_num=0)
    async def cmd_ping(self, ctx: Context) -> None:
        """
        ping指令
        用于测试bot可用性的空指令
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=129, need_arg_num=65536)
    async def cmd_default(self, ctx: Context) -> None:
        """
        default指令
        """

        await ctx.handler.speaker.add_post(ctx.tieba_name, ctx.tid, "关注嘉然顿顿解馋~")


if __name__ == '__main__':

    async def main():
        async with Listener() as listener:
            await listener.run()

    try:
        asyncio.run(main())
    except BaseException:
        pass
