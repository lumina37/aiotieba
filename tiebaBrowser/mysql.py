# -*- coding:utf-8 -*-
__all__ = ['MySQL']

import functools
import sys
from collections.abc import AsyncIterable
from typing import Optional, Union
from warnings import filterwarnings

import pymysql

from ._config import config
from ._logger import log
from ._types import BasicUserInfo

filterwarnings('ignore', category=pymysql.Warning)


def translate_tieba_name(func):

    @functools.wraps(func)
    def wrapper(self, tieba_name, *args, **kwargs):
        if not (tieba_name_eng := config['tieba_name_mapping'].get(tieba_name, None)):
            log.error(f"Can not find key:{tieba_name} in name mapping")
            return
        return func(self, tieba_name_eng, *args, **kwargs)

    return wrapper


class MySQL(object):
    """
    MySQL连接基类

    Args:
        db_name (str, optional): 连接的数据库名. Defaults to 'tieba_cloud_review'.
    """

    __slots__ = ['db_name', '_conn', '_cursor']

    def __init__(self, db_name: str = 'tieba_cloud_review') -> None:

        self.db_name = db_name

        try:
            self._conn = pymysql.connect(**config['MySQL'], database=db_name)
            self._cursor = self._conn.cursor()
        except pymysql.Error as err:
            log.warning(f"Cannot link to the database {db_name}. reason:{err}")
            self.init_database()

    async def close(self) -> None:
        self._conn.commit()
        self._conn.close()

    async def init_database(self) -> None:
        """
        初始化数据库
        """

        self._conn = pymysql.connect(**config['MySQL'])
        self._cursor = self._conn.cursor()
        self._cursor.execute(f"CREATE DATABASE {self.db_name}")
        self._cursor.execute(f"USE {self.db_name}")

        await self.create_table_forum()
        await self.create_table_user()
        for tieba_name in config['tieba_name_mapping'].keys():
            await self.create_table_id(tieba_name)
            await self.create_table_user_id(tieba_name)
            await self.create_table_img_blacklist(tieba_name)
            await self.create_table_tid_water(tieba_name)

    async def ping(self) -> bool:
        """
        检测连接状态 若断连则尝试重连

        Returns:
            bool: 是否连接成功
        """

        try:
            self._conn.ping(reconnect=True)
        except pymysql.Error as err:
            return False
        else:
            return True

    async def create_table_forum(self) -> None:
        """
        创建表forum
        """

        self._cursor.execute(f"SHOW TABLES LIKE 'forum'")
        if not self._cursor.fetchone():
            self._cursor.execute(
                f"CREATE TABLE forum (fid INT PRIMARY KEY, tieba_name VARCHAR(36) UNIQUE)")

    async def get_fid(self, tieba_name: str) -> int:
        """
        通过贴吧名获取forum_id

        Args:
            tieba_name (str): 贴吧名

        Returns:
            int: 该贴吧的forum_id
        """

        try:
            self._cursor.execute(
                f"SELECT fid FROM forum WHERE tieba_name='{tieba_name}'")
        except pymysql.Error as err:
            log.warning(f"Failed to select {tieba_name}. reason:{err}")
            return 0
        else:
            if (res_tuple := self._cursor.fetchone()):
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
            self._cursor.execute(
                f"SELECT tieba_name FROM forum WHERE fid={fid}")
        except pymysql.Error as err:
            log.warning(f"Failed to select {fid}. reason:{err}")
            return ''
        else:
            if (res_tuple := self._cursor.fetchone()):
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
            self._cursor.execute(
                f"INSERT IGNORE INTO forum VALUES ({fid},'{tieba_name}')")
        except pymysql.Error as err:
            log.warning(f"Failed to insert {fid}. reason:{err}")
            return False
        else:
            self._conn.commit()
            return True

    async def create_table_user(self) -> None:
        """
        创建表user
        """

        self._cursor.execute(f"SHOW TABLES LIKE 'user'")
        if not self._cursor.fetchone():
            self._cursor.execute(
                f"CREATE TABLE user (user_id BIGINT PRIMARY KEY, user_name VARCHAR(14), portrait VARCHAR(36) UNIQUE, INDEX index_user_name(user_name))")

    async def get_basic_user_info(self, _id: Union[str, int]) -> BasicUserInfo:
        """
        补全简略版用户信息

        Args:
            _id (Union[str, int]): 用户id user_name/portrait/user_id

        Returns:
            BasicUserInfo: 简略版用户信息 仅保证包含user_name/portrait/user_id
        """

        user = BasicUserInfo(_id)

        try:
            if user.user_id:
                self._cursor.execute(
                    f"SELECT * FROM user WHERE user_id={user.user_id}")
            elif user.portrait:
                self._cursor.execute(
                    f"SELECT * FROM user WHERE portrait='{user.portrait}'")
            elif user.user_name:
                self._cursor.execute(
                    f"SELECT * FROM user WHERE user_name='{user.user_name}'")
        except pymysql.Error as err:
            log.warning(f"Failed to select {user}. reason:{err}")
            return BasicUserInfo()
        else:
            if (res_tuple := self._cursor.fetchone()):
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
            self._cursor.execute(
                f"INSERT IGNORE INTO user VALUES ({user.user_id},'{user.user_name}','{user.portrait}')")
        except pymysql.Error as err:
            log.warning(f"Failed to insert {user}. reason:{err}")
            return False
        else:
            self._conn.commit()
            return True

    async def del_user(self, user: BasicUserInfo) -> bool:
        """
        从user中删除简略版用户信息

        Args:
            user (BasicUserInfo): 待删除的简略版用户信息

        Returns:
            bool: 操作是否成功
        """

        try:
            if user.user_id:
                self._cursor.execute(
                    f"DELETE FROM user WHERE user_id={user.user_id}")
            elif user.portrait:
                self._cursor.execute(
                    f"DELETE FROM user WHERE portrait='{user.portrait}'")
            elif user.user_name:
                self._cursor.execute(
                    f"DELETE FROM user WHERE user_name='{user.user_name}'")
        except pymysql.Error as err:
            log.warning(f"Failed to delete {user}. reason:{err}")
            return False
        else:
            log.info(f"Successfully deleted {user} from table user")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def create_table_id(self, tieba_name_eng: str) -> None:
        """
        创建表id_{tieba_name_eng}

        Args:
            tieba_name (str): 贴吧名
        """

        self._cursor.execute(
            f"SHOW TABLES LIKE 'id_{tieba_name_eng}'")
        if not self._cursor.fetchone():
            self._cursor.execute(
                f"CREATE TABLE id_{tieba_name_eng} (id BIGINT PRIMARY KEY, id_last_edit INT NOT NULL, record_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            self._cursor.execute(f"""CREATE EVENT event_auto_del_id_{tieba_name_eng}
            ON SCHEDULE
            EVERY 1 DAY STARTS '2000-01-01 00:00:00'
            DO
            DELETE FROM id_{tieba_name_eng} WHERE record_time<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)""")

    @translate_tieba_name
    async def update_id(self, tieba_name_eng: str, id: int, id_last_edit: int = 0) -> bool:
        """
        向id_{tieba_name_eng}插入id

        Args:
            tieba_name (str): 贴吧名
            id (int)
            id_last_edit (int): 用于识别id的子对象列表是否发生修改 若该id为tid则id_last_edit应为last_time 若该id为pid则id_last_edit应为reply_num

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(
                f"REPLACE INTO id_{tieba_name_eng} VALUES ({id},{id_last_edit},DEFAULT)")
        except pymysql.Error as err:
            log.warning(f"Failed to insert {id}. reason:{err}")
            return False
        else:
            self._conn.commit()
            return True

    @translate_tieba_name
    async def get_id(self, tieba_name_eng: str, id: int) -> int:
        """
        检索id_{tieba_name_eng}中是否已有id

        Args:
            tieba_name (str): 贴吧名
            id (int)

        Returns:
            int: id_last_edit -1表示表中无id
        """

        try:
            self._cursor.execute(
                f"SELECT id_last_edit FROM id_{tieba_name_eng} WHERE id={id}")
        except pymysql.Error as err:
            log.warning(f"Failed to select {id}. reason:{err}")
            return False
        else:
            if (res_tuple := self._cursor.fetchone()):
                return res_tuple[0]
            else:
                return -1

    @translate_tieba_name
    async def del_id(self, tieba_name_eng: str, id: int) -> bool:
        """
        从id_{tieba_name_eng}中删除id

        Args:
            tieba_name (str): 贴吧名
            id (int)

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(
                f"DELETE FROM id_{tieba_name_eng} WHERE id={id}")
        except pymysql.Error as err:
            log.warning(f"Failed to delete {id}. reason:{err}")
            return False
        else:
            log.info(
                f"Successfully deleted {id} from table of {tieba_name_eng}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def del_ids(self, tieba_name_eng: str, hour: int) -> bool:
        """
        删除最近hour个小时id_{tieba_name_eng}中记录的id

        Args:
            tieba_name (str): 贴吧名
            hour (int): 小时数

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(
                f"DELETE FROM id_{tieba_name_eng} WHERE record_time>(CURRENT_TIMESTAMP() + INTERVAL -{hour} HOUR)")
        except pymysql.Error as err:
            log.warning(
                f"Failed to delete id in id_{tieba_name_eng}")
            return False
        else:
            self._conn.commit()
            log.info(
                f"Successfully deleted id in id_{tieba_name_eng} within {hour} hour(s)")
            return True

    @translate_tieba_name
    async def create_table_tid_water(self, tieba_name_eng: str) -> None:
        """
        创建表tid_water_{tieba_name_eng}

        Args:
            tieba_name (str): 贴吧名
        """

        self._cursor.execute(
            f"SHOW TABLES LIKE 'tid_water_{tieba_name_eng}'")
        if not self._cursor.fetchone():
            self._cursor.execute(
                f"CREATE TABLE tid_water_{tieba_name_eng} (tid BIGINT PRIMARY KEY, is_hide BOOL NOT NULL DEFAULT TRUE, record_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            self._cursor.execute(f"""CREATE EVENT event_auto_del_tid_water_{tieba_name_eng}
            ON SCHEDULE
            EVERY 1 DAY STARTS '2000-01-01 00:00:00'
            DO
            DELETE FROM tid_water_{tieba_name_eng} WHERE record_time<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)""")

    @translate_tieba_name
    async def update_tid(self, tieba_name_eng: str, tid: int, mode: bool) -> bool:
        """
        在tid_water_{tieba_name_eng}中更新tid的待恢复状态

        Args:
            tieba_name (str): 贴吧名
            mode (bool): 待恢复状态 True对应待恢复 False对应已恢复

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(
                f"REPLACE INTO tid_water_{tieba_name_eng} VALUES ({tid},{mode},DEFAULT)")
        except pymysql.Error as err:
            log.warning(f"Failed to insert {tid}. reason:{err}")
            return False
        else:
            log.info(
                f"Successfully add {tid} to table of {tieba_name_eng}. mode:{mode}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def is_tid_hide(self, tieba_name_eng: str, tid: int) -> Optional[bool]:
        """
        检索tid的待恢复状态

        Args:
            tieba_name (str): 贴吧名
            tid (int)

        Returns:
            Optional[bool]: True表示tid待恢复 False表示tid已恢复 None表示表中无记录
        """

        try:
            self._cursor.execute(
                f"SELECT is_hide FROM tid_water_{tieba_name_eng} WHERE tid={tid}")
        except pymysql.Error as err:
            log.warning(f"Failed to select {tid}. reason:{err}")
            return None
        else:
            if (res_tuple := self._cursor.fetchone()):
                return True if res_tuple[0] else False
            else:
                return None

    @translate_tieba_name
    async def del_tid(self, tieba_name_eng: str, tid: int) -> bool:
        """
        从tid_water_{tieba_name_eng}中删除tid

        Args:
            tieba_name (str): 贴吧名

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(
                f"DELETE FROM tid_water_{tieba_name_eng} WHERE tid={tid}")
        except pymysql.Error as err:
            log.warning(f"Failed to delete {tid}. reason:{err}")
            return False
        else:
            log.info(
                f"Successfully deleted {tid} from table of {tieba_name_eng}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def get_tids(self, tieba_name_eng: str, batch_size: int = 128) -> AsyncIterable[int]:
        """
        获取tid_water_{tieba_name_eng}中所有待恢复的tid
        get_tids(tieba_name,batch_size=128)

        Args:
            tieba_name (str): 贴吧名
            batch_size (int): 分包大小

        Yields:
            AsyncIterable[int]: tid
        """

        for i in range(sys.maxsize):
            try:
                self._cursor.execute(
                    f"SELECT tid FROM tid_water_{tieba_name_eng} WHERE is_hide=TRUE LIMIT {batch_size} OFFSET {i * batch_size}")
            except pymysql.Error as err:
                log.warning(
                    f"Failed to get tids in {tieba_name_eng}. reason:{err}")
                return
            else:
                tid_list = self._cursor.fetchall()
                for tid in tid_list:
                    yield tid[0]
                if len(tid_list) != batch_size:
                    return

    @translate_tieba_name
    async def create_table_user_id(self, tieba_name_eng: str) -> None:
        """
        创建表user_id_{tieba_name_eng}

        Args:
            tieba_name (str): 贴吧名
        """

        self._cursor.execute(f"SHOW TABLES LIKE 'user_id_{tieba_name_eng}'")
        if not self._cursor.fetchone():
            self._cursor.execute(
                f"CREATE TABLE user_id_{tieba_name_eng} (user_id BIGINT PRIMARY KEY, is_white BOOL NOT NULL DEFAULT TRUE, record_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)")

    @translate_tieba_name
    async def update_user_id(self, tieba_name_eng: str, user_id: int, mode: bool) -> bool:
        """
        更新user_id在user_id_{tieba_name_eng}中的状态
        Args:
            tieba_name (str): 贴吧名

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(
                f"REPLACE INTO user_id_{tieba_name_eng} VALUES ({user_id},{mode},DEFAULT)")
        except pymysql.Error as err:
            log.warning(f"Failed to insert {user_id}. reason:{err}")
            return False
        else:
            log.info(
                f"Successfully updated {user_id} to table of {tieba_name_eng}. mode:{mode}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def del_user_id(self, tieba_name_eng: str, user_id: int) -> bool:
        """
        从黑/白名单中删除user_id

        Args:
            tieba_name (str): 贴吧名
            user_id (int)

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(
                f"DELETE FROM user_id_{tieba_name_eng} WHERE user_id={user_id}")
        except pymysql.Error as err:
            log.warning(f"Failed to delete {user_id}. reason:{err}")
            return False
        else:
            log.info(
                f"Successfully deleted {user_id} from table of {tieba_name_eng}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def is_user_id_white(self, tieba_name_eng: str, user_id: int) -> Optional[bool]:
        """
        检索user_id的黑/白名单状态

        Args:
            tieba_name (str): 贴吧名
            user_id (int)

        Returns:
            Optional[bool]: True表示user_id为白名单 False表示user_id为黑名单 None表示表中无记录
        """

        try:
            self._cursor.execute(
                f"SELECT is_white FROM user_id_{tieba_name_eng} WHERE user_id={user_id}")
        except pymysql.Error as err:
            return None
        else:
            if (res_tuple := self._cursor.fetchone()):
                return True if res_tuple[0] else False
            else:
                return None

    @translate_tieba_name
    async def get_user_ids(self, tieba_name_eng: str, batch_size: int = 128) -> AsyncIterable[int]:
        """
        获取user_id列表

        Args:
            tieba_name (str): 贴吧名
            batch_size (int): 分包大小

        Yields:
            AsyncIterable[int]: user_id
        """

        for i in range(sys.maxsize):
            try:
                self._cursor.execute(
                    f"SELECT user_id FROM user_id_{tieba_name_eng} LIMIT {batch_size} OFFSET {i * batch_size}")
            except pymysql.Error as err:
                log.warning(
                    f"Failed to get user_ids in {tieba_name_eng}. reason:{err}")
                return
            else:
                user_ids = self._cursor.fetchall()
                for user_id in user_ids:
                    yield user_id[0]
                if len(user_ids) != batch_size:
                    return

    @translate_tieba_name
    async def create_table_img_blacklist(self, tieba_name_eng: str) -> None:
        """
        创建表img_blacklist_{tieba_name_eng}

        Args:
            tieba_name (str): 贴吧名
        """

        self._cursor.execute(
            f"SHOW TABLES LIKE 'img_blacklist_{tieba_name_eng}'")
        if not self._cursor.fetchone():
            self._cursor.execute(
                f"CREATE TABLE img_blacklist_{tieba_name_eng} (img_hash CHAR(16) PRIMARY KEY, raw_hash CHAR(40) UNIQUE NOT NULL)")

    @translate_tieba_name
    async def add_imghash(self, tieba_name_eng: str, img_hash: str, raw_hash: str) -> bool:
        """
        向img_blacklist_{tieba_name_eng}插入img_hash

        Args:
            tieba_name (str): 贴吧名
            img_hash (str)
            raw_hash (str): 贴吧图床hash

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(
                f"REPLACE INTO img_blacklist_{tieba_name_eng} VALUES ('{img_hash}','{raw_hash}')")
        except pymysql.Error as err:
            log.warning(f"Failed to insert {img_hash}. reason:{err}")
            return False
        else:
            log.info(
                f"Successfully add {img_hash} to table of {tieba_name_eng}")
            self._conn.commit()
            return True

    @translate_tieba_name
    async def has_imghash(self, tieba_name_eng: str, img_hash: str) -> bool:
        """
        检索img_blacklist_{tieba_name_eng}中是否已有img_hash

        Args:
            tieba_name (str): 贴吧名
            img_hash (str)

        Returns:
            bool: True表示表中已有img_hash False表示表中无img_hash或查询失败
        """

        try:
            self._cursor.execute(
                f"SELECT NULL FROM img_blacklist_{tieba_name_eng} WHERE img_hash='{img_hash}'")
        except pymysql.Error as err:
            log.warning(f"Failed to select {img_hash}. reason:{err}")
            return False
        else:
            return True if self._cursor.fetchone() else False

    @translate_tieba_name
    async def del_imghash(self, tieba_name_eng: str, img_hash: str) -> bool:
        """
        从img_blacklist_{tieba_name_eng}中删除img_hash

        Args:
            tieba_name (str): 贴吧名
            img_hash (str)

        Returns:
            bool: 操作是否成功
        """

        try:
            self._cursor.execute(
                f"DELETE FROM img_blacklist_{tieba_name_eng} WHERE img_hash='{img_hash}'")
        except pymysql.Error as err:
            log.warning(f"Failed to delete {img_hash}. reason:{err}")
            return False
        else:
            log.info(
                f"Successfully deleted {img_hash} from table of {tieba_name_eng}")
            self._conn.commit()
            return True
