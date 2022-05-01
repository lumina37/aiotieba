# -*- coding:utf-8 -*-
import asyncio
import functools
import json
import re
import time
from collections.abc import Callable

import tiebaBrowser as tb
from tiebaBrowser._config import SCRIPT_PATH

with (SCRIPT_PATH.parent / 'config/listen_config.json').open('r', encoding='utf-8') as _file:
    LISTEN_CONFIG = json.load(_file)


class TimerRecorder(object):
    """
    时间记录器

    Args:
        shift_sec: int 启动时允许解析shift_sec秒之前的at
        post_interval: int 两次post_add之间需要的时间间隔

    Fields:
        last_parse_time: int 上次解析at信息的时间(以百度服务器为准)
        last_post_time: int 上次发送回复的时间(以百度服务器为准)
        post_interval: int 两次post_add之间需要的时间间隔
    """

    __slots__ = ['last_parse_time', 'last_post_time', 'post_interval']

    def __init__(self, shift_sec: int, post_interval: int) -> None:

        self.last_post_time: int = 0
        self.post_interval: int = post_interval
        self.last_parse_time: int = int(time.time()) - shift_sec

    def is_inrange(self, check_time: int) -> bool:
        return self.last_parse_time < check_time

    def allow_execute(self) -> bool:
        current_time = time.time()
        if current_time - self.last_post_time > self.post_interval:
            self.last_post_time = current_time
            return True
        else:
            return False


