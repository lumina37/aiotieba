# -*- coding:utf-8 -*-
__all__ = ['get_database']

import asyncio
import datetime
import functools
import sys
from collections.abc import AsyncIterable

import pymysql

from ._config import CONFIG
from ._logger import get_logger
from ._types import BasicUserInfo

LOG = get_logger()


def translate_tieba_name(func):

    @functools.wraps(func)
    def wrapper(self, tieba_name, *args, **kwargs):
        if not (tieba_name := CONFIG['tieba_name_mapping'].get(tieba_name, None)):
            LOG.error(f"Can not find key:{tieba_name} in name mapping")
            return
        return func(self, tieba_name, *args, **kwargs)

    return wrapper


class Database(object):
    """
    提供与MySQL交互的方法

    Args:
        db_name (str, optional): 连接的数据库名
    """

    __slots__ = ['db_name', '_conn', '_cursor']

    def __init__(self, db_name: str) -> None:

        self.db_name = db_name

        try:
            self._conn = pymysql.connect(**CONFIG['database'], database=self.db_name)
        except pymysql.Error as err:
            LOG.warning(f"Cannot link to the database {db_name}. reason:{err}")
            self._init_database()
        else:
            self._cursor = self._conn.cursor()

    def close(self) -> None:
        self._cursor.close()
        self._conn.commit()
        self._conn.close()

    async def _init_database(self) -> None:
        """
        初始化数据库
        """

        self._conn = pymysql.connect(**CONFIG['database'])
        self._cursor = self._conn.cursor()
        self._cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.db_name}`")
        self._cursor.execute(f"USE `{self.db_name}`")

        coros = []
        for tieba_name in CONFIG['tieba_name_mapping'].keys():
            coros.extend([
                self._create_table_id(tieba_name),
                self._create_table_user_id(tieba_name),
                self._create_table_img_blacklist(tieba_name),
                self._create_table_tid_water(tieba_name)
            ])
        await asyncio.gather(*coros, self._create_table_forum(), self._create_table_user())

    async def ping(self) -> bool:
        """
        检测连接状态 若断连则尝试重连

        Returns:
            bool: 是否连接成功
        """

        try:
            self._conn.ping()
        except pymysql.Error as err:
            LOG.warning(f"Failed to ping sql. reason:{err}")
            return False
        else:
            if not self._conn.open:
                LOG.warning("Failed to reconnect database")
                return False
            else:
                return True

    async def _create_table_forum(self) -> None:
        """
        创建表forum
        """

        self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS `forum` (`fid` INT PRIMARY KEY, `tieba_name` VARCHAR(36) UNIQUE)")

    async def get_fid(self, tieba_name: str) -> int:
        """
        通过贴吧名获取forum_id

        Args:
            tieba_name (str): 贴吧名

        Returns:
            int: 该贴吧的forum_id
        """

        try:
            self._cursor.execute("SELECT `fid` FROM `forum` WHERE `tieba_name`=%s", (tieba_name, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to select {tieba_name}. reason:{err}")
            return 0
        else:
            if res_tuple := self._cursor.fetchone():
                return int(res_tuple[0])
            else:
                return 0

    async def get_tieba_name(self, fid: int) -> str:
        """
        通过forum_id获取贴吧名

        Args:
            fid (int): forum_id

        Returns:
            str: 该贴吧的贴吧名
        """

        try:
            self._cursor.execute("SELECT `tieba_name` FROM `forum` WHERE `fid`=%s", (fid, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to select {fid}. reason:{err}")
            return ''
        else:
            if res_tuple := self._cursor.fetchone():
                return res_tuple[0]
            else:
                return ''

    async def add_forum(self, fid: int, tieba_name: str) -> bool:
        """
        向表forum添加forum_id和贴吧名的映射关系

        Args:
            fid (int): forum_id
            tieba_name (str): 贴吧名

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute("INSERT IGNORE INTO `forum` VALUES (%s,%s)", (fid, tieba_name))
        except pymysql.Error as err:
            LOG.warning(f"Failed to insert {fid}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            self._conn.commit()
            return True

    async def _create_table_user(self) -> None:
        """
        创建表user
        """

        self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS `user` (`user_id` BIGINT PRIMARY KEY, `user_name` VARCHAR(14), `portrait` VARCHAR(36) UNIQUE, INDEX `user_name`(user_name))"
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
            if user.user_id:
                self._cursor.execute("SELECT * FROM `user` WHERE `user_id`=%s", (user.user_id, ))
            elif user.portrait:
                self._cursor.execute("SELECT * FROM `user` WHERE `portrait`=%s", (user.portrait, ))
            elif user.user_name:
                self._cursor.execute("SELECT * FROM `user` WHERE `user_name`=%s", (user.user_name, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to select {user}. reason:{err}")
            return BasicUserInfo()
        else:
            if res_tuple := self._cursor.fetchone():
                user = BasicUserInfo()
                user.user_id = res_tuple[0]
                user.user_name = res_tuple[1]
                user.portrait = res_tuple[2]
                return user
            else:
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
            self._cursor.execute("INSERT IGNORE INTO `user` VALUES (%s,%s,%s)",
                                 (user.user_id, user.user_name, user.portrait))
        except pymysql.Error as err:
            LOG.warning(f"Failed to insert {user}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            self._conn.commit()
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
            if user.user_id:
                self._cursor.execute("DELETE FROM `user` WHERE `user_id`=%s", (user.user_id, ))
            elif user.portrait:
                self._cursor.execute("DELETE FROM `user` WHERE `portrait`=%s", (user.portrait, ))
            elif user.user_name:
                self._cursor.execute("DELETE FROM `user` WHERE `user_name`=%s", (user.user_name, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to delete {user}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            LOG.info(f"Successfully deleted {user} from table user")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def _create_table_id(self, tieba_name: str) -> None:
        """
        创建表id_{tieba_name}

        Args:
            tieba_name (str): 贴吧名
        """

        self._cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `id_{tieba_name}` (`id` BIGINT PRIMARY KEY, `id_last_edit` INT NOT NULL, `record_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        self._cursor.execute(f"""CREATE EVENT IF NOT EXISTS `event_auto_del_id_{tieba_name}`
        ON SCHEDULE
        EVERY 1 DAY STARTS '2000-01-01 00:00:00'
        DO
        DELETE FROM `id_{tieba_name}` WHERE record_time<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)""")

    @translate_tieba_name
    async def add_id(self, tieba_name: str, _id: int, id_last_edit: int = 0) -> bool:
        """
        将id添加到表id_{tieba_name}

        Args:
            tieba_name (str): 贴吧名
            _id (int): tid或pid
            id_last_edit (int): 用于识别id的子对象列表是否发生修改 若该id为tid则id_last_edit应为last_time 若该id为pid则id_last_edit应为reply_num

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(f"REPLACE INTO `id_{tieba_name}` VALUES (%s,%s,DEFAULT)", (_id, id_last_edit))
        except pymysql.Error as err:
            LOG.warning(f"Failed to insert {_id}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            self._conn.commit()
            return True

    @translate_tieba_name
    async def get_id(self, tieba_name: str, _id: int) -> int:
        """
        获取表id_{tieba_name}中id对应的id_last_edit值

        Args:
            tieba_name (str): 贴吧名
            _id (int): tid或pid

        Returns:
            int: id_last_edit -1表示表中无id
        """

        try:
            self._cursor.execute(f"SELECT `id_last_edit` FROM `id_{tieba_name}` WHERE `id`=%s", (_id, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to select {_id}. reason:{err}")
            return False
        else:
            if res_tuple := self._cursor.fetchone():
                return res_tuple[0]
            else:
                return -1

    @translate_tieba_name
    async def del_id(self, tieba_name: str, _id: int) -> bool:
        """
        从表id_{tieba_name}中删除id

        Args:
            tieba_name (str): 贴吧名
            _id (int): tid或pid

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(f"DELETE FROM `id_{tieba_name}` WHERE `id`=%s", (_id, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to delete {_id}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            LOG.info(f"Successfully deleted {_id} from table of {tieba_name}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def del_ids(self, tieba_name: str, hour: int) -> bool:
        """
        删除表id_{tieba_name}中最近hour个小时记录的id

        Args:
            tieba_name (str): 贴吧名
            hour (int): 小时数

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(
                f"DELETE FROM `id_{tieba_name}` WHERE `record_time`>(CURRENT_TIMESTAMP() + INTERVAL -%s HOUR)",
                (hour, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to delete id in id_{tieba_name}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            self._conn.commit()
            LOG.info(f"Successfully deleted id in id_{tieba_name} within {hour} hour(s)")
            return True

    @translate_tieba_name
    async def _create_table_tid_water(self, tieba_name: str) -> None:
        """
        创建表tid_water_{tieba_name}

        Args:
            tieba_name (str): 贴吧名
        """

        self._cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `tid_water_{tieba_name}` (`tid` BIGINT PRIMARY KEY, `is_hide` TINYINT NOT NULL DEFAULT 1, `record_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, INDEX `is_hide`(is_hide))"
        )
        self._cursor.execute(f"""CREATE EVENT IF NOT EXISTS `event_auto_del_tid_water_{tieba_name}`
        ON SCHEDULE
        EVERY 1 DAY STARTS '2000-01-01 00:00:00'
        DO
        DELETE FROM `tid_water_{tieba_name}` WHERE `record_time`<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)""")

    @translate_tieba_name
    async def add_tid(self, tieba_name: str, tid: int, mode: bool) -> bool:
        """
        将tid添加到表tid_water_{tieba_name}

        Args:
            tieba_name (str): 贴吧名
            tid (int): 主题帖tid
            mode (bool): 待恢复状态 True对应待恢复 False对应已恢复

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(f"REPLACE INTO `tid_water_{tieba_name}` VALUES (%s,%s,DEFAULT)", (tid, mode))
        except pymysql.Error as err:
            LOG.warning(f"Failed to insert {tid}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            LOG.info(f"Successfully add {tid} to table of {tieba_name}. mode: {mode}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def is_tid_hide(self, tieba_name: str, tid: int) -> bool | None:
        """
        获取表tid_water_{tieba_name}中tid的待恢复状态

        Args:
            tieba_name (str): 贴吧名
            tid (int): 主题帖tid

        Returns:
            bool | None: True表示tid待恢复 False表示tid已恢复 None表示表中无记录
        """

        try:
            self._cursor.execute(f"SELECT `is_hide` FROM `tid_water_{tieba_name}` WHERE `tid`=%s", (tid, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to select {tid}. reason:{err}")
            return None
        else:
            if res_tuple := self._cursor.fetchone():
                return True if res_tuple[0] else False
            else:
                return None

    @translate_tieba_name
    async def del_tid(self, tieba_name: str, tid: int) -> bool:
        """
        从表tid_water_{tieba_name}中删除tid

        Args:
            tieba_name (str): 贴吧名
            tid (int): 主题帖tid

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(f"DELETE FROM `tid_water_{tieba_name}` WHERE `tid`=%s", (tid, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to delete {tid}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            LOG.info(f"Successfully deleted {tid} from table of {tieba_name}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def get_tids(self, tieba_name: str, batch_size: int = 128) -> AsyncIterable[int]:
        """
        获取表tid_water_{tieba_name}中所有待恢复的tid

        Args:
            tieba_name (str): 贴吧名
            batch_size (int): 分包大小

        Yields:
            AsyncIterable[int]: tid
        """

        for i in range(sys.maxsize):
            try:
                self._cursor.execute(
                    f"SELECT `tid` FROM `tid_water_{tieba_name}` WHERE `is_hide`=TRUE LIMIT %s OFFSET %s",
                    (batch_size, i * batch_size))
            except pymysql.Error as err:
                LOG.warning(f"Failed to get tids in {tieba_name}. reason:{err}")
                return
            else:
                tid_list = self._cursor.fetchall()
                for tid in tid_list:
                    yield tid[0]
                if len(tid_list) != batch_size:
                    return

    @translate_tieba_name
    async def _create_table_user_id(self, tieba_name: str) -> None:
        """
        创建表user_id_{tieba_name}

        Args:
            tieba_name (str): 贴吧名
        """

        self._cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `user_id_{tieba_name}` (`user_id` BIGINT PRIMARY KEY, `permission` TINYINT NOT NULL DEFAULT 0, `note` VARCHAR(64) NOT NULL DEFAULT '', `record_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, INDEX `permission`(permission), INDEX `record_time`(record_time))"
        )

    @translate_tieba_name
    async def add_user_id(self, tieba_name: str, user_id: int, permission: int = 0, note: str = '') -> bool:
        """
        将user_id添加到表user_id_{tieba_name}

        Args:
            tieba_name (str): 贴吧名
            user_id (int): 用户的user_id
            permission (int, optional): 权限级别
            note (str, optional): 备注

        Returns:
            bool: 操作是否成功
        """

        if not user_id:
            return

        try:
            self._cursor.execute(f"REPLACE INTO `user_id_{tieba_name}` VALUES (%s,%s,%s,DEFAULT)",
                                 (user_id, permission, note))
        except pymysql.Error as err:
            LOG.warning(f"Failed to insert {user_id}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            LOG.info(f"Successfully added {user_id} to table of {tieba_name}. permission: {permission} note: {note}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def del_user_id(self, tieba_name: str, user_id: int) -> bool:
        """
        从表user_id_{tieba_name}中删除user_id

        Args:
            tieba_name (str): 贴吧名
            user_id (int): 用户的user_id

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(f"DELETE FROM `user_id_{tieba_name}` WHERE `user_id`=%s", (user_id, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to delete {user_id}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            LOG.info(f"Successfully deleted {user_id} from table of {tieba_name}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def get_user_id(self, tieba_name: str, user_id: int) -> int:
        """
        获取表user_id_{tieba_name}中user_id的权限级别

        Args:
            tieba_name (str): 贴吧名
            user_id (int): 用户的user_id

        Returns:
            int: 权限级别
        """

        try:
            self._cursor.execute(f"SELECT `permission` FROM `user_id_{tieba_name}` WHERE `user_id`=%s", (user_id, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to get {user_id}. reason:{err}")
            return 0
        else:
            if res_tuple := self._cursor.fetchone():
                return res_tuple[0]
            else:
                return 0

    @translate_tieba_name
    async def get_user_id_full(self, tieba_name: str, user_id: int) -> tuple[int, str, datetime.datetime]:
        """
        获取表user_id_{tieba_name}中user_id的完整信息

        Args:
            tieba_name (str): 贴吧名
            user_id (int): 用户的user_id

        Returns:
            int: 权限级别
            str: 备注
            datetime.datetime: 记录时间
        """

        try:
            self._cursor.execute(
                f"SELECT `permission`,`note`,`record_time` FROM `user_id_{tieba_name}` WHERE `user_id`=%s", (user_id, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to get full {user_id}. reason:{err}")
            return 0, '', datetime.datetime(1970, 1, 1)
        else:
            if res_tuple := self._cursor.fetchone():
                return res_tuple
            else:
                return 0, '', datetime.datetime(1970, 1, 1)

    @translate_tieba_name
    async def get_user_id_list(self,
                               tieba_name: str,
                               limit: int = 1,
                               offset: int = 0,
                               permission: int = 0) -> list[int]:
        """
        获取表user_id_{tieba_name}中user_id的列表

        Args:
            tieba_name (str): 贴吧名
            limit (int, optional): 返回数量限制
            offset (int, optional): 偏移
            permission (int, optional): 获取所有权限级别大于等于permission的user_id

        Returns:
            list[int]: user_id列表
        """

        try:
            self._cursor.execute(
                f"SELECT `user_id` FROM `user_id_{tieba_name}` WHERE `permission`>=%s ORDER BY `record_time` DESC LIMIT %s OFFSET %s",
                (permission, limit, offset))
        except pymysql.Error as err:
            LOG.warning(f"Failed to get user_ids in {tieba_name}. reason:{err}")
            res_list = []
        else:
            res_tuples = self._cursor.fetchall()
            res_list = [res_tuple[0] for res_tuple in res_tuples]

        return res_list

    @translate_tieba_name
    async def _create_table_img_blacklist(self, tieba_name: str) -> None:
        """
        创建表img_blacklist_{tieba_name}

        Args:
            tieba_name (str): 贴吧名
        """

        self._cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `img_blacklist_{tieba_name}` (`img_hash` CHAR(16) PRIMARY KEY, `raw_hash` CHAR(40) UNIQUE NOT NULL)"
        )

    @translate_tieba_name
    async def add_imghash(self, tieba_name: str, img_hash: str, raw_hash: str) -> bool:
        """
        向img_blacklist_{tieba_name}插入img_hash

        Args:
            tieba_name (str): 贴吧名
            img_hash (str): 图像的phash
            raw_hash (str): 贴吧图床hash

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(f"REPLACE INTO `img_blacklist_{tieba_name}` VALUES (%s,%s)", (img_hash, raw_hash))
        except pymysql.Error as err:
            LOG.warning(f"Failed to insert {img_hash}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            LOG.info(f"Successfully add {img_hash} to table of {tieba_name}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def has_imghash(self, tieba_name: str, img_hash: str) -> bool:
        """
        检索img_blacklist_{tieba_name}中是否已有img_hash

        Args:
            tieba_name (str): 贴吧名
            img_hash (str): 图像的phash

        Returns:
            bool: True表示表中已有img_hash False表示表中无img_hash或查询失败
        """

        try:
            self._cursor.execute(f"SELECT NULL FROM `img_blacklist_{tieba_name}` WHERE `img_hash`=%s", (img_hash, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to select {img_hash}. reason:{err}")
            return False
        else:
            return True if self._cursor.fetchone() else False

    @translate_tieba_name
    async def del_imghash(self, tieba_name: str, img_hash: str) -> bool:
        """
        从img_blacklist_{tieba_name}中删除img_hash

        Args:
            tieba_name (str): 贴吧名
            img_hash (str): 图像的phash

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(f"DELETE FROM `img_blacklist_{tieba_name}` WHERE `img_hash`=%s", (img_hash, ))
        except pymysql.Error as err:
            LOG.warning(f"Failed to delete {img_hash}. reason:{err}")
            self._conn.rollback()
            return False
        else:
            LOG.info(f"Successfully deleted {img_hash} from table of {tieba_name}")
            self._conn.commit()
            return True


DATABASE = None


def get_database():
    global DATABASE
    if DATABASE is None:
        DATABASE = Database('tieba_cloud_review')

        import atexit
        atexit.register(DATABASE.close)

    return DATABASE
