__all__ = ['Reviewer']

import asyncio
import binascii
from typing import List, Literal, Optional, Tuple, Union

import cv2 as cv
import numpy as np

from ._logger import LOG
from .client import Client
from .database import Database
from .typedefs import BasicUserInfo, Comments, Posts, Threads


class Reviewer(object):
    """
    提供贴吧审查功能

    Args:
        BDUSS_key (str, optional): 用于从CONFIG中提取BDUSS. Defaults to None.
        fname (str, optional): 贴吧名. Defaults to ''.

    Attributes:
        fname (str): 贴吧名
        client (Client): 客户端
        db (Database): 数据库连接
    """

    __slots__ = [
        'fname',
        'client',
        'db',
        '_img_hasher',
        '_qrdetector',
    ]

    def __init__(self, BDUSS_key: Optional[str] = None, fname: str = ''):
        super(Reviewer, self).__init__()

        self.fname: str = fname

        self.client = Client(BDUSS_key)
        self.db = Database(fname)
        self._img_hasher: cv.img_hash.AverageHash = None
        self._qrdetector: cv.QRCodeDetector = None

    async def enter(self) -> "Reviewer":
        await asyncio.gather(self.client.__aenter__(), self.db.__aenter__())
        return self

    async def __aenter__(self) -> "Reviewer":
        return await self.enter()

    async def close(self) -> None:
        await self.client.close()
        await self.db.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @property
    def img_hasher(self) -> cv.img_hash.AverageHash:
        if self._img_hasher is None:
            self._img_hasher = cv.img_hash.AverageHash.create()
        return self._img_hasher

    @property
    def qrdetector(self) -> cv.QRCodeDetector:
        if self._qrdetector is None:
            self._qrdetector = cv.QRCodeDetector()
        return self._qrdetector

    async def get_fid(self, fname: str) -> int:
        """
        通过贴吧名获取fid

        Args:
            fname (str): 贴吧名

        Returns:
            int: 该贴吧的fid
        """

        if fid := self.client._fname2fid.get(fname, 0):
            return fid

        if fid := await self.db.get_fid(fname):
            self.client.add_forum_cache(fname, fid)
            return fid

        if fid := await self.client.get_fid(fname):
            self.client.add_forum_cache(fname, fid)
            await self.db.add_forum(fid, fname)

        return fid

    async def get_fname(self, fid: int) -> str:
        """
        通过fid获取贴吧名

        Args:
            fid (int): forum_id

        Returns:
            str: 该贴吧的贴吧名
        """

        if fname := self.client._fid2fname.get(fid, 0):
            return fname

        if fname := await self.db.get_fname(fid):
            self.client.add_forum_cache(fname, fid)
            return fname

        if fname := await self.client.get_fname(fid):
            self.client.add_forum_cache(fname, fid)
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

        return await self.client.get_threads(self.fname, pn, rn=rn, sort=sort, is_good=is_good)

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
            bool: 操作是否成功
        """

        return await self.client.block(self.fname, _id, day=day, reason=reason)

    async def hide_thread(self, tid: int) -> bool:
        """
        屏蔽主题帖

        Args:
            tid (int): 待屏蔽的主题帖tid

        Returns:
            bool: 操作是否成功
        """

        return await self.client.hide_thread(self.fname, tid)

    async def del_thread(self, tid: int) -> bool:
        """
        删除主题帖

        Args:
            tid (int): 待删除的主题帖tid

        Returns:
            bool: 操作是否成功
        """

        return await self.client.del_thread(self.fname, tid)

    async def del_post(self, pid: int) -> bool:
        """
        删除回复

        Args:
            pid (int): 待删除的回复pid

        Returns:
            bool: 操作是否成功
        """

        return await self.client.del_post(self.fname, pid)

    async def add_id(self, _id: int, *, id_last_edit: int = 0) -> bool:
        """
        将id添加到表id_{fname}
        Args:
            _id (int): tid或pid
            id_last_edit (int): 用于识别id的子对象列表是否发生修改 \
                若该id为tid则id_last_edit应为last_time 若该id为pid则id_last_edit应为reply_num. Defaults to 0.
        Returns:
            bool: 操作是否成功
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

    def scan_QRcode(self, image: np.ndarray) -> str:
        """
        扫描图像中的二维码

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

    def compute_imghash(self, image: np.ndarray) -> str:
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

    async def get_imghash(self, image: np.ndarray) -> int:
        """
        获取图像的封锁级别

        Args:
            image (np.ndarray): 图像

        Returns:
            int: 封锁级别
        """

        if img_hash := self.compute_imghash(image):
            return await self.db.get_imghash(self.fname, img_hash)
        return 0

    async def get_imghash_full(self, image: np.ndarray) -> Tuple[int, str]:
        """
        获取图像的完整信息

        Args:
            image (np.ndarray): 图像

        Returns:
            tuple[int, str]: 封锁级别, 备注
        """

        if img_hash := self.compute_imghash(image):
            return await self.db.get_imghash_full(self.fname, img_hash)
        return 0, ''
