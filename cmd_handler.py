"""
指令管理器
使用前请在当前工作目录下新建cmd_handler.toml配置文件，并参考下列案例填写你自己的配置

--------
listener_key = "listener"  # 在这里填用于监听at信息的账号的BDUSS_key

[[Configs]]
fname = "lol半价"  # 在这里填贴吧名
admin_key = "default"  # 在这里填用于在该吧行使吧务权限的账号的BDUSS_key
speaker_key = "default"  # 在这里填用于在该吧发送回复的账号的BDUSS_key

[[Configs]]
fname = "asoul"  # 在这里填另一个贴吧名
admin_key = "default"  # 在这里填用于在该吧行使吧务权限的账号的BDUSS_key
speaker_key = "default"  # 在这里填用于在该吧发送回复的账号的BDUSS_key
"""

import asyncio
import functools
import itertools
import time
from collections.abc import Callable
from typing import Dict, List, Optional, Tuple, Union

import tomli

import aiotieba as tb

with open("cmd_handler.toml", 'rb') as file:
    LISTEN_CONFIG = tomli.load(file)


class TimerRecorder(object):
    """
    时间记录器

    Args:
        shift_sec (float): 启动时允许解析shift_sec秒之前的at
        post_interval (float): 两次post_add之间需要的间隔秒数

    Attributes:
        last_parse_time (float): 上次解析at信息的时间(以百度服务器为准)
        last_post_time (float): 上次发送回复的时间(以百度服务器为准)
        post_interval (float): 两次post_add之间需要的时间间隔
    """

    __slots__ = ['last_parse_time', 'last_post_time', 'post_interval']

    def __init__(self, shift_sec: float, post_interval: float) -> None:

        self.last_post_time: float = 0
        self.post_interval: float = post_interval
        self.last_parse_time: float = time.time() - shift_sec

    def is_inrange(self, check_time: int) -> bool:
        return self.last_parse_time < check_time

    def allow_execute(self) -> bool:
        current_time = time.time()

        if current_time - self.last_post_time > self.post_interval:
            self.last_post_time = current_time
            return True

        return False


class Context(object):

    __slots__ = [
        'at',
        'admin',
        'speaker',
        '_init_full_success',
        '_args',
        '_cmd_type',
        '_note',
        'exec_permission',
        'parent',
    ]

    def __init__(self, at: tb.At) -> None:
        self.at: tb.At = at
        self.admin: tb.Reviewer = None
        self.speaker: tb.Client = None
        self._init_full_success: bool = False
        self._args = None
        self._cmd_type = None
        self._note = None
        self.exec_permission: int = 0
        self.parent: Union[tb.ShareThread, tb.Thread, tb.Post] = None

    async def _init(self) -> bool:
        self.exec_permission = await self.admin.get_user_id(self.user.user_id)
        if len(self.at.text.encode('utf-8')) >= 78:
            await self._init_full()

        self._init_args()
        return True

    async def _init_full(self) -> bool:

        if self._init_full_success:
            return True

        if self.at.is_floor:
            await asyncio.sleep(1.5)
            comments = await self.admin.get_comments(self.tid, self.pid, is_floor=True)
            self.parent = comments.post
            if not comments:
                return False
            for comment in comments:
                if comment.pid == self.pid:
                    self.at._text = comment.text

        else:
            if self.at.is_thread:
                await asyncio.sleep(3)
                posts = await self.admin.get_posts(self.tid, pn=-1, rn=0, sort=1)
                if not posts:
                    return False
                self.parent = posts.thread.share_origin
                self.at._text = posts.thread.text

            else:
                posts = await self.admin.get_posts(self.tid, pn=-1, rn=10, sort=1)
                if not posts:
                    return False
                for post in posts:
                    if post.pid == self.pid:
                        self.at._text = post.text
                        break
                posts = await self.admin.get_posts(self.tid, rn=0)
                if not posts:
                    return False
                self.parent = posts[0]

        self._init_full_success = True
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
    def fname(self):
        return self.at.fname

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
    def user(self) -> tb.UserInfo:
        return self.at.user

    @property
    def note(self) -> str:
        if self._note is None:
            self._note = f"cmd_{self.cmd_type}_by_{self.user.user_id}"
        return self._note


_TypeCommandFunc = Callable[["Listener", Context], None]


