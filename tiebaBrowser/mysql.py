# -*- coding:utf-8 -*-
__all__ = ['MySQL']


import sys
from functools import wraps
from typing import NoReturn, Optional

import pymysql

from .config import config
from .logger import log


def translate_tieba_name(func):

    @wraps(func)
    def wrapper(self, tieba_name, *args, **kwargs):
        tieba_name_eng = config['tieba_name_mapping'].get(tieba_name, None)
        if not tieba_name_eng:
            log.error(f"Can not find key:{tieba_name} in name mapping")
            return
        return func(self, tieba_name_eng, *args, **kwargs)

    return wrapper


class MySQL(object):
    """
    MySQL链接基类

    MySQL(db_name)
    """

    __slots__ = ['db_name', 'conn', 'cursor']

    def __init__(self, db_name: str = 'tieba_cloud_review') -> NoReturn:

        self.db_name = db_name

        try:
            self.conn = pymysql.connect(**config['MySQL'], database=db_name)
            self.cursor = self.conn.cursor()
        except pymysql.Error:
            log.warning(f"Cannot link to the database {db_name}!")
            self.init_database()

    async def close(self) -> NoReturn:
        self.conn.commit()
        self.conn.close()

    async def init_database(self) -> NoReturn:
        self.conn = pymysql.connect(**config['MySQL'])
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"CREATE DATABASE {self.db_name}")
        self.cursor.execute(f"USE {self.db_name}")

        for tieba_name in config['tieba_name_mapping'].keys():
            await self.create_table_pid_whitelist(tieba_name)
            await self.create_table_user_id(tieba_name)
            await self.create_table_img_blacklist(tieba_name)
            await self.create_table_tid_water(tieba_name)

    async def ping(self) -> bool:
        """
        尝试重连
        """

        try:
            self.conn.ping(reconnect=True)
        except pymysql.Error:
            return False
        else:
            return True

    @translate_tieba_name
    async def create_table_pid_whitelist(self, tieba_name_eng: str) -> NoReturn:
        """
        创建表pid_whitelist_{tieba_name_eng}
        create_table_pid_whitelist(tieba_name)
        """

        self.cursor.execute(
            f"SHOW TABLES LIKE 'pid_whitelist_{tieba_name_eng}'")
        if not self.cursor.fetchone():
            self.cursor.execute(
                f"CREATE TABLE pid_whitelist_{tieba_name_eng} (pid BIGINT PRIMARY KEY, record_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            self.cursor.execute(f"""CREATE EVENT event_auto_del_pid_whitelist_{tieba_name_eng}
            ON SCHEDULE
            EVERY 1 DAY STARTS '2000-01-01 00:00:00'
            DO
            DELETE FROM pid_whitelist_{tieba_name_eng} WHERE record_time<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)""")

    @translate_tieba_name
    async def add_pid(self, tieba_name_eng: str, pid: int) -> bool:
        """
        向pid_whitelist_{tieba_name_eng}插入pid
        add_pid(tieba_name,pid)
        """

        try:
            self.cursor.execute(
                f"REPLACE INTO pid_whitelist_{tieba_name_eng} VALUES ({pid},DEFAULT)")
        except pymysql.Error:
            log.warning(f"MySQL Error: Failed to insert {pid}!")
            return False
        else:
            self.conn.commit()
            return True

    @translate_tieba_name
    async def has_pid(self, tieba_name_eng: str, pid: int) -> bool:
        """
        检索pid_whitelist_{tieba_name_eng}中是否已有pid
        has_pid(tieba_name,pid)
        """

        try:
            self.cursor.execute(
                f"SELECT NULL FROM pid_whitelist_{tieba_name_eng} WHERE pid={pid}")
        except pymysql.Error:
            log.warning(f"MySQL Error: Failed to select {pid}!")
            return False
        else:
            return True if self.cursor.fetchone() else False

    @translate_tieba_name
    async def del_pid(self, tieba_name_eng: str, pid: int) -> bool:
        """
        从pid_whitelist_{tieba_name_eng}中删除pid
        del_pid(tieba_name,pid)
        """

        try:
            self.cursor.execute(
                f"DELETE FROM pid_whitelist_{tieba_name_eng} WHERE pid={pid}")
        except pymysql.Error:
            log.warning(f"MySQL Error: Failed to delete {pid}!")
            return False
        else:
            log.info(
                f"Successfully deleted {pid} from table of {tieba_name_eng}")
            self.conn.commit()
            return True

    @translate_tieba_name
    async def del_pids(self, tieba_name_eng: str, hour: int) -> bool:
        """
        删除最近hour个小时pid_whitelist_{tieba_name_eng}中记录的pid
        del_pid(tieba_name,hour)
        """

        try:
            self.cursor.execute(
                f"DELETE FROM pid_whitelist_{tieba_name_eng} WHERE record_time>(CURRENT_TIMESTAMP() + INTERVAL -{hour} HOUR)")
        except pymysql.Error:
            log.warning(
                f"MySQL Error: Failed to delete pid in pid_whitelist_{tieba_name_eng}")
            return False
        else:
            self.conn.commit()
            log.info(
                f"Successfully deleted pid in pid_whitelist_{tieba_name_eng} within {hour} hour(s)")
            return True

    @translate_tieba_name
    async def create_table_tid_water(self, tieba_name_eng: str) -> NoReturn:
        """
        创建表tid_water_{tieba_name_eng}
        create_table_tid_water(tieba_name)
        """

        self.cursor.execute(
            f"SHOW TABLES LIKE 'tid_water_{tieba_name_eng}'")
        if not self.cursor.fetchone():
            self.cursor.execute(
                f"CREATE TABLE tid_water_{tieba_name_eng} (tid BIGINT PRIMARY KEY, is_hide BOOL NOT NULL DEFAULT TRUE, record_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            self.cursor.execute(f"""CREATE EVENT event_auto_del_tid_water_{tieba_name_eng}
            ON SCHEDULE
            EVERY 1 DAY STARTS '2000-01-01 00:00:00'
            DO
            DELETE FROM tid_water_{tieba_name_eng} WHERE record_time<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)""")

    @translate_tieba_name
    async def update_tid(self, tieba_name_eng: str, tid: int, mode: bool) -> bool:
        """
        在tid_water_{tieba_name_eng}中更新tid的待恢复状态
        add_tid(tieba_name,tid,mode)

        参数:
            tieba_name: str 贴吧名
            mode: bool True对应待恢复，False对应已恢复
        """

        try:
            self.cursor.execute(
                f"REPLACE INTO tid_water_{tieba_name_eng} VALUES ({tid},{mode},DEFAULT)")
        except pymysql.Error:
            log.warning(f"MySQL Error: Failed to insert {tid}!")
            return False
        else:
            log.info(
                f"Successfully add {tid} to table of {tieba_name_eng}. mode:{mode}")
            self.conn.commit()
            return True

    @translate_tieba_name
    async def is_tid_hide(self, tieba_name_eng: str, tid: int) -> bool:
        """
        检索tid的待恢复状态
        is_tid_hide(tieba_name,tid)

        返回值:
            is_hide: True 待恢复 / False 已恢复 / None 表中无记录
        """

        try:
            self.cursor.execute(
                f"SELECT is_hide FROM tid_water_{tieba_name_eng} WHERE tid={tid}")
        except pymysql.Error:
            log.warning(f"MySQL Error: Failed to select {tid}!")
            return None
        else:
            res_tuple = self.cursor.fetchone()
            if res_tuple:
                return True if res_tuple[0] else False
            else:
                return None

    @translate_tieba_name
    async def del_tid(self, tieba_name_eng: str, tid: int) -> bool:
        """
        从tid_water_{tieba_name_eng}中删除tid
        del_tid(tieba_name,tid)
        """

        try:
            self.cursor.execute(
                f"DELETE FROM tid_water_{tieba_name_eng} WHERE tid={tid}")
        except pymysql.Error:
            log.warning(f"MySQL Error: Failed to delete {tid}!")
            return False
        else:
            log.info(
                f"Successfully deleted {tid} from table of {tieba_name_eng}")
            self.conn.commit()
            return True

    @translate_tieba_name
    async def get_tids(self, tieba_name_eng: str, batch_size: int = 128) -> int:
        """
        获取tid_water_{tieba_name_eng}中所有待恢复的tid
        get_tids(tieba_name,batch_size=128)

        参数:
            batch_size: int 分包大小

        迭代返回值:
            tid: int
        """

        for i in range(sys.maxsize):
            try:
                self.cursor.execute(
                    f"SELECT tid FROM tid_water_{tieba_name_eng} WHERE is_hide=TRUE LIMIT {batch_size} OFFSET {i * batch_size}")
            except pymysql.Error:
                log.warning(
                    f"MySQL Error: Failed to get tids in {tieba_name_eng}!")
                return
            else:
                tid_list = self.cursor.fetchall()
                for tid in tid_list:
                    yield tid[0]
                if len(tid_list) != batch_size:
                    return

    @translate_tieba_name
    async def create_table_user_id(self, tieba_name_eng: str) -> NoReturn:
        """
        创建表user_id_{tieba_name_eng}
        create_table_user_id(tieba_name)
        """

        self.cursor.execute(f"SHOW TABLES LIKE 'user_id_{tieba_name_eng}'")
        if not self.cursor.fetchone():
            self.cursor.execute(
                f"CREATE TABLE user_id_{tieba_name_eng} (user_id BIGINT PRIMARY KEY, is_white BOOL NOT NULL DEFAULT TRUE, record_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)")

    @translate_tieba_name
    async def update_user_id(self, tieba_name_eng: str, user_id: int, mode: bool) -> bool:
        """
        更新user_id在user_id_{tieba_name_eng}中的状态
        update_user_id(tieba_name,user_id,mode)

        参数:
            mode: bool True对应白名单，False对应黑名单
        """

        try:
            self.cursor.execute(
                f"REPLACE INTO user_id_{tieba_name_eng} VALUES ({user_id},{mode},DEFAULT)")
        except pymysql.Error:
            log.warning(f"MySQL Error: Failed to insert {user_id}!")
            return False
        else:
            log.info(
                f"Successfully updated {user_id} to table of {tieba_name_eng}. mode:{mode}")
            self.conn.commit()
            return True

    @translate_tieba_name
    async def del_user_id(self, tieba_name_eng: str, user_id: int) -> bool:
        """
        从黑/白名单中删除user_id
        del_user_id(tieba_name,user_id)
        """

        try:
            self.cursor.execute(
                f"DELETE FROM user_id_{tieba_name_eng} WHERE user_id={user_id}")
        except pymysql.Error:
            log.warning(f"MySQL Error: Failed to delete {user_id}!")
            return False
        else:
            log.info(
                f"Successfully deleted {user_id} from table of {tieba_name_eng}")
            self.conn.commit()
            return True

    @translate_tieba_name
    async def is_user_id_white(self, tieba_name_eng: str, user_id: int) -> Optional[bool]:
        """
        检索user_id的黑/白名单状态
        is_user_id_white(tieba_name,user_id)

        返回值:
            is_white: True 白名单 / False 黑名单 / None 表中无记录
        """

        try:
            self.cursor.execute(
                f"SELECT is_white FROM user_id_{tieba_name_eng} WHERE user_id={user_id}")
        except pymysql.Error:
            return None
        else:
            res_tuple = self.cursor.fetchone()
            if res_tuple:
                return True if res_tuple[0] else False
            else:
                return None

    @translate_tieba_name
    async def get_user_ids(self, tieba_name_eng: str, batch_size: int = 128) -> int:
        """
        获取user_id列表
        get_user_ids(tieba_name,batch_size=128)

        参数:
            batch_size: int 分包大小

        迭代返回值:
            user_id
        """

        for i in range(sys.maxsize):
            try:
                self.cursor.execute(
                    f"SELECT user_id FROM user_id_{tieba_name_eng} LIMIT {batch_size} OFFSET {i * batch_size}")
            except pymysql.Error:
                log.warning(
                    f"MySQL Error: Failed to get user_ids in {tieba_name_eng}!")
                return
            else:
                user_ids = self.cursor.fetchall()
                for user_id in user_ids:
                    yield user_id[0]
                if len(user_ids) != batch_size:
                    return

    @translate_tieba_name
    async def create_table_img_blacklist(self, tieba_name_eng: str) -> NoReturn:
        """
        创建表img_blacklist_{tieba_name_eng}
        create_table_img_blacklist(tieba_name)
        """

        self.cursor.execute(
            f"SHOW TABLES LIKE 'img_blacklist_{tieba_name_eng}'")
        if not self.cursor.fetchone():
            self.cursor.execute(
                f"CREATE TABLE img_blacklist_{tieba_name_eng} (img_hash CHAR(16) PRIMARY KEY, raw_hash CHAR(40) NOT NULL)")

    @translate_tieba_name
    async def add_imghash(self, tieba_name_eng: str, img_hash: str, raw_hash: str) -> bool:
        """
        向img_blacklist_{tieba_name_eng}插入img_hash
        add_imghash(tieba_name,img_hash,raw_hash)
        """

        try:
            self.cursor.execute(
                f"REPLACE INTO img_blacklist_{tieba_name_eng} VALUES ('{img_hash}','{raw_hash}')")
        except pymysql.Error:
            log.warning(f"MySQL Error: Failed to insert {img_hash}!")
            return False
        else:
            log.info(
                f"Successfully add {img_hash} to table of {tieba_name_eng}")
            self.conn.commit()
            return True

    @translate_tieba_name
    async def has_imghash(self, tieba_name_eng: str, img_hash: str) -> bool:
        """
        检索img_blacklist_{tieba_name_eng}中是否已有img_hash
        has_imghash(tieba_name,img_hash)
        """

        try:
            self.cursor.execute(
                f"SELECT NULL FROM img_blacklist_{tieba_name_eng} WHERE img_hash='{img_hash}'")
        except pymysql.Error:
            log.warning(f"MySQL Error: Failed to select {img_hash}!")
            return False
        else:
            return True if self.cursor.fetchone() else False

    @translate_tieba_name
    async def del_imghash(self, tieba_name_eng: str, img_hash: str) -> bool:
        """
        从img_blacklist_{tieba_name_eng}中删除img_hash
        del_imghash(tieba_name,img_hash)
        """

        try:
            self.cursor.execute(
                f"DELETE FROM img_blacklist_{tieba_name_eng} WHERE img_hash='{img_hash}'")
        except pymysql.Error:
            log.warning(f"MySQL Error: Failed to delete {img_hash}!")
            return False
        else:
            log.info(
                f"Successfully deleted {img_hash} from table of {tieba_name_eng}")
            self.conn.commit()
            return True
