__all__ = [
    'BaseReviewer',
    'Reviewer',
]

try:
    import cv2 as cv
    import numpy as np
except ImportError:
    pass

import asyncio
import binascii
import functools
import time
import types
from collections.abc import Callable, Iterator
from typing import List, Literal, Optional, Tuple, Union

from ._helpers import DelFlag, Punish, alog_time
from ._logger import LOG
from .client import Client
from .database import Database
from .typedefs import BasicUserInfo, Comment, Comments, Post, Posts, Thread, Threads


class BaseReviewer(object):
    """
    贴吧审查实用功能

    """

    __slots__ = [
        'client',
        'db',
        '_img_hasher',
        '_qrdetector',
    ]

    def __init__(self, BDUSS_key: Optional[str] = None, fname: str = ''):
        super(BaseReviewer, self).__init__()

        self.client = Client(BDUSS_key)
        self.db = Database(fname)
        self._img_hasher: "cv.img_hash.AverageHash" = None
        self._qrdetector: "cv.QRCodeDetector" = None

    async def __aenter__(self) -> "BaseReviewer":
        await asyncio.gather(self.client.__aenter__(), self.db.__aenter__())
        return self

    async def close(self) -> None:
        await self.client.close()
        await self.db.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @property
    def img_hasher(self) -> "cv.img_hash.AverageHash":
        if self._img_hasher is None:
            self._img_hasher = cv.img_hash.AverageHash.create()
        return self._img_hasher

    @property
    def qrdetector(self) -> "cv.QRCodeDetector":
        if self._qrdetector is None:
            self._qrdetector = cv.QRCodeDetector()
        return self._qrdetector

    async def get_fid(self, fname: str) -> int:
        """
        通过贴吧名获取forum_id

        Args:
            fname (str): 贴吧名

        Returns:
            int: 该贴吧的forum_id
        """

        if fid := self.client._fname2fid.get(fname, 0):
            return fid

        if fid := await self.db.get_fid(fname):
            self.client._add_forum_cache(fname, fid)
            return fid

        if fid := await self.client.get_fid(fname):
            self.client._add_forum_cache(fname, fid)
            await self.db.add_forum(fid, fname)

        return fid

    async def get_fname(self, fid: int) -> str:
        """
        通过forum_id获取贴吧名

        Args:
            fid (int): forum_id

        Returns:
            str: 该贴吧的贴吧名
        """

        if fname := self.client._fid2fname.get(fid, 0):
            return fname

        if fname := await self.db.get_fname(fid):
            self.client._add_forum_cache(fname, fid)
            return fname

        if fname := await self.client.get_fname(fid):
            self.client._add_forum_cache(fname, fid)
            await self.db.add_forum(fid, fname)

        return fname

    async def get_basic_user_info(self, _id: Union[str, int]) -> BasicUserInfo:
        """
        获取简略版用户信息

        Args:
            _id (str | int): 待补全用户的id user_id/user_name/portrait

        Returns:
            BasicUserInfo: 简略版用户信息 仅保证包含user_name/portrait/user_id
        """

        if user := await self.db.get_basic_user_info(_id):
            return user

        if user := await self.client.get_basic_user_info(_id):
            await self.db.add_user(user)

        return user

    async def get_threads(
        self,
        /,
        pn: int = 1,
        *,
        rn: int = 30,
        sort: int = 5,
        is_good: bool = False,
    ) -> Threads:
        """
        获取首页帖子

        Args:
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30.
            sort (int, optional): 排序方式 对于有热门分区的贴吧0是热门排序1是按发布时间2报错34都是热门排序>=5是按回复时间
                对于无热门分区的贴吧0是按回复时间1是按发布时间2报错>=3是按回复时间. Defaults to 5.
            is_good (bool, optional): True为获取精品区帖子 False为获取普通区帖子. Defaults to False.

        Returns:
            Threads: 帖子列表
        """

        return await self.client.get_threads(self.db.fname, pn, rn=rn, sort=sort, is_good=is_good)

    async def get_posts(
        self,
        tid: int,
        /,
        pn: int = 1,
        *,
        rn: int = 30,
        sort: int = 0,
        only_thread_author: bool = False,
        with_comments: bool = False,
        comment_sort_by_agree: bool = True,
        comment_rn: int = 10,
        is_fold: bool = False,
    ) -> Posts:
        """
        获取主题帖内回复

        Args:
            tid (int): 所在主题帖tid
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30.
            sort (int, optional): 0则按时间顺序请求 1则按时间倒序请求 2则按热门序请求. Defaults to 0.
            only_thread_author (bool, optional): True则只看楼主 False则请求全部. Defaults to False.
            with_comments (bool, optional): True则同时请求高赞楼中楼 False则返回的Posts.comments为空. Defaults to False.
            comment_sort_by_agree (bool, optional): True则楼中楼按点赞数顺序 False则楼中楼按时间顺序. Defaults to True.
            comment_rn (int, optional): 请求的楼中楼数量. Defaults to 10.
            is_fold (bool, optional): 是否请求被折叠的回复. Defaults to False.

        Returns:
            Posts: 回复列表
        """

        return await self.client.get_posts(
            tid,
            pn,
            rn=rn,
            sort=sort,
            only_thread_author=only_thread_author,
            with_comments=with_comments,
            comment_sort_by_agree=comment_sort_by_agree,
            comment_rn=comment_rn,
            is_fold=is_fold,
        )

    async def get_comments(
        self,
        tid: int,
        pid: int,
        /,
        pn: int = 1,
        *,
        is_floor: bool = False,
    ) -> Comments:
        """
        获取楼中楼回复

        Args:
            tid (int): 所在主题帖tid
            pid (int): 所在回复pid或楼中楼pid
            pn (int, optional): 页码. Defaults to 1.
            is_floor (bool, optional): pid是否指向楼中楼. Defaults to False.

        Returns:
            Comments: 楼中楼列表
        """

        return await self.client.get_comments(tid, pid, pn, is_floor=is_floor)

    async def block(
        self,
        _id: Union[str, int],
        *,
        day: Literal[1, 3, 10] = 1,
        reason: str = '',
    ) -> bool:
        """
        封禁用户

        Args:
            _id (str | int): 待封禁用户的id user_id/user_name/portrait 优先portrait
            day (Literal[1, 3, 10], optional): 封禁天数. Defaults to 1.
            reason (str, optional): 封禁理由. Defaults to ''.

        Returns:
            bool: True成功 False失败
        """

        return await self.client.block(self.db.fname, _id, day=day, reason=reason)

    async def hide_thread(self, tid: int) -> bool:
        """
        屏蔽主题帖

        Args:
            tid (int): 待屏蔽的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        return await self.client.hide_thread(self.db.fname, tid)

    async def del_thread(self, tid: int) -> bool:
        """
        删除主题帖

        Args:
            tid (int): 待删除的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        return await self.client.del_thread(self.db.fname, tid)

    async def del_post(self, pid: int) -> bool:
        """
        删除回复

        Args:
            pid (int): 待删除的回复pid

        Returns:
            bool: True成功 False失败
        """

        return await self.client.del_post(self.db.fname, pid)

    async def add_id(self, _id: int, *, id_last_edit: int = 0) -> bool:
        """
        将id添加到表id_{fname}
        Args:
            _id (int): tid或pid
            id_last_edit (int): 用于识别id的子对象列表是否发生修改 \
                若该id为tid则id_last_edit应为last_time 若该id为pid则id_last_edit应为reply_num. Defaults to 0.
        Returns:
            bool: True成功 False失败
        """

        return await self.db.add_id(_id, tag=id_last_edit)

    async def get_id(self, _id: int) -> int:
        """
        获取表id_{fname}中id对应的id_last_edit值
        Args:
            _id (int): tid或pid
        Returns:
            int: id_last_edit -1表示表中无id
        """

        res = await self.db.get_id(_id)
        if res is None:
            res = -1
        return res

    async def is_tid_hide(self, tid: int) -> Optional[bool]:
        """
        获取表tid_water_{fname}中tid的待恢复状态

        Args:
            tid (int): 主题帖tid

        Returns:
            bool | None: True表示tid待恢复 False表示tid已恢复 None表示表中无记录
        """

        res = await self.db.get_tid(tid)
        if res == 1:
            return True
        elif res == 0:
            return False
        else:
            return None

    async def get_tid_hide_list(self, limit: int = 128, offset: int = 0) -> List[int]:
        """
        获取表tid_{fname}中待恢复的tid的列表

        Args:
            limit (int, optional): 返回数量限制. Defaults to 128.
            offset (int, optional): 偏移. Defaults to 0.

        Returns:
            list[int]: tid列表
        """

        return await self.db.get_tid_list(tag=1, limit=limit, offset=offset)

    def scan_QRcode(self, image: "np.ndarray") -> str:
        """
        审查图像中的二维码

        Args:
            image (np.ndarray): 图像

        Returns:
            str: 二维码信息 解析失败时返回''
        """

        try:
            data = self.qrdetector.detectAndDecode(image)[0]
        except Exception as err:
            LOG.warning(err)
            data = ''

        return data

    def compute_imghash(self, image: "np.ndarray") -> str:
        """
        计算图像的phash

        Args:
            image (np.ndarray): 图像

        Returns:
            str: 图像的phash
        """

        try:
            img_hash_array = self.img_hasher.compute(image)
            img_hash = binascii.hexlify(img_hash_array.tobytes()).decode('ascii')
        except Exception as err:
            LOG.warning(err)
            img_hash = ''

        return img_hash

    async def get_imghash(self, image: "np.ndarray") -> int:
        """
        获取图像的封锁级别

        Args:
            image (np.ndarray): 图像

        Returns:
            int: 封锁级别
        """

        if img_hash := self.compute_imghash(image):
            return await self.db.get_imghash(img_hash)
        return 0

    async def get_imghash_full(self, image: "np.ndarray") -> Tuple[int, str]:
        """
        获取图像的完整信息

        Args:
            image (np.ndarray): 图像

        Returns:
            tuple[int, str]: 封锁级别, 备注
        """

        if img_hash := self.compute_imghash(image):
            return await self.db.get_imghash_full(img_hash)
        return 0, ''


