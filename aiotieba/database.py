# -*- coding:utf-8 -*-
__all__ = ['Database']

import asyncio
import datetime
from typing import List, Optional, Tuple, Union

import aiomysql

from .config import CONFIG
from .log import LOG
from .typedef import BasicUserInfo


class Database(object):
    """
    提供与MySQL交互的方法
    """

    __slots__ = ['_db_name', '_pool_recycle', '_pool']

    def __init__(self) -> None:
        self._db_name: str = CONFIG['Database'].get('db', 'tieba_cloud_review')
        self._pool_recycle: int = CONFIG['Database'].get('pool_recycle', 28800)
        self._pool: aiomysql.Pool = None

    async def enter(self) -> "Database":
        try:
            self._pool: aiomysql.Pool = await aiomysql.create_pool(
                minsize=0,
                maxsize=8,
                pool_recycle=self._pool_recycle,
                db=self._db_name,
                autocommit=True,
                **CONFIG['Database'],
            )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. 无法连接数据库`{self._db_name}`请检查配置文件中的`Database`字段是否填写正确")

        return self

    async def __aenter__(self) -> "Database":
        return await self.enter()

    async def close(self) -> None:
        self._pool.close()
        await self._pool.wait_closed()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def init_database(self, fnames: List[str]) -> None:
        """
        初始化各个fname对应贴吧的数据库

        Args:
            fnames (list[str]): 贴吧名列表
        """

        conn: aiomysql.Connection = await aiomysql.connect(autocommit=True, **CONFIG['Database'])

        async with conn.cursor() as cursor:
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self._db_name}`")

        self._pool: aiomysql.Pool = await aiomysql.create_pool(
            minsize=0,
            maxsize=32,
            pool_recycle=self._pool_recycle,
            db=self._db_name,
            autocommit=True,
            **CONFIG['Database'],
        )

        for fname in fnames:
            await asyncio.gather(
                self._create_table_id(fname),
                self._create_table_user_id(fname),
                self._create_table_imghash(fname),
                self._create_table_tid(fname),
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
                    "CREATE TABLE IF NOT EXISTS `forum` \
                    (`fid` INT PRIMARY KEY, `fname` VARCHAR(36) UNIQUE NOT NULL)"
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
            LOG.warning(f"{err}. fname={fname}")
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
            LOG.warning(f"{err}. fid={fid}")
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
            LOG.warning(f"{err}. fname={fname} fid={fid}")
            return False
        return True

    async def _create_table_user(self) -> None:
        """
        创建表user
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "CREATE TABLE IF NOT EXISTS `user` \
                    (`user_id` BIGINT PRIMARY KEY, `user_name` VARCHAR(14) NOT NULL DEFAULT '', `portrait` VARCHAR(36) UNIQUE NOT NULL, \
                    INDEX `user_name`(user_name))"
                )

    async def get_basic_user_info(self, _id: Union[str, int]) -> BasicUserInfo:
        """
        获取简略版用户信息

        Args:
            _id (str | int): 待补全用户的id user_id/user_name/portrait

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
            LOG.warning(f"{err}. user={user}")
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
            LOG.warning(f"{err}. user={user}")
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
            LOG.warning(f"{err}. user={user}")
            return False

        LOG.info(f"Succeeded. user={user}")
        return True

    async def _create_table_id(self, fname: str) -> None:
        """
        创建表id_{fname}

        Args:
            fname (str): 贴吧名
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `id_{fname}` \
                    (`id` BIGINT PRIMARY KEY, `tag` INT NOT NULL, `record_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
                )
                await cursor.execute(
                    f"""CREATE EVENT IF NOT EXISTS `event_auto_del_id_{fname}` \
                    ON SCHEDULE EVERY 1 DAY STARTS '2000-01-01 00:00:00' \
                    DO DELETE FROM `id_{fname}` WHERE record_time<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)"""
                )

    async def add_id(self, fname: str, /, _id: int, *, tag: int = 0) -> bool:
        """
        将id添加到表id_{fname}

        Args:
            fname (str): 贴吧名
            _id (int): tid或pid
            tag (int, optional): 自定义标签. Defaults to 0.

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"REPLACE INTO `id_{fname}` VALUES (%s,%s,DEFAULT)", (_id, tag))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={fname} id={_id}")
            return False
        return True

    async def get_id(self, fname: str, /, _id: int) -> Optional[int]:
        """
        获取表id_{fname}中id对应的tag值

        Args:
            fname (str): 贴吧名
            _id (int): tid或pid

        Returns:
            int | None: 自定义标签 None表示表中无id
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"SELECT `tag` FROM `id_{fname}` WHERE `id`=%s", (_id,))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={fname} id={_id}")
            return False
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return None

    async def del_id(self, fname: str, /, _id: int) -> bool:
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
            LOG.warning(f"{err}. forum={fname} id={_id}")
            return False

        LOG.info(f"Succeeded. forum={fname} id={_id}")
        return True

    async def del_ids(self, fname: str, /, hour: int) -> bool:
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
            LOG.warning(f"{err}. forum={fname}")
            return False

        LOG.info(f"Succeeded. forum={fname} hour={hour}")
        return True

    async def _create_table_tid(self, fname: str) -> None:
        """
        创建表tid_{fname}

        Args:
            fname (str): 贴吧名
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `tid_{fname}` \
                    (`tid` BIGINT PRIMARY KEY, `tag` TINYINT NOT NULL DEFAULT 1, `record_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
                    INDEX `tag`(tag))"
                )
                await cursor.execute(
                    f"""CREATE EVENT IF NOT EXISTS `event_auto_del_tid_{fname}` \
                    ON SCHEDULE EVERY 1 DAY STARTS '2000-01-01 00:00:00' \
                    DO DELETE FROM `tid_{fname}` WHERE `record_time`<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)"""
                )

    async def add_tid(self, fname: str, /, tid: int, *, tag: int = 0) -> bool:
        """
        将tid添加到表tid_{fname}

        Args:
            fname (str): 贴吧名
            tid (int): 主题帖tid
            tag (int, optional): 自定义标签. Defaults to 0.

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"REPLACE INTO `tid_{fname}` VALUES (%s,%s,DEFAULT)", (tid, tag))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={fname} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname} tid={tid} tag={tag}")
        return True

    async def get_tid(self, fname: str, /, tid: int) -> Optional[int]:
        """
        获取表tid_{fname}中tid对应的tag值

        Args:
            fname (str): 贴吧名
            tid (int): 主题帖tid

        Returns:
            int | None: 自定义标签 None表示表中无记录
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"SELECT `tag` FROM `tid_{fname}` WHERE `tid`=%s", (tid,))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={fname} tid={tid}")
            return None
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return None

    async def del_tid(self, fname: str, /, tid: int) -> bool:
        """
        从表tid_{fname}中删除tid

        Args:
            fname (str): 贴吧名
            tid (int): 主题帖tid

        Returns:
            bool: 操作是否成功
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"DELETE FROM `tid_{fname}` WHERE `tid`=%s", (tid,))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={fname} tid={tid}")
            return False
        LOG.info(f"Succeeded. forum={fname} tid={tid}")
        return True

    async def get_tid_list(self, fname: str, /, tag: int = 0, *, limit: int = 128, offset: int = 0) -> List[int]:
        """
        获取表tid_{fname}中对应tag的tid列表

        Args:
            fname (str): 贴吧名
            tag (int, optional): 待匹配的tag值. Defaults to 0.
            limit (int, optional): 返回数量限制. Defaults to 128.
            offset (int, optional): 偏移. Defaults to 0.

        Returns:
            list[int]: tid列表
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"SELECT `tid` FROM `tid_{fname}` WHERE `tag`=%s LIMIT %s OFFSET %s",
                        (tag, limit, offset),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={fname}")
            res_list = []
        else:
            res_tuples = await cursor.fetchall()
            res_list = [res_tuple[0] for res_tuple in res_tuples]

        return res_list

    async def _create_table_user_id(self, fname: str) -> None:
        """
        创建表user_id_{fname}

        Args:
            fname (str): 贴吧名
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `user_id_{fname}` \
                    (`user_id` BIGINT PRIMARY KEY, `permission` TINYINT NOT NULL DEFAULT 0, `note` VARCHAR(64) NOT NULL DEFAULT '', `record_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, \
                    INDEX `permission`(permission), INDEX `record_time`(record_time))"
                )

    async def add_user_id(self, fname: str, /, user_id: int, *, permission: int = 0, note: str = '') -> bool:
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
            return False

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"REPLACE INTO `user_id_{fname}` VALUES (%s,%s,%s,DEFAULT)", (user_id, permission, note)
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={fname} user_id={user_id}")
            return False
        LOG.info(f"Succeeded. forum={fname} user_id={user_id} permission={permission}")
        return True

    async def del_user_id(self, fname: str, /, user_id: int) -> bool:
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
            LOG.warning(f"{err}. forum={fname} user_id={user_id}")
            return False
        LOG.info(f"Succeeded. forum={fname} user_id={user_id}")
        return True

    async def get_user_id(self, fname: str, /, user_id: int) -> int:
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
            LOG.warning(f"{err}. forum={fname} user_id={user_id}")
            return 0
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return 0

    async def get_user_id_full(self, fname: str, /, user_id: int) -> Tuple[int, str, datetime.datetime]:
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
            LOG.warning(f"{err}. forum={fname} user_id={user_id}")
            return 0, '', datetime.datetime(1970, 1, 1)
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple
            return 0, '', datetime.datetime(1970, 1, 1)

    async def get_user_id_list(
        self, fname: str, /, lower_permission: int = 0, upper_permission: int = 5, *, limit: int = 1, offset: int = 0
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

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"SELECT `user_id` FROM `user_id_{fname}` WHERE `permission`>=%s AND `permission`<=%s ORDER BY `record_time` DESC LIMIT %s OFFSET %s",
                        (lower_permission, upper_permission, limit, offset),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={fname}")
            res_list = []
        else:
            res_tuples = await cursor.fetchall()
            res_list = [res_tuple[0] for res_tuple in res_tuples]

        return res_list

    async def _create_table_imghash(self, fname: str) -> None:
        """
        创建表imghash_{fname}

        Args:
            fname (str): 贴吧名
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `imghash_{fname}` \
                    (`img_hash` CHAR(16) PRIMARY KEY, `raw_hash` CHAR(40) UNIQUE NOT NULL, `permission` TINYINT NOT NULL DEFAULT 0, `note` VARCHAR(64) NOT NULL DEFAULT '', `record_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, \
                    INDEX `permission`(permission), INDEX `record_time`(record_time))"
                )

    async def add_imghash(
        self, fname: str, /, img_hash: str, raw_hash: str, *, permission: int = 0, note: str = ''
    ) -> bool:
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
                        f"REPLACE INTO `imghash_{fname}` VALUES (%s,%s,%s,%s,DEFAULT)",
                        (img_hash, raw_hash, permission, note),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={fname} img_hash={img_hash}")
            return False

        LOG.info(f"Succeeded. forum={fname} img_hash={img_hash} permission={permission}")
        return True

    async def del_imghash(self, fname: str, /, img_hash: str) -> bool:
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
            LOG.warning(f"{err}. forum={fname} img_hash={img_hash}")
            return False

        LOG.info(f"Succeeded. forum={fname} img_hash={img_hash}")
        return True

    async def get_imghash(self, fname: str, /, img_hash: str) -> int:
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
            LOG.warning(f"{err}. forum={fname} img_hash={img_hash}")
            return False
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return 0

    async def get_imghash_full(self, fname: str, /, img_hash: str) -> Tuple[int, str]:
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
            LOG.warning(f"{err}. forum={fname} img_hash={img_hash}")
            return 0, ''
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple
            return 0, ''
