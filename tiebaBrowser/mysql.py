# -*- coding:utf-8 -*-
import os
import sys
from functools import wraps

import json

import pymysql

from .data_structure import SCRIPT_DIR
from .utils import config
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

    __slots__ = ['db_name', 'mydb', 'mycursor']

    def __init__(self, db_name):

        mysql_json = config['MySQL']

        self.db_name = db_name

        try:
            self.mydb = pymysql.connect(**mysql_json, database=db_name)
            self.mycursor = self.mydb.cursor()
        except pymysql.ProgrammingError:
            log.critical(f"Cannot link to the database {db_name}!")
            raise

    def close(self):
        self.mydb.commit()
        self.mydb.close()

    def init_database(self):
        self.mydb = mysql.connector.connect(
            **mysql_json, auth_plugin='mysql_native_password')
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute(f"CREATE DATABASE {db_name}")
        self.mycursor.execute(f"USE {db_name}")

    def ping(self):
        """
        尝试重连
        """

        try:
            self.mydb.cmd_ping()
        except pymysql.MySQLError:
            try:
                self.mydb.reconnect()
                self.mycursor = self.mydb.cursor()
                self.mycursor.execute(f"USE {self.db_name}")
            except pymysql.MySQLError:
                return False
            else:
                return True
        else:
            return True

    @translate_tieba_name
    def create_table_pid_whitelist(self, tieba_name_eng):
        """
        创建表pid_whitelist_{tieba_name_eng}
        create_table_pid_whitelist(tieba_name)
        """

        self.mycursor.execute(
            f"SHOW TABLES LIKE 'pid_whitelist_{tieba_name_eng}'")
        if not self.mycursor.fetchone():
            self.mycursor.execute(
                f"CREATE TABLE pid_whitelist_{tieba_name_eng} (pid BIGINT NOT NULL PRIMARY KEY, record_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            self.mycursor.execute(f"""CREATE EVENT event_auto_del_pid_whitelist_{tieba_name_eng}
            ON SCHEDULE
            EVERY 1 DAY STARTS '2000-01-01 00:00:00'
            DO
            DELETE FROM pid_whitelist_{tieba_name_eng} WHERE record_time<(CURRENT_TIMESTAMP() + INTERVAL -15 DAY)""")

    @translate_tieba_name
    def add_pid(self, tieba_name_eng, pid):
        """
        向pid_whitelist_{tieba_name_eng}插入pid
        add_pid(tieba_name,pid)
        """

        try:
            self.mycursor.execute(
                f"INSERT IGNORE INTO pid_whitelist_{tieba_name_eng} VALUES ({pid},DEFAULT)")
        except pymysql.DatabaseError:
            log.error(f"MySQL Error: Failed to insert {pid}!")
            return False
        else:
            self.mydb.commit()
            return True

    @translate_tieba_name
    def has_pid(self, tieba_name_eng, pid):
        """
        检索pid_whitelist_{tieba_name_eng}中是否已有pid
        has_pid(tieba_name,pid)
        """

        try:
            self.mycursor.execute(
                f"SELECT NULL FROM pid_whitelist_{tieba_name_eng} WHERE pid={pid}")
        except pymysql.DatabaseError:
            log.error(f"MySQL Error: Failed to select {pid}!")
            return False
        else:
            return True if self.mycursor.fetchone() else False

    @translate_tieba_name
    def del_pid(self, tieba_name_eng, hour):
        """
        删除最近hour个小时pid_whitelist_{tieba_name_eng}中记录的pid
        del_pid(tieba_name,hour)
        """

        try:
            self.mycursor.execute(
                f"DELETE FROM pid_whitelist_{tieba_name_eng} WHERE record_time>(CURRENT_TIMESTAMP() + INTERVAL -{hour} HOUR)")
        except pymysql.DatabaseError:
            log.error(
                f"MySQL Error: Failed to delete pid in pid_whitelist_{tieba_name_eng}")
            return False
        else:
            self.mydb.commit()
            log.info(
                f"Successfully deleted pid in pid_whitelist_{tieba_name_eng} within {hour} hour(s)")
            return True

    @translate_tieba_name
    def set_tid(self, tieba_name_eng, tid, mode=False):
        """
        在tid_indroplist_{tieba_name_eng}中设置tid的待恢复状态
        set_tid(tieba_name,tid,mode)

        参数:
            tieba_name: str 贴吧名
            tid: int
            mode: bool 若为True则该帖需要定时恢复
        """

        try:
            self.mycursor.execute(
                f"INSERT INTO tid_indroplist_{tieba_name_eng} VALUES ({tid},{mode},DEFAULT) ON DUPLICATE KEY UPDATE need_rec={mode}")
        except pymysql.DatabaseError:
            log.error(f"MySQL Error: Failed to insert {tid}!")
            return False
        else:
            log.info(
                f"Successfully set {tid} in table of {tieba_name_eng} mode:{mode}")
            self.mydb.commit()
            return True

    @translate_tieba_name
    def get_tid(self, tieba_name_eng, tid):
        """
        获取tid_indroplist_{tieba_name_eng}中某个tid的待恢复状态
        get_tid(tieba_name,tid)

        返回值:
            mode: bool 若为True则该帖需要定时恢复
        """

        try:
            self.mycursor.execute(
                f"SELECT need_rec FROM tid_indroplist_{tieba_name_eng} WHERE tid={tid} LIMIT 1")
        except pymysql.DatabaseError:
            log.error(f"MySQL Error: Failed to select {tid}!")
            return None
        else:
            res_tuple = self.mycursor.fetchone()
            if res_tuple:
                return True if res_tuple[0] else False
            else:
                return None

    @translate_tieba_name
    def del_tid(self, tieba_name_eng, tid):
        """
        从tid_indroplist_{tieba_name_eng}中删除tid
        del_tid(tieba_name,tid)
        """

        try:
            self.mycursor.execute(
                f"DELETE FROM tid_indroplist_{tieba_name_eng} WHERE tid={tid}")
        except pymysql.DatabaseError:
            log.error(f"MySQL Error: Failed to delete {tid}!")
            return False
        else:
            log.info(
                f"Successfully deleted {tid} from table of {tieba_name_eng}")
            self.mydb.commit()
            return True

    @translate_tieba_name
    def get_tids(self, tieba_name_eng, batch_size=100):
        """
        获取tid_indroplist_{tieba_name_eng}中所有待恢复的tid
        get_tids(tieba_name,batch_size)

        参数:
            batch_size: int 分包大小

        返回值:
            tid: int
        """

        for i in range(sys.maxsize):
            try:
                self.mycursor.execute(
                    f"SELECT tid FROM tid_indroplist_{tieba_name_eng} WHERE need_rec=1 LIMIT {batch_size} OFFSET {i * batch_size}")
            except pymysql.DatabaseError:
                log.error(f"MySQL Error: Failed to select {tid}!")
                return False
            else:
                tid_list = self.mycursor.fetchall()
                for tid in tid_list:
                    yield tid[0]
                if len(tid_list) != batch_size:
                    break

    @translate_tieba_name
    def create_table_portrait(self, tieba_name_eng):
        """
        创建表portrait_{tieba_name_eng}
        create_table_portrait(tieba_name)
        """

        self.mycursor.execute(f"SHOW TABLES LIKE 'portrait_{tieba_name_eng}'")
        if not self.mycursor.fetchone():
            self.mycursor.execute(
                f"CREATE TABLE portrait_{tieba_name_eng} (portrait CHAR(36) NOT NULL PRIMARY KEY, is_white BOOL NOT NULL DEFAULT TRUE, record_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP)")

    @translate_tieba_name
    def update_portrait(self, tieba_name_eng, portrait, mode):
        """
        更新portrait在portrait_{tieba_name_eng}中的状态
        update_portrait(tieba_name,portrait,mode)
        """

        try:
            self.mycursor.execute(
                f"INSERT INTO portrait_{tieba_name_eng} VALUES ('{portrait}',{mode},DEFAULT) ON DUPLICATE KEY UPDATE is_white={mode}")
        except pymysql.DatabaseError:
            log.error(f"MySQL Error: Failed to insert {portrait}!")
            return False
        else:
            log.info(
                f"Successfully updated {portrait} to table of {tieba_name_eng} mode:{mode}")
            self.mydb.commit()
            return True

    @translate_tieba_name
    def del_portrait(self, tieba_name_eng, portrait):
        """
        从黑/白名单中删除portrait
        del_portrait(tieba_name,portrait)
        """

        try:
            self.mycursor.execute(
                f"DELETE FROM portrait_{tieba_name_eng} WHERE portrait='{portrait}'")
        except pymysql.DatabaseError:
            log.error(f"MySQL Error: Failed to delete {portrait}!")
            return False
        else:
            log.info(
                f"Successfully deleted {portrait} from table of {tieba_name_eng}")
            self.mydb.commit()
            return True

    @translate_tieba_name
    def is_portrait_white(self, tieba_name_eng, portrait):
        """
        检索portrait的黑/白名单状态
        is_portrait_white(tieba_name,portrait)

        返回值:
            iswhite: True 白名单 / False 黑名单 / None 不在名单中
        """

        try:
            self.mycursor.execute(
                f"SELECT is_white FROM portrait_{tieba_name_eng} WHERE portrait='{portrait}'")
        except pymysql.DatabaseError:
            return None
        else:
            res_tuple = self.mycursor.fetchone()
            if res_tuple:
                return True if res_tuple[0] else False
            else:
                return None

    @translate_tieba_name
    def create_table_img_blacklist(self, tieba_name_eng):
        """
        创建表img_blacklist_{tieba_name_eng}
        create_table_img_blacklist(tieba_name)
        """

        self.mycursor.execute(
            f"SHOW TABLES LIKE 'img_blacklist_{tieba_name_eng}'")
        if not self.mycursor.fetchone():
            self.mycursor.execute(
                f"CREATE TABLE img_blacklist_{tieba_name_eng} (img_hash CHAR(16) NOT NULL PRIMARY KEY)")

    @translate_tieba_name
    def add_img_hash(self, tieba_name_eng, img_hash):
        """
        向img_blacklist_{tieba_name_eng}插入img_hash
        add_img_hash(tieba_name,img_hash)
        """

        try:
            self.mycursor.execute(
                f"INSERT IGNORE INTO img_blacklist_{tieba_name_eng} SET img_hash='{img_hash}'")
        except pymysql.DatabaseError:
            log.error(f"MySQL Error: Failed to insert {img_hash}!")
            return False
        else:
            log.info(f"Successfully add {img_hash} to table of {tieba_name_eng}")
            self.mydb.commit()
            return True

    @translate_tieba_name
    def has_img_hash(self, tieba_name_eng, img_hash):
        """
        检索img_blacklist_{tieba_name_eng}中是否已有img_hash
        has_img_hash(tieba_name,img_hash)
        """

        try:
            self.mycursor.execute(
                f"SELECT NULL FROM img_blacklist_{tieba_name_eng} WHERE img_hash='{img_hash}'")
        except pymysql.DatabaseError:
            log.error(f"MySQL Error: Failed to select {img_hash}!")
            return False
        else:
            return True if self.mycursor.fetchone() else False

    @translate_tieba_name
    def del_img_hash(self, tieba_name_eng, img_hash):
        """
        从img_blacklist_{tieba_name_eng}中删除img_hash
        del_img_hash(tieba_name,img_hash)
        """

        try:
            self.mycursor.execute(
                f"DELETE FROM img_blacklist_{tieba_name_eng} WHERE img_hash='{img_hash}'")
        except pymysql.DatabaseError:
            log.error(f"MySQL Error: Failed to delete {img_hash}!")
            return False
        else:
            log.info(
                f"Successfully deleted {img_hash} from table of {tieba_name_eng}")
            self.mydb.commit()
            return True