def check_and_log(need_permission: int = 0, need_arg_num: int = 0) -> _TypeCommandFunc:
    """
    装饰器实现鉴权和参数数量检查

    Args:
        need_permission (int, optional): 需要的权限级别
        need_arg_num (bool, optional): 需要的参数数量
    """

    def wrapper(func: _TypeCommandFunc) -> _TypeCommandFunc:
        @functools.wraps(func)
        async def _(self: "Listener", ctx: Context) -> None:

            tb.LOG.info(f"user={ctx.user} type={ctx.cmd_type} args={ctx.args} tid={ctx.tid}")

            try:
                if len(ctx.args) < need_arg_num:
                    raise ValueError("参数量不足")
                if ctx.exec_permission < need_permission:
                    raise ValueError("权限不足")

                await func(self, ctx)

            except Exception as err:
                tb.LOG.error(err)

        return _

    return wrapper


class Listener(object):

    __slots__ = ['listener', 'admins', 'time_recorder']

    def __init__(self) -> None:

        self.listener = tb.Reviewer(LISTEN_CONFIG['listener_key'])

        def _parse_config(_config: Dict[str, str]) -> Tuple[str, tb.Reviewer, tb.Client]:
            fname = _config['fname']
            admin = tb.Reviewer(_config['admin_key'], fname)
            speaker = tb.Client(_config['speaker_key'])
            return fname, admin, speaker

        self.admins = {
            fname: (admin, speaker) for fname, admin, speaker in map(_parse_config, LISTEN_CONFIG['Configs'])
        }

        self.time_recorder = TimerRecorder(86400, 10)

    async def close(self) -> None:
        await asyncio.gather(
            *[client.close() for client in itertools.chain.from_iterable(self.admins.values())], self.listener.close()
        )

    async def __aenter__(self) -> "Listener":
        await asyncio.gather(
            *[client.enter() for client in itertools.chain.from_iterable(self.admins.values())], self.listener.enter()
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def run(self) -> None:

        while 1:
            try:
                asyncio.create_task(self._fetch_and_execute_cmds())
                tb.LOG.debug('heartbeat')
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                return
            except Exception:
                tb.LOG.critical("Unhandled error", exc_info=True)
                return

    async def _fetch_and_execute_cmds(self) -> None:
        ats = await self.listener.client.get_ats()

        for end_idx, at in enumerate(ats):
            if not self.time_recorder.is_inrange(at.create_time):
                ats = ats[:end_idx]
                break

        if ats:
            self.time_recorder.last_parse_time = ats[0].create_time
            await asyncio.gather(*[asyncio.wait_for(self._execute_cmd(at), timeout=120) for at in ats])

    async def _execute_cmd(self, at: tb.At) -> None:
        ctx = Context(at)
        ctx.admin, ctx.speaker = self.admins.get(ctx.fname, (None, None))
        if ctx.admin is None:
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
            user = await self.listener.client.tieba_uid2user_info(tieba_uid)
        elif user_id := _get_num_between_two_signs(arg, '/'):
            user = await self.listener.get_basic_user_info(user_id)
        else:
            user = await self.listener.get_basic_user_info(arg)

        if not user:
            raise ValueError("找不到对应的用户")

        return user

    async def _cmd_set(
        self, ctx: Context, new_permission: int, note: str, user: Optional[tb.BasicUserInfo] = None
    ) -> bool:
        """
        设置权限级别
        """

        if user is None:
            user = await self._arg2user_info(ctx.args[0])

        old_permission, old_note, _ = await ctx.admin.get_user_id_full(user.user_id)
        if old_permission >= ctx.exec_permission:
            raise ValueError("原权限大于等于操作者权限")
        if new_permission >= ctx.exec_permission:
            raise ValueError("新权限大于等于操作者权限")

        tb.LOG.info(f"forum={ctx.fname} user={user} old_note={old_note}")

        if new_permission != 0:
            success = await ctx.admin.add_user_id(user.user_id, permission=new_permission, note=note)
        else:
            success = await ctx.admin.del_user_id(user.user_id)

        return success

    @check_and_log(need_permission=0, need_arg_num=0)
    async def cmd_holyshit(self, ctx: Context) -> None:
        """
        holyshit指令
        召唤4名活跃吧务，使用参数extra_info来附带额外的召唤需求
        """

        if not self.time_recorder.allow_execute():
            raise ValueError("speaker尚未冷却完毕")

        active_admin_list = [
            (await self.listener.get_basic_user_info(user_id)).user_name
            for user_id in await ctx.admin.get_user_id_list(lower_permission=2, limit=5)
        ]
        extra_info = ctx.args[0] if len(ctx.args) else '无'
        content = f"该回复为吧务召唤指令@.v_guard holyshit的自动响应\n召唤人诉求: {extra_info} @" + " @".join(active_admin_list)

        if await ctx.speaker.add_post(ctx.fname, ctx.tid, content):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=1, need_arg_num=0)
    async def cmd_recommend(self, ctx: Context) -> None:
        """
        recommend指令
        对指令所在主题帖执行“大吧主首页推荐”操作
        """

        if await ctx.admin.client.recommend(ctx.fname, ctx.tid):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=2, need_arg_num=1)
    async def cmd_move(self, ctx: Context) -> None:
        """
        move指令
        将指令所在主题帖移动至名为tab_name的分区
        """

        if not (threads := await self.listener.client.get_threads(ctx.fname)):
            return

        from_tab_id = 0
        for thread in threads:
            if thread.tid == ctx.tid:
                from_tab_id = thread.tab_id
        to_tab_id = threads.tab_map.get(ctx.args[0], 0)

        if await ctx.admin.client.move(ctx.fname, ctx.tid, to_tab_id=to_tab_id, from_tab_id=from_tab_id):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=2, need_arg_num=0)
    async def cmd_good(self, ctx: Context) -> None:
        """
        good指令
        将指令所在主题帖加到以cname为名的精华分区。cname默认为''即不分区
        """

        cname = ctx.args[0] if len(ctx.args) else ''

        if await ctx.admin.client.good(ctx.fname, ctx.tid, cname=cname):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=2, need_arg_num=0)
    async def cmd_ungood(self, ctx: Context) -> None:
        """
        ungood指令
        撤销指令所在主题帖的精华
        """

        if await ctx.admin.client.ungood(ctx.fname, ctx.tid):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=4, need_arg_num=0)
    async def cmd_top(self, ctx: Context) -> None:
        """
        top指令
        置顶指令所在主题帖
        """

        if await ctx.admin.client.top(ctx.fname, ctx.tid):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=4, need_arg_num=0)
    async def cmd_untop(self, ctx: Context) -> None:
        """
        untop指令
        撤销指令所在主题帖的置顶
        """

        if await ctx.admin.client.untop(ctx.fname, ctx.tid):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=2, need_arg_num=0)
    async def cmd_hide(self, ctx: Context) -> None:
        """
        hide指令
        屏蔽指令所在主题帖
        """

        if await ctx.admin.hide_thread(ctx.tid):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=2, need_arg_num=0)
    async def cmd_unhide(self, ctx: Context) -> None:
        """
        unhide指令
        解除指令所在主题帖的屏蔽
        """

        if await ctx.admin.client.unhide_thread(ctx.fname, ctx.tid):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=2, need_arg_num=0)
    async def cmd_delete(self, ctx: Context) -> None:
        """
        delete指令
        删帖
        """

        await self._cmd_drop(ctx)

    @check_and_log(need_permission=2, need_arg_num=1)
    async def cmd_recover(self, ctx: Context) -> None:
        """
        recover指令
        恢复删帖
        """

        _id = ctx.args[0]
        _id = _id[_id.rfind('#') + 1 :]
        _id = int(_id)

        if _id < 1e11:
            success = await ctx.admin.client.recover_thread(ctx.fname, _id)
        else:
            success = await ctx.admin.client.recover_post(ctx.fname, _id)

        if success:
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=2, need_arg_num=1)
    async def cmd_block(self, ctx: Context) -> None:
        """
        block指令
        通过id封禁对应用户10天
        """

        await self._cmd_block(ctx, 10)

    @check_and_log(need_permission=2, need_arg_num=1)
    async def cmd_block3(self, ctx: Context) -> None:
        """
        block3指令
        通过id封禁对应用户3天
        """

        await self._cmd_block(ctx, 3)

    @check_and_log(need_permission=2, need_arg_num=1)
    async def cmd_block1(self, ctx: Context) -> None:
        """
        block1指令
        通过id封禁对应用户1天
        """

        await self._cmd_block(ctx, 1)

    async def _cmd_block(self, ctx: Context, day: int) -> None:
        """
        封禁用户
        """

        user = await self._arg2user_info(ctx.args[0])
        note = ctx.args[1] if len(ctx.args) > 1 else ctx.note

        if await ctx.admin.block(user.portrait, day=day, reason=note):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=2, need_arg_num=1)
    async def cmd_unblock(self, ctx: Context) -> None:
        """
        unblock指令
        通过id解封用户
        """

        user = await self._arg2user_info(ctx.args[0])

        if await ctx.admin.client.unblock(ctx.fname, user.user_id):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=2, need_arg_num=0)
    async def cmd_drop(self, ctx: Context) -> None:
        """
        drop指令
        删帖并封10天
        """

        await self._cmd_drop(ctx, 10)

    @check_and_log(need_permission=2, need_arg_num=0)
    async def cmd_drop3(self, ctx: Context) -> None:
        """
        drop3指令
        删帖并封3天
        """

        await self._cmd_drop(ctx, 3)

    @check_and_log(need_permission=2, need_arg_num=0)
    async def cmd_drop1(self, ctx: Context) -> None:
        """
        drop1指令
        删帖并封1天
        """

        await self._cmd_drop(ctx, 1)

    async def _cmd_drop(self, ctx: Context, day: int = 0) -> None:
        """
        封禁用户并删除父级
        """

        await ctx._init_full()

        note = ctx.args[0] if len(ctx.args) > 0 else ctx.note
        coros = []

        if ctx.at.is_floor:
            tb.LOG.info(f"Try to del post. text={ctx.parent.text} user={ctx.parent.user}")
            coros.append(ctx.admin.del_post(ctx.parent.pid))

        else:
            if ctx.at.is_thread:
                if ctx.fname != ctx.parent.fname:
                    raise ValueError("被转发帖不来自同一个吧")
                if not ctx.parent.contents.ats:
                    raise ValueError("无法获取被转发帖的作者信息")
                ctx.parent._user = await self.listener.get_basic_user_info(ctx.parent.contents.ats[0].user_id)

                tb.LOG.info(f"Try to del thread. text={ctx.parent.text} user={ctx.parent.user}")
                coros.append(ctx.admin.del_post(ctx.parent.pid))

            else:
                tb.LOG.info(f"Try to del thread. text={ctx.parent.text} user={ctx.parent.user}")
                coros.append(ctx.admin.del_post(ctx.parent.pid))

        if day:
            coros.append(ctx.admin.block(ctx.parent.user.portrait, day=day, reason=note))

        await ctx.admin.del_post(ctx.pid)
        await asyncio.gather(*coros)

    @check_and_log(need_permission=4, need_arg_num=1)
    async def cmd_black(self, ctx: Context) -> None:
        """
        black指令
        将id加入脚本黑名单
        """

        note = ctx.args[1] if len(ctx.args) > 1 else ctx.note

        if await self._cmd_set(ctx, -5, note):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=3, need_arg_num=1)
    async def cmd_white(self, ctx: Context) -> None:
        """
        white指令
        将id加入脚本白名单
        """

        note = ctx.args[1] if len(ctx.args) > 1 else ctx.note

        if await self._cmd_set(ctx, 1, note):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=3, need_arg_num=1)
    async def cmd_reset(self, ctx: Context) -> None:
        """
        reset指令
        将id移出脚本名单
        """

        note = ctx.args[1] if len(ctx.args) > 1 else ctx.note

        if await self._cmd_set(ctx, 0, note):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=4, need_arg_num=0)
    async def cmd_exdrop(self, ctx: Context) -> None:
        """
        exdrop指令
        删帖并将发帖人加入脚本黑名单+封禁十天
        """

        await self._cmd_drop(ctx, 10)

        user = ctx.parent.user
        note = ctx.args[0] if len(ctx.args) > 0 else ctx.note

        await self._cmd_set(ctx, -5, note, user=user)

    @check_and_log(need_permission=4, need_arg_num=2)
    async def cmd_set(self, ctx: Context) -> None:
        """
        set指令
        设置用户的权限级别
        """

        new_permission = int(ctx.args[1])
        note = ctx.args[2] if len(ctx.args) > 2 else ctx.note

        if await self._cmd_set(ctx, new_permission, note):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=0, need_arg_num=1)
    async def cmd_get(self, ctx: Context) -> None:
        """
        get指令
        获取用户的个人信息与标记信息
        """

        if not self.time_recorder.allow_execute():
            raise ValueError("speaker尚未冷却完毕")

        user = await self._arg2user_info(ctx.args[0])

        permission, note, record_time = await ctx.admin.get_user_id_full(user.user_id)
        msg_content = f"""user_name: {user.user_name}\nuser_id: {user.user_id}\nportrait: {user.portrait}\npermission: {permission}\nnote: {note}\nrecord_time: {record_time.strftime("%Y-%m-%d %H:%M:%S")}"""
        post_content = f"""@{ctx.at.user.user_name} \n{msg_content}"""

        success, _ = await asyncio.gather(
            ctx.speaker.add_post(ctx.fname, ctx.tid, post_content),
            ctx.speaker.send_msg(ctx.user.user_id, msg_content),
        )
        if success:
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=4, need_arg_num=2)
    async def cmd_img_set(self, ctx: Context) -> None:
        """
        img_set指令
        设置图片的封锁级别
        """

        await ctx._init_full()
        imgs = ctx.parent.contents.imgs

        if len(ctx.args) > 2:
            index = int(ctx.args[0])
            imgs: List[tb.typedefs.FragImage] = imgs[index - 1 : index]
            permission = int(ctx.args[1])
            note = ctx.args[2]
        else:
            permission = int(ctx.args[0])
            note = ctx.args[1]

        for img in imgs:
            image = await self.listener.client.get_image(img.src)
            if image is None:
                continue
            img_hash = self.listener.compute_imghash(image)

            await ctx.admin.db.add_imghash(ctx.fname, img_hash, img.hash, permission=permission, note=note)

        await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=3, need_arg_num=0)
    async def cmd_img_reset(self, ctx: Context) -> None:
        """
        img_reset指令
        重置图片的封锁级别
        """

        await ctx._init_full()
        imgs = ctx.parent.contents.imgs

        if ctx.args:
            index = int(ctx.args[0])
            imgs: List[tb.typedefs.FragImage] = imgs[index - 1 : index]

        for img in imgs:
            image = await self.listener.client.get_image(img.src)
            if image is None:
                continue
            img_hash = self.listener.compute_imghash(image)

            await ctx.admin.db.del_imghash(ctx.fname, img_hash)

        await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=1, need_arg_num=0)
    async def cmd_recom_status(self, ctx: Context) -> None:
        """
        recom_status指令
        获取大吧主推荐功能的月度配额状态
        """

        if not self.time_recorder.allow_execute():
            raise ValueError("speaker尚未冷却完毕")

        total_recom_num, used_recom_num = await ctx.admin.client.get_recom_status(ctx.fname)
        content = f"Used: {used_recom_num} / {total_recom_num} = {used_recom_num/total_recom_num*100:.2f}%"

        if await ctx.speaker.send_msg(ctx.user.user_id, content):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=4, need_arg_num=1)
    async def cmd_tb_black(self, ctx: Context) -> None:
        """
        tb_black指令
        将id加入贴吧黑名单
        """

        user = await self._arg2user_info(ctx.args[0])

        if await ctx.admin.client.blacklist_add(ctx.fname, user.user_id):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=3, need_arg_num=1)
    async def cmd_tb_reset(self, ctx: Context) -> None:
        """
        tb_reset指令
        将id移出贴吧黑名单
        """

        user = await self._arg2user_info(ctx.args[0])

        if await ctx.admin.client.blacklist_del(ctx.fname, user.user_id):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=2, need_arg_num=0)
    async def cmd_water(self, ctx: Context) -> None:
        """
        water指令
        将指令所在主题帖标记为无关水，并临时屏蔽
        """

        if await ctx.admin.add_tid(ctx.tid, mode=True) and await ctx.admin.hide_thread(ctx.tid):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=2, need_arg_num=0)
    async def cmd_unwater(self, ctx: Context) -> None:
        """
        unwater指令
        清除指令所在主题帖的无关水标记，并立刻解除屏蔽
        """

        if await ctx.admin.del_tid(ctx.tid) and await ctx.admin.client.unhide_thread(ctx.fname, ctx.tid):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=3, need_arg_num=1)
    async def cmd_water_restrict(self, ctx: Context) -> None:
        """
        water_restrict指令
        控制当前吧的云审查脚本的无关水管控状态
        """

        if ctx.args[0] == "enter":
            if await ctx.admin.add_tid(0, mode=True):
                await ctx.admin.del_post(ctx.pid)
        elif ctx.args[0] == "exit":
            if await ctx.admin.add_tid(0, mode=False):
                await ctx.admin.del_post(ctx.pid)
            limit = 128
            tids = await ctx.admin.get_tid_hide_list(limit=limit)
            while 1:
                for tid in tids:
                    if await ctx.admin.client.unhide_thread(ctx.fname, tid):
                        await ctx.admin.add_tid(tid, mode=False)
                if len(tids) != limit:
                    break

    @check_and_log(need_permission=2, need_arg_num=0)
    async def cmd_active(self, ctx: Context) -> None:
        """
        active指令
        将发起指令的吧务移动到活跃吧务队列的最前端，以响应holyshit指令
        """

        if await ctx.admin.add_user_id(ctx.user.user_id, permission=ctx.exec_permission, note="cmd_active"):
            await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=1, need_arg_num=0)
    async def cmd_ping(self, ctx: Context) -> None:
        """
        ping指令
        用于测试bot可用性的空指令
        """

        await ctx.admin.del_post(ctx.pid)

    @check_and_log(need_permission=129, need_arg_num=65536)
    async def cmd_default(self, ctx: Context) -> None:
        """
        default指令
        """


if __name__ == '__main__':

    async def main():
        async with Listener() as listener:
            await listener.run()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
