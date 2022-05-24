# -*- coding:utf-8 -*-
__all__ = ['Database']

import asyncio
import datetime
import functools

import aiomysql

from ._config import CONFIG
from ._logger import get_logger
from ._types import BasicUserInfo

LOG = get_logger()


def translate_fname(func):
    @functools.wraps(func)
    def wrapper(self, fname, *args, **kwargs):
        if not (fname_eng := CONFIG['fname_mapping'].get(fname, None)):
            LOG.error(f"Can not find key:{fname} in name mapping")
            return
        return func(self, fname_eng, *args, **kwargs)

    return wrapper


class Database(object):
    """
    提供与MySQL交互的方法
    """

    __slots__ = ['_db_name', '_pool_recycle', '_pool']

    def __init__(self) -> None:
        self._db_name: str = CONFIG['database'].get('db', 'tieba_cloud_review')
        self._pool_recycle: int = CONFIG['database'].get('pool_recycle', 28800)
        self._pool: aiomysql.Pool = None

    async def enter(self) -> "Database":
        try:
            self._pool: aiomysql.Pool = await aiomysql.create_pool(
                minsize=0,
                maxsize=8,
                pool_recycle=self._pool_recycle,
                db=self._db_name,
                autocommit=True,
                **CONFIG['database'],
            )
        except aiomysql.Error as err:
            LOG.warning(f"Cannot link to the database {self._db_name}. reason:{err}")

        return self

    async def __aenter__(self) -> "Database":
        return await self.enter()

    async def close(self) -> None:
        self._pool.close()
        await self._pool.wait_closed()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def _init_database(self) -> None:
        """
        初始化数据库
        """

        conn: aiomysql.Connection = await aiomysql.connect(autocommit=True, **CONFIG['database'])

        async with conn.cursor() as cursor:
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self._db_name}`")

        self._pool: aiomysql.Pool = await aiomysql.create_pool(
            minsize=0,
            maxsize=30,
            pool_recycle=self._pool_recycle,
            db=self._db_name,
            autocommit=True,
            **CONFIG['database'],
        )

        for fname in CONFIG['fname_mapping'].keys():
            await asyncio.gather(
                self._create_table_id(fname),
                self._create_table_user_id(fname),
                self._create_table_imghash(fname),
                self._create_table_tid_water(fname),
            )
        await asyncio.gather(self._create_table_forum(), self._create_table_user())
        await conn.ensure_closed()

    async def _create_table_forum(self) -> None:
        """
        创建表forum
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "CREATE TABLE IF NOT EXISTS `forum` (`fid` INT PRIMARY KEY, `fname` VARCHAR(36) UNIQUE NOT NULL)"
                )

    async def get_fid(self, fname: str) -> int:
        """
        通过贴吧名获取fid

        Args:
            fname (str): 贴吧名

        Returns:
            int: 该贴吧的fid
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT `fid` FROM `forum` WHERE `fname`=%s", (fname,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to select {fname}. reason:{err}")
            return 0
        else:
            if res_tuple := await cursor.fetchone():
                return int(res_tuple[0])
            return 0

    async def get_fname(self, fid: int) -> str:
        """
        通过fid获取贴吧名

        Args:
            fid (int): fid

        Returns:
            str: 该贴吧的贴吧名
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT `fname` FROM `forum` WHERE `fid`=%s", (fid,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to select {fid}. reason:{err}")
            return ''
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return ''

    async def add_forum(self, fid: int, fname: str) -> bool:
        """
        向表forum添加fid和贴吧名的映射关系

        Args:
            fid (int): fid
            fname (str): 贴吧名

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("INSERT IGNORE INTO `forum` VALUES (%s,%s)", (fid, fname))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to insert {fid}. reason:{err}")
            return False
        return True

    async def _create_table_user(self) -> None:
        """
        创建表user
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "CREATE TABLE IF NOT EXISTS `user` (`user_id` BIGINT PRIMARY KEY, `user_name` VARCHAR(14) NOT NULL DEFAULT '', `portrait` VARCHAR(36) UNIQUE NOT NULL, INDEX `user_name`(user_name))"
                )

    async def get_basic_user_info(self, _id: str | int) -> BasicUserInfo:
        """
        获取简略版用户信息

        Args:
            _id (str | int): 用户id user_id/user_name/portrait

        Returns:
            BasicUserInfo: 简略版用户信息 仅保证包含user_name/portrait/user_id
        """

        user = BasicUserInfo(_id)

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    if user.user_id:
                        await cursor.execute("SELECT * FROM `user` WHERE `user_id`=%s", (user.user_id,))
                    elif user.portrait:
                        await cursor.execute("SELECT * FROM `user` WHERE `portrait`=%s", (user.portrait,))
                    elif user.user_name:
                        await cursor.execute("SELECT * FROM `user` WHERE `user_name`=%s", (user.user_name,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to select {user}. reason:{err}")
            return BasicUserInfo()
        else:
            if res_tuple := await cursor.fetchone():
                user = BasicUserInfo()
                user.user_id = res_tuple[0]
                user.user_name = res_tuple[1]
                user.portrait = res_tuple[2]
                return user
            return BasicUserInfo()

    async def add_user(self, user: BasicUserInfo) -> bool:
        """
        将简略版用户信息添加到表user

        Args:
            user (BasicUserInfo): 待添加的简略版用户信息

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "INSERT IGNORE INTO `user` VALUES (%s,%s,%s)", (user.user_id, user.user_name, user.portrait)
                    )
        except aiomysql.Error as err:
            LOG.warning(f"Failed to insert {user}. reason:{err}")
            return False
        return True

    async def del_user(self, user: BasicUserInfo) -> bool:
        """
        从表user中删除简略版用户信息

        Args:
            user (BasicUserInfo): 待删除的简略版用户信息

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    if user.user_id:
                        await cursor.execute("DELETE FROM `user` WHERE `user_id`=%s", (user.user_id,))
                    elif user.portrait:
                        await cursor.execute("DELETE FROM `user` WHERE `portrait`=%s", (user.portrait,))
                    elif user.user_name:
                        await cursor.execute("DELETE FROM `user` WHERE `user_name`=%s", (user.user_name,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to delete {user}. reason:{err}")
            return False

        LOG.info(f"Successfully deleted {user} from table user")
        return True

    @translate_fname
    async def _create_table_id(self, fname: str) -> None:
        """
        创建表id_{fname}

        Args:
            fname (str): 贴吧名
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `id_{fname}` (`id` BIGINT PRIMARY KEY, `id_last_edit` INT NOT NULL, `record_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
                )
                await cursor.execute(
                    f"""CREATE EVENT IF NOT EXISTS `event_auto_del_id_{fname}` \
                    ON SCHEDULE EVERY 1 DAY STARTS '2000-01-01 00:00:00' \
                    DO DELETE FROM `id_{fname}` WHERE record_time<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)"""
                )

    @translate_fname
    async def add_id(self, fname: str, _id: int, id_last_edit: int = 0) -> bool:
        """
        将id添加到表id_{fname}

        Args:
            fname (str): 贴吧名
            _id (int): tid或pid
            id_last_edit (int): 用于识别id的子对象列表是否发生修改 \
                若该id为tid则id_last_edit应为last_time 若该id为pid则id_last_edit应为reply_num. Defaults to 0.

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"REPLACE INTO `id_{fname}` VALUES (%s,%s,DEFAULT)", (_id, id_last_edit))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to insert {_id}. reason:{err}")
            return False
        return True

    @translate_fname
    async def get_id(self, fname: str, _id: int) -> int:
        """
        获取表id_{fname}中id对应的id_last_edit值

        Args:
            fname (str): 贴吧名
            _id (int): tid或pid

        Returns:
            int: id_last_edit -1表示表中无id
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"SELECT `id_last_edit` FROM `id_{fname}` WHERE `id`=%s", (_id,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to select {_id}. reason:{err}")
            return False
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return -1

    @translate_fname
    async def del_id(self, fname: str, _id: int) -> bool:
        """
        从表id_{fname}中删除id

        Args:
            fname (str): 贴吧名
            _id (int): tid或pid

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"DELETE FROM `id_{fname}` WHERE `id`=%s", (_id,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to delete {_id}. reason:{err}")
            return False

        LOG.info(f"Successfully deleted {_id} from table of {fname}")
        return True

    @translate_fname
    async def del_ids(self, fname: str, hour: int) -> bool:
        """
        删除表id_{fname}中最近hour个小时记录的id

        Args:
            fname (str): 贴吧名
            hour (int): 小时数

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"DELETE FROM `id_{fname}` WHERE `record_time`>(CURRENT_TIMESTAMP() + INTERVAL -%s HOUR)",
                        (hour,),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"Failed to delete id in id_{fname}. reason:{err}")
            return False

        LOG.info(f"Successfully deleted id in id_{fname} within {hour} hour(s)")
        return True

    @translate_fname
    async def _create_table_tid_water(self, fname: str) -> None:
        """
        创建表tid_water_{fname}

        Args:
            fname (str): 贴吧名
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `tid_water_{fname}` (`tid` BIGINT PRIMARY KEY, `is_hide` TINYINT NOT NULL DEFAULT 1, `record_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, INDEX `is_hide`(is_hide))"
                )
                await cursor.execute(
                    f"""CREATE EVENT IF NOT EXISTS `event_auto_del_tid_water_{fname}` \
                ON SCHEDULE EVERY 1 DAY STARTS '2000-01-01 00:00:00' \
                DO DELETE FROM `tid_water_{fname}` WHERE `record_time`<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)"""
                )

    @translate_fname
    async def add_tid(self, fname: str, tid: int, mode: bool) -> bool:
        """
        将tid添加到表tid_water_{fname}

        Args:
            fname (str): 贴吧名
            tid (int): 主题帖tid
            mode (bool): 待恢复状态 True对应待恢复 False对应已恢复

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"REPLACE INTO `tid_water_{fname}` VALUES (%s,%s,DEFAULT)", (tid, mode))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to insert {tid}. reason:{err}")
            return False

        LOG.info(f"Successfully added {tid} to table of {fname}. mode: {mode}")
        return True

    @translate_fname
    async def is_tid_hide(self, fname: str, tid: int) -> bool | None:
        """
        获取表tid_water_{fname}中tid的待恢复状态

        Args:
            fname (str): 贴吧名
            tid (int): 主题帖tid

        Returns:
            bool | None: True表示tid待恢复 False表示tid已恢复 None表示表中无记录
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"SELECT `is_hide` FROM `tid_water_{fname}` WHERE `tid`=%s", (tid,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to select {tid}. reason:{err}")
            return None
        else:
            if res_tuple := await cursor.fetchone():
                return True if res_tuple[0] else False
            return None

    @translate_fname
    async def del_tid(self, fname: str, tid: int) -> bool:
        """
        从表tid_water_{fname}中删除tid

        Args:
            fname (str): 贴吧名
            tid (int): 主题帖tid

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"DELETE FROM `tid_water_{fname}` WHERE `tid`=%s", (tid,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to delete {tid}. reason:{err}")
            return False
        LOG.info(f"Successfully deleted {tid} from table of {fname}")
        return True

    @translate_fname
    async def get_tid_list(self, fname: str, limit: int = 128, offset: int = 0) -> list[int]:
        """
        获取表tid_water_{fname}中待恢复的tid的列表

        Args:
            fname (str): 贴吧名
            limit (int, optional): 返回数量限制. Defaults to 128.
            offset (int, optional): 偏移. Defaults to 0.

        Returns:
            list[int]: tid列表
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"SELECT `tid` FROM `tid_water_{fname}` WHERE `is_hide`=1 LIMIT %s OFFSET %s",
                        (limit, offset),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"Failed to get tids in {fname}. reason:{err}")
            res_list = []
        else:
            res_tuples = await cursor.fetchall()
            res_list = [res_tuple[0] for res_tuple in res_tuples]

        return res_list

    @translate_fname
    async def _create_table_user_id(self, fname: str) -> None:
        """
        创建表user_id_{fname}

        Args:
            fname (str): 贴吧名
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `user_id_{fname}` (`user_id` BIGINT PRIMARY KEY, `permission` TINYINT NOT NULL DEFAULT 0, `note` VARCHAR(64) NOT NULL DEFAULT '', `record_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, INDEX `permission`(permission), INDEX `record_time`(record_time))"
                )

    @translate_fname
    async def add_user_id(self, fname: str, user_id: int, permission: int = 0, note: str = '') -> bool:
        """
        将user_id添加到表user_id_{fname}

        Args:
            fname (str): 贴吧名
            user_id (int): 用户的user_id
            permission (int, optional): 权限级别. Defaults to 0.
            note (str, optional): 备注. Defaults to ''.

        Returns:
            bool: 操作是否成功
        """

        if not user_id:
            return

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"REPLACE INTO `user_id_{fname}` VALUES (%s,%s,%s,DEFAULT)", (user_id, permission, note)
                    )
        except aiomysql.Error as err:
            LOG.warning(f"Failed to insert {user_id}. reason:{err}")
            return False
        LOG.info(f"Successfully added {user_id} to table of {fname}. permission: {permission} note: {note}")
        return True

    @translate_fname
    async def del_user_id(self, fname: str, user_id: int) -> bool:
        """
        从表user_id_{fname}中删除user_id

        Args:
            fname (str): 贴吧名
            user_id (int): 用户的user_id

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"DELETE FROM `user_id_{fname}` WHERE `user_id`=%s", (user_id,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to delete {user_id}. reason:{err}")
            return False
        LOG.info(f"Successfully deleted {user_id} from table of {fname}")
        return True

    @translate_fname
    async def get_user_id(self, fname: str, user_id: int) -> int:
        """
        获取表user_id_{fname}中user_id的权限级别

        Args:
            fname (str): 贴吧名
            user_id (int): 用户的user_id

        Returns:
            int: 权限级别
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"SELECT `permission` FROM `user_id_{fname}` WHERE `user_id`=%s", (user_id,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to get {user_id}. reason:{err}")
            return 0
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return 0

    @translate_fname
    async def get_user_id_full(self, fname: str, user_id: int) -> tuple[int, str, datetime.datetime]:
        """
        获取表user_id_{fname}中user_id的完整信息

        Args:
            fname (str): 贴吧名
            user_id (int): 用户的user_id

        Returns:
            tuple[int, str, datetime.datetime]: 权限级别, 备注, 记录时间
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"SELECT `permission`,`note`,`record_time` FROM `user_id_{fname}` WHERE `user_id`=%s",
                        (user_id,),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"Failed to get full {user_id}. reason:{err}")
            return 0, '', datetime.datetime(1970, 1, 1)
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple
            return 0, '', datetime.datetime(1970, 1, 1)

    @translate_fname
    async def get_user_id_list(
        self, fname: str, lower_permission: int = 0, upper_permission: int = 5, limit: int = 1, offset: int = 0
    ) -> list[int]:
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

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"SELECT `user_id` FROM `user_id_{fname}` WHERE `permission`>=%s AND `permission`<=%s ORDER BY `record_time` DESC LIMIT %s OFFSET %s",
                        (lower_permission, upper_permission, limit, offset),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"Failed to get user_ids in {fname}. reason:{err}")
            res_list = []
        else:
            res_tuples = await cursor.fetchall()
            res_list = [res_tuple[0] for res_tuple in res_tuples]

        return res_list

    @translate_fname
    async def _create_table_imghash(self, fname: str) -> None:
        """
        创建表imghash_{fname}

        Args:
            fname (str): 贴吧名
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `imghash_{fname}` (`img_hash` CHAR(16) PRIMARY KEY, `raw_hash` CHAR(40) UNIQUE NOT NULL, `permission` TINYINT NOT NULL DEFAULT 0, `note` VARCHAR(64) NOT NULL DEFAULT '', INDEX `permission`(permission))"
                )

    @translate_fname
    async def add_imghash(self, fname: str, img_hash: str, raw_hash: str, permission: int = 0, note: str = '') -> bool:
        """
        将img_hash添加到表imghash_{fname}

        Args:
            fname (str): 贴吧名
            img_hash (str): 图像的phash
            raw_hash (str): 贴吧图床hash
            permission (int, optional): 封锁级别. Defaults to 0.
            note (str, optional): 备注. Defaults to ''.

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"REPLACE INTO `imghash_{fname}` VALUES (%s,%s,%s,%s)",
                        (img_hash, raw_hash, permission, note),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"Failed to insert {img_hash}. reason:{err}")
            return False

        LOG.info(f"Successfully added {img_hash} to table of {fname}. permission: {permission} note: {note}")
        return True

    @translate_fname
    async def del_imghash(self, fname: str, img_hash: str) -> bool:
        """
        从imghash_{fname}中删除img_hash

        Args:
            fname (str): 贴吧名
            img_hash (str): 图像的phash

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"DELETE FROM `imghash_{fname}` WHERE `img_hash`=%s", (img_hash,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to delete {img_hash}. reason:{err}")
            return False

        LOG.info(f"Successfully deleted {img_hash} from table of {fname}")
        return True

    @translate_fname
    async def get_imghash(self, fname: str, img_hash: str) -> int:
        """
        获取表imghash_{fname}中img_hash的封锁级别

        Args:
            fname (str): 贴吧名
            img_hash (str): 图像的phash

        Returns:
            int: 封锁级别
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"SELECT `permission` FROM `imghash_{fname}` WHERE `img_hash`=%s", (img_hash,))
        except aiomysql.Error as err:
            LOG.warning(f"Failed to select {img_hash}. reason:{err}")
            return False
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return 0

    @translate_fname
    async def get_imghash_full(self, fname: str, img_hash: str) -> tuple[int, str]:
        """
        获取表imghash_{fname}中img_hash的完整信息

        Args:
            fname (str): 贴吧名
            img_hash (str): 图像的phash

        Returns:
            tuple[int, str]: 封锁级别, 备注
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"SELECT `permission`,`note` FROM `imghash_{fname}` WHERE `img_hash`=%s", (img_hash,)
                    )
        except aiomysql.Error as err:
            LOG.warning(f"Failed to select {img_hash}. reason:{err}")
            return 0, ''
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple
            return 0, ''
