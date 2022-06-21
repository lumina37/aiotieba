# -*- coding:utf-8 -*-
__all__ = ['Reviewer']

import asyncio
import binascii
import datetime
from typing import List, Optional, Tuple, Union

import cv2 as cv
import numpy as np

from .client import Client
from .database import Database
from .logger import LOG
from .types import BasicUserInfo


class Reviewer(Client):
    """
    提供贴吧审查功能

    Args:
        BDUSS_key (str, optional): 用于从CONFIG中提取BDUSS. Defaults to ''.
        fname (str, optional): 贴吧名. Defaults to ''.
    """

    __slots__ = ['fname', 'database', '_qrdetector']

    def __init__(self, BDUSS_key: str = '', fname: str = ''):
        super(Reviewer, self).__init__(BDUSS_key)

        self.fname: str = fname

        self.database: Database = Database()
        self._qrdetector: cv.QRCodeDetector = None

    async def enter(self) -> "Reviewer":
        await asyncio.gather(super().enter(), self.database.enter())
        return self

    async def __aenter__(self) -> "Reviewer":
        return await self.enter()

    async def close(self) -> None:
        await asyncio.gather(super().close(), self.database.close(), return_exceptions=True)

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

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

        if fid := self.fid_dict.get(fname, 0):
            return fid

        if fid := await self.database.get_fid(fname):
            self.fid_dict[fname] = fid
            return fid

        if fid := await super().get_fid(fname):
            await self.database.add_forum(fid, fname)

        return fid

    async def get_fname(self, fid: int) -> str:
        """
        通过fid获取贴吧名

        Args:
            fid (int): forum_id

        Returns:
            str: 该贴吧的贴吧名
        """

        if fname := await self.database.get_fname(fid):
            return fname

        if fname := await super().get_fname(fid):
            await self.database.add_forum(fid, fname)

        return fname

    async def get_basic_user_info(self, _id: Union[str, int]) -> BasicUserInfo:
        """
        获取简略版用户信息

        Args:
            _id (str | int): 待补全用户的id user_id/user_name/portrait

        Returns:
            BasicUserInfo: 简略版用户信息 仅保证包含user_name/portrait/user_id
        """

        if user := await self.database.get_basic_user_info(_id):
            return user

        if user := await super().get_basic_user_info(_id):
            await self.database.add_user(user)

        return user

    async def refuse_unblock_appeals(self) -> None:
        """
        拒绝本吧所有解封申诉
        """

        while appeal_ids := await self.get_unblock_appeal_list(self.fname):
            await asyncio.gather(*[self.handle_unblock_appeal(self.fname, appeal_id) for appeal_id in appeal_ids])

    async def add_id(self, _id: int, id_last_edit: int = 0) -> bool:
        """
        将id添加到表id_{fname}

        Args:
            _id (int): tid或pid
            id_last_edit (int): 用于识别id的子对象列表是否发生修改 \
                若该id为tid则id_last_edit应为last_time 若该id为pid则id_last_edit应为reply_num. Defaults to 0.

        Returns:
            bool: 操作是否成功
        """

        return await self.database.add_id(self.fname, _id, id_last_edit)

    async def get_id(self, _id: int) -> int:
        """
        获取表id_{fname}中id对应的id_last_edit值

        Args:
            _id (int): tid或pid

        Returns:
            int: id_last_edit -1表示表中无id
        """

        res = await self.database.get_id(self.fname, _id)
        if res is None:
            res = -1
        return res

    async def del_id(self, _id: int) -> bool:
        """
        从表id_{fname}中删除id

        Args:
            _id (int): tid或pid

        Returns:
            bool: 操作是否成功
        """

        return await self.database.del_id(self.fname, _id)

    async def del_ids(self, hour: int) -> bool:
        """
        删除表id_{fname}中最近hour个小时记录的id

        Args:
            hour (int): 小时数

        Returns:
            bool: 操作是否成功
        """

        return await self.database.del_ids(self.fname, hour)

    async def add_tid(self, tid: int, mode: bool) -> bool:
        """
        将tid添加到表tid_water_{fname}

        Args:
            tid (int): 主题帖tid
            mode (bool): 待恢复状态 True对应待恢复 False对应已恢复

        Returns:
            bool: 操作是否成功
        """

        return await self.database.add_tid(self.fname, tid, int(mode))

    async def is_tid_hide(self, tid: int) -> Optional[bool]:
        """
        获取表tid_water_{fname}中tid的待恢复状态

        Args:
            tid (int): 主题帖tid

        Returns:
            bool | None: True表示tid待恢复 False表示tid已恢复 None表示表中无记录
        """

        res = await self.database.get_tid(self.fname, tid)
        if res == 1:
            return True
        elif res == 0:
            return False
        else:
            return None

    async def del_tid(self, tid: int) -> bool:
        """
        从表tid_water_{fname}中删除tid

        Args:
            tid (int): 主题帖tid

        Returns:
            bool: 操作是否成功
        """

        return await self.database.del_tid(self.fname, tid)

    async def get_tid_hide_list(self, limit: int = 128, offset: int = 0) -> List[int]:
        """
        获取表tid_{fname}中待恢复的tid的列表

        Args:
            limit (int, optional): 返回数量限制. Defaults to 128.
            offset (int, optional): 偏移. Defaults to 0.

        Returns:
            list[int]: tid列表
        """

        return await self.database.get_tid_list(self.fname, tag=1, limit=limit, offset=offset)

    async def add_user_id(self, user_id: int, permission: int = 0, note: str = '') -> bool:
        """
        将user_id添加到表user_id_{fname}

        Args:
            user_id (int): 用户的user_id
            permission (int, optional): 权限级别. Defaults to 0.
            note (str, optional): 备注. Defaults to ''.

        Returns:
            bool: 操作是否成功
        """

        return await self.database.add_user_id(self.fname, user_id, permission, note)

    async def del_user_id(self, user_id: int) -> bool:
        """
        从表user_id_{fname}中删除user_id

        Args:
            user_id (int): 用户的user_id

        Returns:
            bool: 操作是否成功
        """

        return await self.database.del_user_id(self.fname, user_id)

    async def get_user_id(self, user_id: int) -> int:
        """
        获取表user_id_{fname}中user_id的权限级别

        Args:
            user_id (int): 用户的user_id

        Returns:
            int: 权限级别
        """

        return await self.database.get_user_id(self.fname, user_id)

    async def get_user_id_full(self, user_id: int) -> Tuple[int, str, datetime.datetime]:
        """
        获取表user_id_{fname}中user_id的完整信息

        Args:
            user_id (int): 用户的user_id

        Returns:
            tuple[int, str, datetime.datetime]: 权限级别, 备注, 记录时间
        """

        return await self.database.get_user_id_full(self.fname, user_id)

    async def get_user_id_list(
        self, lower_permission: int = 0, upper_permission: int = 5, limit: int = 1, offset: int = 0
    ) -> List[int]:
        """
        获取表user_id_{fname}中user_id的列表

        Args:
            fname (str): 贴吧名
            lower_permission (int, optional): 获取所有权限级别大于等于lower_permission的user_id. Defaults to 0.
            upper_permission (int, optional): 获取所有权限级别小于等于upper_permission的user_id. Defaults to 5.
            limit (int, optional): 返回数量限制. Defaults to 1.
            offset (int, optional): 偏移. Defaults to 0.

        Returns:
            list[int]: user_id列表
        """

        return await self.database.get_user_id_list(self.fname, lower_permission, upper_permission, limit, offset)

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
            LOG.warning(f"Failed to decode image. reason:{err}")
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
            img_hash_array = cv.img_hash.averageHash(image)
            img_hash = binascii.hexlify(img_hash_array.tobytes()).decode('ascii')
        except Exception as err:
            LOG.warning(f"Failed to get imagehash. reason:{err}")
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
            return await self.database.get_imghash(self.fname, img_hash)
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
            return await self.database.get_imghash_full(self.fname, img_hash)
        return 0, ''
