__all__ = ['Database']

import asyncio
import datetime
from typing import Final, List, Optional, Tuple, Union

import aiomysql

from ._config import CONFIG
from ._logger import LOG
from .typedefs import BasicUserInfo


class Database(object):
    """
    与MySQL交互

    Args:
        fname (str): 操作的目标贴吧名. Defaults to ''.

    Attributes:
        fname (str): 操作的目标贴吧名
    """

    __slots__ = ['fname', '_pool']

    _default_port: Final[int] = 3306
    _default_db_name: Final[str] = 'aiotieba'
    _default_minsize: Final[int] = 0
    _default_maxsize: Final[int] = 16
    _default_pool_recycle: Final[int] = 28800

    def __init__(self, fname: str = '') -> None:
        self.fname: str = fname
        self._pool: aiomysql.Pool = None

    async def __aenter__(self) -> "Database":
        try:
            await self._create_pool()
        except aiomysql.Error as err:
            LOG.warning(f"{err}. 无法连接数据库 请检查配置文件中的`Database`字段是否填写正确")

        return self

    async def close(self) -> None:
        if self._pool is not None:
            self._pool.close()
            await self._pool.wait_closed()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def _create_pool(self) -> None:
        """
        创建连接池
        """

        db_config: dict = CONFIG['Database']
        self._pool: aiomysql.Pool = await aiomysql.create_pool(
            user=db_config['user'],
            password=db_config['password'],
            db=db_config.get('db', self._default_db_name),
            minsize=db_config.get('minsize', self._default_minsize),
            maxsize=db_config.get('maxsize', self._default_maxsize),
            pool_recycle=db_config.get('pool_recycle', self._default_pool_recycle),
            loop=asyncio.get_running_loop(),
            autocommit=True,
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', self._default_port),
            unix_socket=db_config.get('unix_socket', None),
        )

    async def create_database(self) -> None:
        """
        创建并初始化数据库
        """

        db_config: dict = CONFIG['Database']
        conn: aiomysql.Connection = await aiomysql.connect(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', self._default_port),
            user=db_config['user'],
            password=db_config['password'],
            unix_socket=db_config.get('unix_socket', None),
            autocommit=True,
            loop=asyncio.get_running_loop(),
        )

        async with conn.cursor() as cursor:
            db_name = db_config.get('db', self._default_db_name)
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")

        await self._create_pool()

        coros = [
            self._create_table_forum(),
            self._create_table_user(),
        ]
        if self.fname:
            coros += [
                self._create_table_id(),
                self._create_table_user_id(),
                self._create_table_imghash(),
                self._create_table_tid(),
            ]
        await asyncio.gather(*coros)

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
        通过贴吧名获取forum_id

        Args:
            fname (str): 贴吧名

        Returns:
            int: 该贴吧的forum_id
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT `fid` FROM `forum` WHERE `fname`=%s", (fname,))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. fname={self.fname}")
            return 0
        else:
            if res_tuple := await cursor.fetchone():
                return int(res_tuple[0])
            return 0

    async def get_fname(self, fid: int) -> str:
        """
        通过forum_id获取贴吧名

        Args:
            fid (int): forum_id

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
        向表forum添加forum_id和贴吧名的映射关系

        Args:
            fid (int): forum_id
            fname (str): 贴吧名

        Returns:
            bool: True成功 False失败
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("INSERT IGNORE INTO `forum` VALUES (%s,%s)", (fid, fname))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. fname={self.fname} fid={fid}")
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
                    else:
                        raise ValueError("用户属性为空")
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
            bool: True成功 False失败
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
            bool: True成功 False失败
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
                    else:
                        raise ValueError("用户属性为空")
        except aiomysql.Error as err:
            LOG.warning(f"{err}. user={user}")
            return False

        LOG.info(f"Succeeded. user={user}")
        return True

    async def _create_table_id(self) -> None:
        """
        创建表id_{self.fname}
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `id_{self.fname}` \
                    (`id` BIGINT PRIMARY KEY, `tag` INT NOT NULL, `record_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
                )
                await cursor.execute(
                    f"""CREATE EVENT IF NOT EXISTS `event_auto_del_id_{self.fname}` \
                    ON SCHEDULE EVERY 1 DAY STARTS '2000-01-01 00:00:00' \
                    DO DELETE FROM `id_{self.fname}` WHERE record_time<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)"""
                )

    async def add_id(self, _id: int, *, tag: int = 0) -> bool:
        """
        将id添加到表id_{self.fname}

        Args:
            _id (int): tid或pid
            tag (int, optional): 自定义标签. Defaults to 0.

        Returns:
            bool: True成功 False失败
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"REPLACE INTO `id_{self.fname}` VALUES (%s,%s,DEFAULT)", (_id, tag))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} id={_id}")
            return False
        return True

    async def get_id(self, _id: int) -> Optional[int]:
        """
        获取表id_{self.fname}中id对应的tag值

        Args:
            _id (int): tid或pid

        Returns:
            int | None: 自定义标签 None表示表中无id
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"SELECT `tag` FROM `id_{self.fname}` WHERE `id`=%s", (_id,))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} id={_id}")
            return False
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return None

    async def del_id(self, _id: int) -> bool:
        """
        从表id_{self.fname}中删除id

        Args:
            _id (int): tid或pid

        Returns:
            bool: True成功 False失败
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"DELETE FROM `id_{self.fname}` WHERE `id`=%s", (_id,))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} id={_id}")
            return False

        LOG.info(f"Succeeded. forum={self.fname} id={_id}")
        return True

    async def del_ids(self, hour: int) -> bool:
        """
        删除表id_{self.fname}中最近hour个小时记录的id

        Args:
            hour (int): 小时数

        Returns:
            bool: True成功 False失败
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"DELETE FROM `id_{self.fname}` WHERE `record_time`>(CURRENT_TIMESTAMP() + INTERVAL -%s HOUR)",
                        (hour,),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname}")
            return False

        LOG.info(f"Succeeded. forum={self.fname} hour={hour}")
        return True

    async def _create_table_tid(self) -> None:
        """
        创建表tid_{self.fname}
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `tid_{self.fname}` \
                    (`tid` BIGINT PRIMARY KEY, `tag` TINYINT NOT NULL DEFAULT 1, `record_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
                    INDEX `tag`(tag))"
                )
                await cursor.execute(
                    f"""CREATE EVENT IF NOT EXISTS `event_auto_del_tid_{self.fname}` \
                    ON SCHEDULE EVERY 1 DAY STARTS '2000-01-01 00:00:00' \
                    DO DELETE FROM `tid_{self.fname}` WHERE `record_time`<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)"""
                )

    async def add_tid(self, tid: int, *, tag: int = 0) -> bool:
        """
        将tid添加到表tid_{self.fname}

        Args:
            tid (int): 主题帖tid
            tag (int, optional): 自定义标签. Defaults to 0.

        Returns:
            bool: True成功 False失败
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"REPLACE INTO `tid_{self.fname}` VALUES (%s,%s,DEFAULT)", (tid, tag))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={self.fname} tid={tid} tag={tag}")
        return True

    async def get_tid(self, tid: int) -> Optional[int]:
        """
        获取表tid_{self.fname}中tid对应的tag值

        Args:
            tid (int): 主题帖tid

        Returns:
            int | None: 自定义标签 None表示表中无记录
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"SELECT `tag` FROM `tid_{self.fname}` WHERE `tid`=%s", (tid,))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} tid={tid}")
            return None
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return None

    async def del_tid(self, tid: int) -> bool:
        """
        从表tid_{self.fname}中删除tid

        Args:
            tid (int): 主题帖tid

        Returns:
            bool: True成功 False失败
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"DELETE FROM `tid_{self.fname}` WHERE `tid`=%s", (tid,))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} tid={tid}")
            return False
        LOG.info(f"Succeeded. forum={self.fname} tid={tid}")
        return True

    async def get_tid_list(self, tag: int = 0, *, limit: int = 128, offset: int = 0) -> List[int]:
        """
        获取表tid_{self.fname}中对应tag的tid列表

        Args:
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
                        f"SELECT `tid` FROM `tid_{self.fname}` WHERE `tag`=%s LIMIT %s OFFSET %s",
                        (tag, limit, offset),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname}")
            res_list = []
        else:
            res_tuples = await cursor.fetchall()
            res_list = [res_tuple[0] for res_tuple in res_tuples]

        return res_list

    async def _create_table_user_id(self) -> None:
        """
        创建表user_id_{self.fname}
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `user_id_{self.fname}` \
                    (`user_id` BIGINT PRIMARY KEY, `permission` TINYINT NOT NULL DEFAULT 0, `note` VARCHAR(64) NOT NULL DEFAULT '', `record_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, \
                    INDEX `permission`(permission), INDEX `record_time`(record_time))"
                )

    async def add_user_id(self, user_id: int, /, permission: int = 0, *, note: str = '') -> bool:
        """
        将user_id添加到表user_id_{self.fname}

        Args:
            user_id (int): 用户的user_id
            permission (int, optional): 权限级别. Defaults to 0.
            note (str, optional): 备注. Defaults to ''.

        Returns:
            bool: True成功 False失败
        """

        if not user_id:
            return False

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"REPLACE INTO `user_id_{self.fname}` VALUES (%s,%s,%s,DEFAULT)", (user_id, permission, note)
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} user_id={user_id}")
            return False
        LOG.info(f"Succeeded. forum={self.fname} user_id={user_id} permission={permission}")
        return True

    async def del_user_id(self, user_id: int) -> bool:
        """
        从表user_id_{self.fname}中删除user_id

        Args:
            user_id (int): 用户的user_id

        Returns:
            bool: True成功 False失败
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"DELETE FROM `user_id_{self.fname}` WHERE `user_id`=%s", (user_id,))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} user_id={user_id}")
            return False
        LOG.info(f"Succeeded. forum={self.fname} user_id={user_id}")
        return True

    async def get_user_id(self, user_id: int) -> int:
        """
        获取表user_id_{self.fname}中user_id的权限级别

        Args:
            user_id (int): 用户的user_id

        Returns:
            int: 权限级别
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"SELECT `permission` FROM `user_id_{self.fname}` WHERE `user_id`=%s", (user_id,)
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} user_id={user_id}")
            return 0
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return 0

    async def get_user_id_full(self, user_id: int) -> Tuple[int, str, datetime.datetime]:
        """
        获取表user_id_{self.fname}中user_id的完整信息

        Args:
            user_id (int): 用户的user_id

        Returns:
            tuple[int, str, datetime.datetime]: 权限级别, 备注, 记录时间
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"SELECT `permission`,`note`,`record_time` FROM `user_id_{self.fname}` WHERE `user_id`=%s",
                        (user_id,),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} user_id={user_id}")
            return 0, '', datetime.datetime(1970, 1, 1)
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple
            return 0, '', datetime.datetime(1970, 1, 1)

    async def get_user_id_list(
        self, lower_permission: int = 0, upper_permission: int = 5, *, limit: int = 1, offset: int = 0
    ) -> List[int]:
        """
        获取表user_id_{self.fname}中user_id的列表

        Args:
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
                        f"SELECT `user_id` FROM `user_id_{self.fname}` WHERE `permission`>=%s AND `permission`<=%s ORDER BY `record_time` DESC LIMIT %s OFFSET %s",
                        (lower_permission, upper_permission, limit, offset),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname}")
            res_list = []
        else:
            res_tuples = await cursor.fetchall()
            res_list = [res_tuple[0] for res_tuple in res_tuples]

        return res_list

    async def _create_table_imghash(self) -> None:
        """
        创建表imghash_{self.fname}
        """

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS `imghash_{self.fname}` \
                    (`img_hash` CHAR(16) PRIMARY KEY, `raw_hash` CHAR(40) UNIQUE NOT NULL, `permission` TINYINT NOT NULL DEFAULT 0, `note` VARCHAR(64) NOT NULL DEFAULT '', `record_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, \
                    INDEX `permission`(permission), INDEX `record_time`(record_time))"
                )

    async def add_imghash(self, img_hash: str, raw_hash: str, /, permission: int = 0, *, note: str = '') -> bool:
        """
        将img_hash添加到表imghash_{self.fname}

        Args:
            img_hash (str): 图像的phash
            raw_hash (str): 贴吧图床hash
            permission (int, optional): 封锁级别. Defaults to 0.
            note (str, optional): 备注. Defaults to ''.

        Returns:
            bool: True成功 False失败
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"REPLACE INTO `imghash_{self.fname}` VALUES (%s,%s,%s,%s,DEFAULT)",
                        (img_hash, raw_hash, permission, note),
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} img_hash={img_hash}")
            return False

        LOG.info(f"Succeeded. forum={self.fname} img_hash={img_hash} permission={permission}")
        return True

    async def del_imghash(self, img_hash: str) -> bool:
        """
        从imghash_{self.fname}中删除img_hash

        Args:
            img_hash (str): 图像的phash

        Returns:
            bool: True成功 False失败
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"DELETE FROM `imghash_{self.fname}` WHERE `img_hash`=%s", (img_hash,))
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} img_hash={img_hash}")
            return False

        LOG.info(f"Succeeded. forum={self.fname} img_hash={img_hash}")
        return True

    async def get_imghash(self, img_hash: str) -> int:
        """
        获取表imghash_{self.fname}中img_hash的封锁级别

        Args:
            img_hash (str): 图像的phash

        Returns:
            int: 封锁级别
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"SELECT `permission` FROM `imghash_{self.fname}` WHERE `img_hash`=%s", (img_hash,)
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} img_hash={img_hash}")
            return False
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple[0]
            return 0

    async def get_imghash_full(self, img_hash: str) -> Tuple[int, str]:
        """
        获取表imghash_{self.fname}中img_hash的完整信息

        Args:
            img_hash (str): 图像的phash

        Returns:
            tuple[int, str]: 封锁级别, 备注
        """

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"SELECT `permission`,`note` FROM `imghash_{self.fname}` WHERE `img_hash`=%s", (img_hash,)
                    )
        except aiomysql.Error as err:
            LOG.warning(f"{err}. forum={self.fname} img_hash={img_hash}")
            return 0, ''
        else:
            if res_tuple := await cursor.fetchone():
                return res_tuple
            return 0, ''