def _check_permission(func):
    """
    装饰器检查用户黑白名单状态
    """

    @functools.wraps(func)
    async def _(self: "Reviewer", obj: Union[Thread, Post, Comment]) -> Optional[Punish]:
        permission = await self.db.get_user_id(obj.user.user_id)
        if permission <= -5:
            return Punish(DelFlag.DELETE, 10, "黑名单")
        if permission >= 1:
            return Punish(DelFlag.WHITE)
        return await func(self, obj)

    return _


def _exce_punish(func):
    """
    装饰器执行删封操作
    """

    @functools.wraps(func)
    async def _(self: "Reviewer", obj: Union[Thread, Post, Comment]) -> None:
        punish: Optional[Punish] = await func(self, obj)
        if punish:
            await self.exce_delete(obj, punish)
            await self.exce_block(obj, punish)

    return _


class Reviewer(BaseReviewer):
    """
    贴吧审查器

    请使用以`review_`开头的类方法作为入口函数

    Args:
        BDUSS_key (str, optional): 用于快捷调用BDUSS. Defaults to None.
        fname (str, optional): 操作的目标贴吧名. Defaults to ''.

    Attributes:
        client (Client): 客户端
        db (Database): 数据库连接
    """

    __slots__ = [
        '__dict__',
    ]

    def __init__(self, BDUSS_key: str, fname: str):
        super(Reviewer, self).__init__(BDUSS_key, fname)

        self.exce_delete = self._exce_delete_debug
        self.exce_block = self._exce_block_debug

        self.thread_checkers = []
        self.post_checkers = []
        self.comment_checkers = []

    async def __aenter__(self) -> "Reviewer":
        await super(Reviewer, self).__aenter__()
        return self

    def time_interval(self) -> Callable[[], float]:
        """
        单页循环审查时由该方法提供执行间隔

        Returns:
            Callable[[], float]: 用于返回时间间隔的闭包
        """

        def _() -> float:
            return 12.0

        return _

    def time_threshold(self) -> Callable[[], int]:
        """
        该方法提供时间下限
        创建日期早于时间下限的对象不会被审查

        Returns:
            Callable[[], int]: 返回时间下限的闭包
        """

        time_thre = int(time.time()) - 15 * 24 * 3600

        def _() -> int:
            return time_thre

        return _

    async def _exce_block(self, obj: Union[Thread, Post, Comment], punish: Punish) -> None:
        """
        执行封禁

        Args:
            obj (Union[Thread,Post,Comment]): 封禁目标为obj.user
            punish (Punish): 待执行的惩罚
        """
        if punish.block_days:
            await self.block(obj.user.portrait, day=punish.block_days, reason=punish.note)

    async def _exce_block_debug(self, obj: Union[Thread, Post, Comment], punish: Punish) -> None:
        """
        执行封禁方法的一个debug替换
        一般在debug模式下不会实际执行封禁

        Args:
            obj (Union[Thread,Post,Comment]): 封禁目标为obj.user
            punish (Punish): 待执行的惩罚
        """
        if punish.block_days:
            LOG.info(f"Block. user={obj.user} note={punish.note}")

    async def _exce_delete(self, obj: Union[Thread, Post, Comment], punish: Punish) -> None:
        """
        执行删除

        Args:
            obj (Union[Thread,Post,Comment]): 删除目标
            punish (Punish): 待执行的惩罚
        """

        if punish.del_flag == DelFlag.DELETE:
            LOG.info(
                f"Del {obj.__class__.__name__}. text={obj.text} user={obj.user} level={obj.user.level} note={punish.note}"
            )
            await self.del_post(obj.pid)
        elif punish.del_flag == DelFlag.HIDE:
            LOG.info(
                f"Hide {obj.__class__.__name__}. text={obj.text} user={obj.user} level={obj.user.level} note={punish.note}"
            )
            await self.hide_thread(obj.tid)

    async def _exce_delete_debug(self, obj: Union[Thread, Post, Comment], punish: Punish) -> None:
        """
        执行删除方法的一个debug替换
        一般在debug模式下不会实际执行删除

        Args:
            obj (Union[Thread,Post,Comment]): 删除目标
            punish (Punish): 待执行的惩罚
        """

        if punish.del_flag == DelFlag.DELETE:
            LOG.info(
                f"Del {obj.__class__.__name__}. text={obj.text} user={obj.user} level={obj.user.level} note={punish.note}"
            )
        elif punish.del_flag == DelFlag.HIDE:
            LOG.info(
                f"Hide {obj.__class__.__name__}. text={obj.text} user={obj.user} level={obj.user.level} note={punish.note}"
            )

    async def review_loop(self) -> None:
        """
        单页循环审查
        """

        self.prepare_cfg_loop()

        while 1:
            try:
                asyncio.create_task(self.loop_handle_threads())
                await asyncio.sleep(self.time_interval_closure())

            except Exception:
                LOG.critical("Unexcepted error", exc_info=True)
                return

    def prepare_cfg_loop(self) -> None:
        """
        在单页循环审查开始前使用该函数设置参数
        """

        self.set_no_debug()
        self.time_interval_closure = self.time_interval()

    def set_no_debug(self) -> None:
        """
        生产环境下取消debug模式
        """

        self.exce_block = self._exce_block
        self.exce_delete = self._exce_delete

    @alog_time
    async def loop_handle_threads(self, pn: int = 1) -> None:
        """
        处理一个页码

        Args:
            pn (int, optional): 页码. Defaults to 1.
        """

        threads = await self.loop_get_threads(pn)
        threads = set(threads)
        await asyncio.gather(*[self.loop_handle_thread(thread) for thread in threads])

    async def loop_get_threads(self, pn: int) -> Iterator[Thread]:
        """
        单页循环审查时由该方法获取页码下的待审查主题帖

        Args:
            pn (int): 待审查主题帖列表所在页码

        Returns:
            Iterator[Thread]: 待审查主题帖的迭代器
        """

        threads = await self.get_threads(pn)
        return [thread for thread in threads if not thread.is_livepost]

    @_exce_punish
    @_check_permission
    async def loop_handle_thread(self, thread: Thread) -> Optional[Punish]:
        """
        处理单个主题帖

        Args:
            thread (Thread): 待处理的主题帖

        Returns:
            Optional[Punish]: 审查结果

        Note:
            一般不需要重写该函数
        """

        last_edit_time = await self.get_id(thread.tid)
        if last_edit_time == -1:
            await self.set_thread_level(thread)
            if punish := await self.run_thread_checkers(thread):
                return punish
        elif thread.last_time == last_edit_time:
            return
        elif thread.last_time < last_edit_time:
            await self.add_id(thread.tid, id_last_edit=thread.last_time)
            return

        if punish := await self.loop_handle_posts(thread):
            return punish

        await self.add_id(thread.tid, id_last_edit=thread.last_time)

    async def set_thread_level(self, thread: Thread) -> None:
        """
        补充主题帖楼主的等级

        Args:
            thread (Thread): 待设置楼主等级的主题帖
        """

        posts = await self.get_posts(thread.tid, rn=0)
        thread._user = posts.thread.user

    async def run_thread_checkers(self, thread: Thread) -> Optional[Punish]:
        """
        审查单个主题帖

        Args:
            thread (Thread): 待审查的主题帖

        Returns:
            Optional[Punish]: 审查结果
        """

        for checker in self.thread_checkers:
            punish = await checker(thread)
            if punish:
                return punish

    async def loop_handle_posts(self, thread: Thread) -> Optional[Punish]:
        """
        处理主题帖下的回复

        Args:
            thread (Thread): 父级主题帖

        Returns:
            Optional[Punish]: 主题帖的审查结果
        """

        posts = await self.loop_get_posts(thread)
        posts = set(posts)
        await asyncio.gather(*[self.loop_handle_post(post) for post in posts])

    async def loop_get_posts(self, thread: Thread) -> Iterator[Post]:
        """
        单页循环审查时由该方法获取主题帖下的待审查回复列表

        Args:
            thread (Thread): 父级主题帖

        Returns:
            Iterator[Post]: 待审查回复的迭代器
        """

        posts = await self.get_posts(thread.tid, pn=99999, sort=1, with_comments=True)
        posts = set(posts.objs)
        if thread.reply_num > 30:
            first_posts = await self.get_posts(thread.tid, with_comments=True)
            posts.update(first_posts.objs)

        return posts

    @_exce_punish
    @_check_permission
    async def loop_handle_post(self, post: Post) -> Optional[Punish]:
        """
        处理单个回复

        Args:
            post (Post): 待处理的回复

        Returns:
            Optional[Punish]: 审查结果

        Note:
            一般不需要重写该函数
        """

        last_reply_num = await self.get_id(post.pid)
        if post.reply_num == last_reply_num:
            return
        elif last_reply_num == -1:
            if punish := await self.run_post_checkers(post):
                return punish
        elif post.reply_num < last_reply_num:
            await self.add_id(post.pid, id_last_edit=post.reply_num)
            return

        if punish := await self.loop_handle_comments(post):
            return punish

        await self.add_id(post.pid, id_last_edit=post.reply_num)

    async def run_post_checkers(self, post: Post) -> Optional[Punish]:
        """
        审查单个回复

        Args:
            post (Post): 待审查的回复

        Returns:
            Optional[Punish]: 审查结果
        """

        for checker in self.post_checkers:
            punish = await checker(post)
            if punish:
                return punish

    async def loop_handle_comments(self, post: Post) -> Optional[Punish]:
        """
        处理回复下的楼中楼

        Args:
            post (Post): 父级回复

        Returns:
            Optional[Punish]: 回复审查结果
        """

        comments = await self.loop_get_comments(post)
        comments = set(comments)
        await asyncio.gather(*[self.loop_handle_comment(comment) for comment in comments])

    async def loop_get_comments(self, post: Post) -> Iterator[Comment]:
        """
        单页循环审查时由该方法获取回复下的待审查楼中楼

        Args:
            post (Post): 父级回复

        Returns:
            Iterator[Comment]: 待审查楼中楼的迭代器
        """

        reply_num = post.reply_num
        if (reply_num <= 10 and len(post.comments) != reply_num) or reply_num > 10:
            last_comments = await self.get_comments(post.tid, post.pid, pn=post.reply_num // 30 + 1)
            comments = set(last_comments)
            comments.update(post.comments)
            return comments

        else:
            return post.comments

    @_exce_punish
    @_check_permission
    async def loop_handle_comment(self, comment: Comment) -> Optional[Punish]:
        """
        处理单个楼中楼

        Args:
            comment (Comment): 待处理的楼中楼

        Returns:
            Optional[Punish]: 审查结果

        Note:
            一般不需要重写该函数
        """

        if await self.get_id(comment.pid) != -1:
            return
        if punish := await self.run_comment_checkers(comment):
            return punish

        await self.add_id(comment.pid)

    async def run_comment_checkers(self, comment: Comment) -> Optional[Punish]:
        """
        审查单个楼中楼

        Args:
            comment (Comment): 待审查的楼中楼

        Returns:
            Optional[Punish]: 审查结果
        """

        for checker in self.comment_checkers:
            punish = await checker(comment)
            if punish:
                return punish

    async def review_multi(self, worker_num: int = 8) -> None:
        """
        多页审查

        Args:
            worker_num (int, optional): 并发协程数. Defaults to 8.
        """

        self.multi_prepare()
        thread_queue: asyncio.Queue[Thread] = asyncio.Queue(maxsize=worker_num)
        running_flag = True

        async def producer() -> None:
            pn_iterator = self.multi_pn_iterator()
            for pn in pn_iterator:
                LOG.info(f"Handling thread_pn={pn}")
                for thread in await self.multi_get_threads(pn):
                    await thread_queue.put(thread)
            nonlocal running_flag
            running_flag = False

        async def worker(i: int) -> None:
            while 1:
                try:
                    thread = await asyncio.wait_for(thread_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    nonlocal running_flag
                    if not running_flag:
                        LOG.info(f"Worker#{i} quit")
                        return
                else:
                    await self.multi_handle_thread(thread)

        workers = [worker(i) for i in range(worker_num)]
        await asyncio.gather(*workers, producer())

    def multi_prepare(self) -> None:
        """
        在多页审查开始前使用该函数设置参数
        """

        self.set_no_debug()
        self.time_thre_closure = self.time_threshold()

    def multi_pn_iterator(self) -> Iterator[int]:
        """
        返回一个页码迭代器

        Returns:
            Iterator[int]: 页码迭代器
        """
        return range(64, 0, -1)

    async def multi_get_threads(self, pn: int) -> Iterator[Thread]:
        """
        多页审查时由该方法获取页码下的待审查主题帖

        Args:
            pn (int): 待审查主题帖列表所在页码

        Returns:
            Iterator[Thread]: 待审查主题帖的迭代器
        """

        threads = await self.get_threads(pn)
        return [thread for thread in threads if not thread.is_livepost]

    @_exce_punish
    @_check_permission
    async def multi_handle_thread(self, thread: Thread) -> Optional[Punish]:
        """
        处理单个主题帖

        Args:
            thread (Thread): 待审查的主题帖

        Returns:
            Optional[Punish]: 主题帖的审查结果
        """

        await self.set_thread_level(thread)
        punish = await self.run_thread_checkers(thread)
        if punish:
            return punish

        return await self.multi_handle_posts(thread)

    async def multi_handle_posts(self, thread: Thread) -> Optional[Punish]:
        """
        审查主题帖下的回复

        Args:
            thread (Thread): 父级主题帖

        Returns:
            Optional[Punish]: 主题帖的审查结果
        """

        async for post in self.multi_get_posts(thread):
            await self.multi_handle_post(post)

    async def multi_get_posts(self, thread: Thread) -> Post:
        """
        多页审查时由该方法获取主题帖下的待审查回复列表

        Args:
            thread (Thread): 父级主题帖

        Yields:
            Post: 待审查回复
        """

        time_thre = self.time_thre_closure()

        posts = await self.get_posts(thread.tid, pn=99999, sort=1, with_comments=True)
        if posts:
            for post in posts:
                yield post
            if posts[0].create_time < time_thre:
                return

        if (total_page := posts.page.total_page) >= 2:
            for post_pn in range(total_page - 2, 0, -1):
                LOG.debug(f"Scanning tid={thread.tid} pn={post_pn}")
                posts = await self.get_posts(thread.tid, pn=post_pn, with_comments=True)
                if posts:
                    for post in posts:
                        yield post
                    if posts[0].create_time < time_thre:
                        return

    @_exce_punish
    @_check_permission
    async def multi_handle_post(self, post: Post) -> Optional[Punish]:
        """
        处理单个回复

        Args:
            post (Post): 待审查的回复

        Returns:
            Optional[Punish]: 回复的审查结果
        """

        punish = await self.run_post_checkers(post)
        if punish:
            return punish
        return await self.multi_handle_comments(post)

    async def multi_handle_comments(self, post: Post) -> Optional[Punish]:
        """
        处理回复下的楼中楼

        Args:
            post (Post): 父级回复

        Returns:
            Optional[Punish]: 回复审查结果
        """

        comments = await self.multi_get_comments(post)
        comments = set(comments)
        await asyncio.gather(*[self.multi_handle_comment(comment) for comment in comments])

    async def multi_get_comments(self, post: Post) -> Iterator[Comment]:
        """
        多页审查时由该方法获取回复下的待审查楼中楼

        Args:
            post (Post): 父级回复

        Returns:
            Iterator[Comment]: 待审查楼中楼的迭代器
        """

        reply_num = post.reply_num
        if (reply_num <= 10 and len(post.comments) != reply_num) or reply_num > 10:
            last_comments = await self.get_comments(post.tid, post.pid, pn=post.reply_num // 30 + 1)
            comments = set(last_comments)
            comments.update(post.comments)
            return comments

        else:
            return post.comments

    @_exce_punish
    @_check_permission
    async def multi_handle_comment(self, comment: Comment) -> Optional[Punish]:
        """
        处理单个楼中楼

        Args:
            comment (Comment): 待审查的楼中楼

        Returns:
            Optional[Punish]: 楼中楼的审查结果
        """

        punish = await self.run_comment_checkers(comment)
        if punish:
            return punish

    async def review_debug(self) -> None:
        """
        debug审查

        在页码(7, 16]上测试审查规则
        请在投入生产环境前使用该方法执行最终检查
        并仔细观察是否存在误删误封的情况
        该方法不会实际执行删封操作
        """

        self.debug_prepare()

        try:
            await self.review_multi(8)
        except KeyboardInterrupt:
            return

    def debug_prepare(self) -> None:
        """
        在debug审查开始前使用该函数设置参数
        """

        self.exce_delete = self._exce_delete_debug
        self.exce_block = self._exce_block_debug
        self.time_thre_closure = self.time_threshold()

        def pn_iterator(_):
            return range(16, 7, -1)

        self.multi_pn_iterator = types.MethodType(pn_iterator, self)

        def prepare_cfg_multi(_):
            pass

        self.multi_prepare = types.MethodType(prepare_cfg_multi, self)

    async def review_test(self, tid: Optional[int] = None, pid: Optional[int] = None, is_floor: bool = False) -> None:
        """
        在单个实际目标上测试审查规则

        Args:
            tid (int, optional): 目标所在主题帖id. Defaults to None.
            pid (int, optional): 目标所在回复或楼中楼id. Defaults to None.
            is_floor (bool, optional): pid是否指向一个楼中楼. Defaults to False.
        """

        async def check_and_print(checkers, obj):
            LOG.debug(f"{obj.__class__.__name__}={obj}")
            for checker in checkers:
                punish = await checker(obj)
                LOG.debug(f"Checker={checker.__name__} punish={punish}")

        if pid:
            comments = await self.get_comments(tid, pid, is_floor=is_floor)
            if is_floor:
                for comment in comments:
                    if comment.pid == pid:
                        break
                await check_and_print(self.comment_checkers, comment)
            else:
                post = comments.post
                await check_and_print(self.post_checkers, post)
        else:
            posts = await self.get_posts(tid, rn=0)
            thread = posts.thread
            await check_and_print(self.thread_checkers, thread)