class Context(object):

    __slots__ = ['at', 'handler', '_full_init', '_args', '_cmd_type', 'this_permission', 'parent', 'note']

    def __init__(self, at: tb.At) -> None:
        self.at: tb.At = at
        self.handler: "Handler" = None
        self._full_init: bool = False
        self._args = None
        self._cmd_type = None
        self.this_permission: int = 0
        self.parent: tb.Thread | tb.Post = None
        self.note: str = ''

    async def _init(self) -> bool:
        handler = self.handler
        if not handler:
            return False

        self.this_permission = await handler.admin.get_user_id(self.user_id)
        if len(self.at.text.encode('utf-8')) >= 70:
            await self._init_full()

        self._init_args()
        return True

    async def _init_full(self) -> bool:

        if self._full_init:
            return True

        if self.at.is_floor:
            await asyncio.sleep(1.5)
            comments = await self.handler.admin.get_comments(self.tid, self.pid, is_floor=True)
            if not comments:
                return False
            self.parent = comments.post
            for comment in comments:
                if comment.pid == self.pid:
                    self.at._text = comment.text

        else:
            if self.at.is_thread:
                await asyncio.sleep(3)
                posts = await self.handler.admin.get_posts(self.tid, pn=-1, rn=0, sort=1)
                if not posts:
                    return False
                self.parent = posts.thread.share_origin
                self.at._text = posts.thread.text

            else:
                posts = await self.handler.admin.get_posts(self.tid, pn=-1, rn=10, sort=1)
                if not posts:
                    return False
                for post in posts:
                    if post.pid == self.pid:
                        self.at._text = post.text
                        break
                posts = await self.handler.admin.get_posts(self.tid, rn=0)
                if not posts:
                    return False
                self.parent = posts[0]

        self._full_init = True
        return True

    def _init_args(self):
        text = self.at.text
        self._args = []
        self._cmd_type = ''

        if (first_blank_idx := text.find(' ', text.find('@') + 1)) == -1:
            return

        text = text[first_blank_idx + 1 :]
        self._args = [arg.lstrip(' ') for arg in text.split(' ') if arg]
        if self._args:
            self._cmd_type = self._args[0]
            self._args = self._args[1:]

    @property
    def cmd_type(self) -> str:
        if self._cmd_type is None:
            self._init_args()
        return self._cmd_type

    @property
    def args(self) -> list[str]:
        if self._args is None:
            self._init_args()
        return self._args

    @property
    def tieba_name(self):
        return self.at.tieba_name

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
    装饰器实现鉴权和参数数量检查

    Args:
        need_permission (int, optional): 需要的权限级别
        need_arg_num (bool, optional): 需要的参数数量
    """

    def wrapper(func) -> Callable:
        @functools.wraps(func)
        async def foo(self: "Listener", ctx: Context):
            if len(ctx.args) < need_arg_num:
                return
            if ctx.this_permission < need_permission:
                return
            return await func(self, ctx)

        return foo

    return wrapper


class Handler(object):

    __slots__ = ['tieba_name', 'admin', 'speaker']

    def __init__(self, tieba_name: str, admin_key: str, speaker_key: str) -> None:
        self.tieba_name = tieba_name
        self.admin = tb.Reviewer(admin_key, self.tieba_name)
        self.speaker = tb.Browser(speaker_key)

    async def enter(self) -> None:
        await asyncio.gather(self.admin.enter(), self.speaker.enter())

    async def close(self):
        await asyncio.gather(self.admin.close(), self.speaker.close(), return_exceptions=True)


class Listener(object):

    __slots__ = ['listener', 'handlers', 'time_recorder']

    def __init__(self) -> None:

        self.handlers = {
            (handler := Handler(**tieba_config)).tieba_name: handler for tieba_config in LISTEN_CONFIG['tieba_configs']
        }

        self.listener = tb.Reviewer(LISTEN_CONFIG['listener_key'], '')

        self.time_recorder = TimerRecorder(3600, 10)

    async def close(self) -> None:
        await asyncio.gather(
            *[handler.close() for handler in self.handlers.values()], self.listener.close(), return_exceptions=True
        )

    async def __aenter__(self) -> "Listener":
        coros = [handler.enter() for handler in self.handlers.values()]
        await asyncio.gather(*coros, self.listener.enter())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def run(self) -> None:

        while 1:
            try:
                asyncio.create_task(self._fetch_and_execute_cmds())
                tb.log.debug('heartbeat')
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                break
            except Exception:
                tb.log.critical("Unhandled error", exc_info=True)
                return

    async def _fetch_and_execute_cmds(self) -> None:
        ats = await self.listener.get_ats()

        for end_idx, at in enumerate(ats):
            if not self.time_recorder.is_inrange(at.create_time):
                ats = ats[:end_idx]
                break

        if ats:
            self.time_recorder.last_parse_time = ats[0].create_time
            await asyncio.gather(*[asyncio.wait_for(self._execute_cmd(at), timeout=120) for at in ats])

    async def _execute_cmd(self, at: tb.At) -> None:
        ctx = Context(at)

        ctx.handler = self.handlers.get(ctx.tieba_name, None)
        if not ctx.handler:
            return

        if not await ctx._init():
            return

        cmd_func = getattr(self, f'cmd_{ctx.cmd_type}', self.cmd_default)
        await cmd_func(ctx)

    async def _arg2user_info(self, arg: str) -> tb.UserInfo:
        def _get_num_between_two_signs(_str: str, _sign: str) -> int:
            if (first_sign := _str.find(_sign)) == -1:
                return 0
            if (last_sign := _str.rfind(_sign)) == -1:
                return 0
            sub_str = _str[first_sign + 1 : last_sign]
            if not sub_str.isdecimal():
                return 0
            return int(sub_str)

        if tieba_uid := _get_num_between_two_signs(arg, '#'):
            user = await self.listener.tieba_uid2user_info(tieba_uid)
        elif user_id := _get_num_between_two_signs(arg, '/'):
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
            for user_id in await ctx.handler.admin.get_user_id_list(limit=4, permission=2)
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

        await self._block(ctx, 10)

    @check_permission(need_permission=2, need_arg_num=1)
    async def cmd_block3(self, ctx: Context) -> None:
        """
        block3指令
        通过id封禁对应用户3天
        """

        await self._block(ctx, 3)

    @check_permission(need_permission=2, need_arg_num=1)
    async def cmd_block1(self, ctx: Context) -> None:
        """
        block1指令
        通过id封禁对应用户1天
        """

        await self._block(ctx, 1)

    async def _block(self, ctx: Context, block_days: int) -> None:
        """
        block & block3指令的实现
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")
        ctx.note = ctx.args[1] if len(ctx.args) >= 2 else f"cmd {ctx.cmd_type} by {ctx.user_id}"

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

        await self._delete(ctx, 10)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_drop3(self, ctx: Context) -> None:
        """
        drop3指令
        删帖并封3天
        """

        await self._delete(ctx, 3)

    @check_permission(need_permission=4, need_arg_num=1)
    async def cmd_black(self, ctx: Context) -> None:
        """
        black指令
        将id加入脚本黑名单
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        user = await self._arg2user_info(ctx.args[0])
        if await ctx.handler.admin.get_user_id(user.user_id) >= ctx.this_permission:
            return
        ctx.note = ctx.args[1] if len(ctx.args) >= 2 else f"cmd black by {ctx.user_id}"

        tb.log.info(f"Try to black {user.log_name} in {ctx.tieba_name}")

        if await ctx.handler.admin.add_user_id(user.user_id, -5, ctx.note):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=3, need_arg_num=1)
    async def cmd_white(self, ctx: Context) -> None:
        """
        white指令
        将id加入脚本白名单
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        user = await self._arg2user_info(ctx.args[0])
        if await ctx.handler.admin.get_user_id(user.user_id) >= ctx.this_permission:
            return
        ctx.note = ctx.args[1] if len(ctx.args) >= 2 else f"cmd white by {ctx.user_id}"

        tb.log.info(f"Try to white {user.log_name} in {ctx.tieba_name}")

        if await ctx.handler.admin.add_user_id(user.user_id, 1, ctx.note):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=3, need_arg_num=1)
    async def cmd_reset(self, ctx: Context) -> None:
        """
        reset指令
        将id移出脚本名单
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        user = await self._arg2user_info(ctx.args[0])
        if await ctx.handler.admin.get_user_id(user.user_id) >= ctx.this_permission:
            return

        tb.log.info(f"Try to reset {user.log_name} in {ctx.tieba_name}")

        if await ctx.handler.admin.del_user_id(user.user_id):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=4, need_arg_num=0)
    async def cmd_exdrop(self, ctx: Context) -> None:
        """
        exdrop指令
        删帖并将发帖人加入脚本黑名单+封禁十天
        """

        await self._delete(ctx, 10, blacklist=True)

    async def _delete(self, ctx: Context, block_days: int = 0, blacklist: bool = False):
        """
        各种处罚指令的实现
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")
        ctx.note = ctx.args[0] if len(ctx.args) >= 1 else f"cmd {ctx.cmd_type} by {ctx.user_id}"

        coros = []
        await ctx._init_full()

        if ctx.at.is_floor:
            tb.log.info(f"Try to delete post {ctx.parent.text} post by {ctx.parent.user.log_name}")
            coros.append(ctx.handler.admin.del_post(ctx.tieba_name, ctx.parent.tid, ctx.parent.pid))

        else:
            if ctx.at.is_thread:
                if (await self.listener.get_fid(ctx.tieba_name)) != ctx.parent.fid:
                    return
                if not ctx.parent.contents.ats:
                    return
                ctx.parent.user = await self.listener.get_basic_user_info(ctx.parent.contents.ats[0].user_id)
                tb.log.info(f"Try to delete thread {ctx.parent.text} post by {ctx.parent.user.log_name}")
                coros.append(ctx.handler.admin.del_thread(ctx.tieba_name, ctx.parent.tid))

            else:
                tb.log.info(f"Try to delete thread {ctx.parent.text} post by {ctx.parent.user.log_name}")
                coros.append(ctx.handler.admin.del_thread(ctx.tieba_name, ctx.parent.tid))

        if block_days:
            coros.append(ctx.handler.admin.block(ctx.tieba_name, ctx.parent.user, block_days, ctx.note))
        if blacklist:
            if await ctx.handler.admin.get_user_id(ctx.parent.user.user_id) < ctx.this_permission:
                tb.log.info(f"Try to black {ctx.parent.user.log_name} in {ctx.tieba_name}")
                coros.append(ctx.handler.admin.add_user_id(ctx.parent.user.user_id, -5, ctx.note))

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

        old_permission = await ctx.handler.admin.get_user_id(user.user_id)
        if old_permission >= ctx.this_permission or new_permission >= ctx.this_permission:
            return

        if await ctx.handler.admin.add_user_id(user.user_id, new_permission, ctx.note):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=0, need_arg_num=1)
    async def cmd_get(self, ctx: Context) -> None:
        """
        get指令
        获取用户的个人信息与标记信息
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if not self.time_recorder.allow_execute():
            return
        user = await self._arg2user_info(ctx.args[0])
        if not user.user_id:
            return

        permission, note, record_time = await ctx.handler.admin.get_user_id_full(user.user_id)
        content = f"""@{ctx.at.user.user_name} \nuser_name: {user.user_name}\nuser_id: {user.user_id}\nportrait: {user.portrait}\npermission: {permission}\nnote: {note}\nrecord_time: {record_time.strftime("%Y-%m-%d %H:%M:%S")}"""

        if await ctx.handler.speaker.add_post(ctx.tieba_name, ctx.tid, content):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=4, need_arg_num=2)
    async def cmd_img_set(self, ctx: Context) -> None:
        """
        img_set指令
        设置图片的封锁级别
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        if len(ctx.args) > 2:
            index = int(ctx.args[0]) - 1
            permission = int(ctx.args[1])
            note = ctx.args[2]
        else:
            index = 0
            permission = int(ctx.args[0])
            note = ctx.args[1]

        await ctx._init_full()
        if not (imgs := ctx.parent.contents.imgs):
            return

        if index > len(imgs) - 1:
            return
        image = await self.listener.get_image(imgs[index].src)
        if image is None:
            return
        img_hash = self.listener.compute_imghash(image)

        if await ctx.handler.admin.database.add_imghash(ctx.tieba_name, img_hash, imgs[index].hash, permission, note):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=3, need_arg_num=0)
    async def cmd_img_reset(self, ctx: Context) -> None:
        """
        img_reset指令
        重置图片的封锁级别
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text}")

        if ctx.args:
            index = int(ctx.args[0]) - 1
        else:
            index = 0

        await ctx._init_full()
        if not (imgs := ctx.parent.contents.imgs):
            return

        if index > len(imgs) - 1:
            return
        image = await self.listener.get_image(imgs[index].src)
        if image is None:
            return
        img_hash = self.listener.compute_imghash(image)

        if await ctx.handler.admin.database.del_imghash(ctx.tieba_name, img_hash):
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
                    if await ctx.handler.admin.add_user_id(ctx.user_id, 1, "cmd register"):
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

        if not ctx.args[1].isdecimal():
            return
        keyword = ctx.args[0]
        limit = int(ctx.args[1])
        min_level = int(ctx.args[2]) if len(ctx.args) > 2 and ctx.args[2].isdecimal() else 0
        if not self.time_recorder.allow_execute():
            return

        async def _stat_pn(pn: int) -> None:
            """
            统计主题帖第pn页的投票结果

            Args:
                pn (int): 页码
            """

            posts = await self.listener.get_posts(
                ctx.tid, pn, only_thread_author=True, with_comments=True, comment_sort_by_agree=True
            )
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
                    if comment.user.level >= min_level and keyword in text:
                        vote_set.add(comment.user.user_id)

                if not comments.has_more:
                    break

            if vote_num := len(vote_set):
                results.append((post.floor, vote_num))

        results = []
        posts = await self.listener.get_posts(ctx.tid, 1, with_comments=True, comment_sort_by_agree=False)
        await asyncio.gather(*[_stat_post(post) for post in posts[1:]])

        if (total_page := posts.page.total_page) > 1:
            await asyncio.gather(*[_stat_pn(pn) for pn in range(2, total_page + 1)], return_exceptions=True)

        results.sort(key=lambda result: result[1], reverse=True)
        contents = [f"@{ctx.at.user.user_name} ", f"keyword:{keyword}", f"min_level:{min_level}"]
        contents.extend([f"floor:{floor} num:{vote_num}" for floor, vote_num in results[:limit]])
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

        if await ctx.handler.admin.add_tid(ctx.tid, True) and await ctx.handler.admin.hide_thread(
            ctx.tieba_name, ctx.tid
        ):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_unwater(self, ctx: Context) -> None:
        """
        unwater指令
        清除指令所在主题帖的无关水标记，并立刻解除屏蔽
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.admin.del_tid(ctx.tid) and await ctx.handler.admin.unhide_thread(ctx.tieba_name, ctx.tid):
            await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)

    @check_permission(need_permission=3, need_arg_num=1)
    async def cmd_water_restrict(self, ctx: Context) -> None:
        """
        water_restrict指令
        控制当前吧的云审查脚本的无关水管控状态
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if ctx.args[0] == "enter":
            if await ctx.handler.admin.add_tid(0, True):
                await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)
        elif ctx.args[0] == "exit":
            if await ctx.handler.admin.add_tid(0, False):
                await ctx.handler.admin.del_post(ctx.tieba_name, ctx.tid, ctx.pid)
            limit = 128
            tids = await ctx.handler.admin.get_tid_list(limit=limit)
            while 1:
                for tid in tids:
                    if await ctx.handler.admin.unhide_thread(ctx.tieba_name, tid):
                        await ctx.handler.admin.add_tid(tid, False)
                if len(tids) != limit:
                    break

    @check_permission(need_permission=2, need_arg_num=0)
    async def cmd_active(self, ctx: Context) -> None:
        """
        active指令
        将发起指令的吧务移动到活跃吧务队列的最前端，以响应holyshit指令
        """

        tb.log.info(f"{ctx.log_name}: {ctx.text} in tid:{ctx.tid}")

        if await ctx.handler.admin.add_user_id(ctx.user_id, ctx.this_permission, "cmd active"):
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

        if not self.time_recorder.allow_execute():
            return

        await ctx.handler.speaker.add_post(ctx.tieba_name, ctx.tid, "关注嘉然顿顿解馋~")


if __name__ == '__main__':

    async def main():
        async with Listener() as listener:
            await listener.run()

    try:
        asyncio.run(main())
    except BaseException:
        pass
