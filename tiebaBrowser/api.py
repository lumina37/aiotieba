# -*- coding:utf-8 -*-
__all__ = ('Browser',)

import hashlib
import re
import sys
import time
import traceback
from io import BytesIO
from typing import NoReturn, Optional, Tuple

import cv2 as cv
import numpy as np
import requests as req
from bs4 import BeautifulSoup
from PIL import Image

from .config import config
from .data_structure import *
from .logger import log

req.packages.urllib3.disable_warnings(
    req.packages.urllib3.exceptions.InsecureRequestWarning)


class Sessions(object):
    """
    保持会话

    参数:
        BDUSS_key: str 用于获取BDUSS
    """

    __slots__ = ['app', 'web', 'BDUSS', 'STOKEN']

    def __init__(self, BDUSS_key: Optional[str] = None):

        self.app = req.Session()
        self.web = req.Session()

        if BDUSS_key:
            self.renew_BDUSS(BDUSS_key)

        self.app.headers = req.structures.CaseInsensitiveDict({'Content-Type': 'application/x-www-form-urlencoded',
                                                               'User-Agent': 'bdtb for Android 12.20.0.3',
                                                               'Connection': 'Keep-Alive',
                                                               'Accept-Encoding': 'gzip',
                                                               'Accept': '*/*',
                                                               'Host': 'c.tieba.baidu.com',
                                                               'Connection': 'keep-alive'
                                                               })
        self.web.headers = req.structures.CaseInsensitiveDict({'Host': 'tieba.baidu.com',
                                                               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0',
                                                               'Accept': '*/*',
                                                               'Accept-Encoding': 'gzip, deflate, br',
                                                               'DNT': '1',
                                                               'Cache-Control': 'no-cache',
                                                               'Connection': 'keep-alive',
                                                               'Upgrade-Insecure-Requests': '1'
                                                               })

        self.app.trust_env = False
        self.web.trust_env = False
        self.app.verify = False
        self.web.verify = False

    def close(self) -> None:
        self.app.close()
        self.web.close()

    def set_host(self, url: str) -> bool:
        match_res = re.search('://(.+?)/', url)
        if match_res:
            self.web.headers['Host'] = match_res.group(1)
            return True
        else:
            return False

    def renew_BDUSS(self, BDUSS_key: str) -> None:
        """
        更新BDUSS

        参数:
            BDUSS_key: str
        """

        self.BDUSS = config['BDUSS'][BDUSS_key]
        self.STOKEN = config['STOKEN'].get(BDUSS_key, '')
        self.web.cookies = req.cookies.cookiejar_from_dict(
            {'BDUSS': self.BDUSS, 'STOKEN': self.STOKEN})


class Browser(object):
    """
    贴吧浏览、参数获取等API的封装
    Browser(BDUSS_key)

    参数:
        BDUSS_key: str 用于获取BDUSS
    """

    __slots__ = ['fid_dict', 'sessions', '_tbs', '_tbs_renew_time']

    def __init__(self, BDUSS_key: Optional[str]):
        self.fid_dict = {}
        self.sessions = Sessions(BDUSS_key)
        self._tbs = ''
        self._tbs_renew_time = 0

    def close(self) -> NoReturn:
        pass

    def _set_host(self, url: str) -> bool:
        """
        设置消息头的host字段
        _set_host(url)

        参数:
            url: str 待请求的地址
        """

        if self.sessions.set_host(url):
            return True
        else:
            log.warning(f"Wrong type of url `{url}`")
            return False

    @staticmethod
    def _app_sign(payload: dict) -> str:
        """
        计算字典payload的贴吧客户端签名值sign
        app_sign(payload)

        返回值:
            sign: str 贴吧客户端签名值sign
        """

        raw_list = [f"{key}={value}" for key, value in payload.items()]
        raw_list.append("tiebaclient!!!")
        raw_str = "".join(raw_list)

        md5 = hashlib.md5()
        md5.update(raw_str.encode('utf-8'))
        sign = md5.hexdigest()

        return sign

    @property
    def tbs(self) -> str:
        """
        获取贴吧反csrf校验码tbs
        """

        if not self._tbs or time.time()-self._tbs_renew_time > 5:
            try:
                self._set_host("http://tieba.baidu.com/")
                res = self.sessions.web.get(
                    "http://tieba.baidu.com/dc/common/tbs", timeout=(3, 10))
                res.raise_for_status()

                main_json = res.json()
                self._tbs = main_json['tbs']

            except Exception as err:
                log.error(f"Failed to get tbs reason: {err}")
                self._tbs = ''

        return self._tbs

    def get_fid(self, tieba_name: str) -> int:
        """
        通过贴吧名获取forum_id
        get_fid(tieba_name)

        参数:
            tieba_name: str 贴吧名

        返回值:
            fid: int 该贴吧的forum_id
        """

        fid = self.fid_dict.get(tieba_name, None)

        if not fid:
            try:
                self._set_host("http://tieba.baidu.com/")
                res = self.sessions.web.get("http://tieba.baidu.com/f/commit/share/fnameShareApi", params={
                                            'fname': tieba_name, 'ie': 'utf-8'}, timeout=(3, 10))
                res.raise_for_status()

                main_json = res.json()
                if int(main_json['no']):
                    raise ValueError(main_json['error'])

                fid = int(main_json['data']['fid'])

            except Exception as err:
                error_msg = f"Failed to get fid of {tieba_name} reason:{err}"
                log.critical(error_msg)
                raise ValueError(error_msg)

            self.fid_dict[tieba_name] = fid

        return fid

    def get_userinfo(self, user: UserInfo) -> UserInfo:
        """
        补全完整版用户信息
        get_userinfo(user)

        参数:
            user: UserInfo 待补全的用户信息

        返回值:
            user: UserInfo 完整版用户信息
        """

        try:
            self._set_host("http://tieba.baidu.com/")
            res = self.sessions.web.get("https://tieba.baidu.com/home/get/panel", params={
                                        'id': user.portrait, 'un': user.user_name or user.nick_name}, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['no']):
                raise ValueError(main_json['error'])

            user_dict = main_json['data']
            sex = user_dict['sex']
            if sex == 'male':
                gender = 1
            elif sex == 'female':
                gender = 2
            else:
                gender = 0
            user = UserInfo(user_name=user_dict['name'],
                            nick_name=user_dict['show_nickname'],
                            portrait=user_dict['portrait'],
                            user_id=user_dict['id'],
                            gender=gender,
                            is_vip=bool(user_dict['vipInfo'])
                            )

        except Exception as err:
            log.error(f"Failed to get UserInfo of {user} reason:{err}")
            user = UserInfo()

        return user

    def get_userinfo_weak(self, user: BasicUserInfo) -> BasicUserInfo:
        """
        补全简略版用户信息
        get_userinfo_weak(user)

        参数:
            user: BasicUserInfo 待补全的用户信息

        返回值:
            user: BasicUserInfo 简略版用户信息，仅保证包含portrait、user_id和user_name
        """

        if user.user_name:
            return self.name2userinfo(user)
        elif user.user_id:
            return self.uid2userinfo(user)
        else:
            return self.get_userinfo(user)

    def name2userinfo(self, user: BasicUserInfo) -> BasicUserInfo:
        """
        通过用户名补全简略版用户信息
        由于api的编码限制，仅支持补全user_id和portrait
        name2userinfo(user)

        参数:
            user: BasicUserInfo 待补全的用户信息

        返回值:
            user: BasicUserInfo 简略版用户信息，仅保证包含portrait、user_id和user_name
        """

        params = {'un': user.user_name, 'ie': 'utf-8'}

        try:
            self._set_host("http://tieba.baidu.com/")
            res = self.sessions.web.get(
                "http://tieba.baidu.com/i/sys/user_json", params=params, timeout=(3, 10))
            res.raise_for_status()

            if not res.content:
                raise ValueError("empty response")
            main_json = res.json()

            user_dict = main_json['creator']
            user.user_id = user_dict['id']
            user.portrait = user_dict['portrait']

        except Exception as err:
            log.error(
                f"Failed to get UserInfo of {user.user_name} reason:{err}")
            user = BasicUserInfo()

        return user

    def uid2userinfo(self, user: BasicUserInfo) -> BasicUserInfo:
        """
        通过user_id补全简略版用户信息
        uid2userinfo(user)

        参数:
            user: UserInfo 待补全的用户信息

        返回值:
            user: UserInfo 简略版用户信息，仅保证包含portrait、user_id和user_name
        """

        try:
            self._set_host("http://tieba.baidu.com/")
            res = self.sessions.web.get(
                "http://tieba.baidu.com/im/pcmsg/query/getUserInfo", params={'chatUid': user.user_id}, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['errno']):
                raise ValueError(main_json['errmsg'])

            user_dict = main_json['chatUser']
            user.user_name = user_dict['uname']
            user.portrait = user_dict['portrait']

        except Exception as err:
            log.error(f"Failed to get UserInfo of {user.user_id} reason:{err}")
            user = BasicUserInfo()

        return user

    def get_threads(self, tieba_name: str, pn: int = 1) -> Threads:
        """
        使用客户端api获取首页帖子
        get_threads(tieba_name,pn=1)

        参数:
            tieba_name: str 贴吧名
            pn: int 页码

        返回值:
            threads: Threads
        """

        payload = {'_client_version': '7.9.2',  # 因新版app使用file传参，改动此处的版本号可能导致列表为空！
                   'kw': tieba_name,
                   'pn': pn,
                   'rn': 30
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/f/frs/page", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            threads = Threads(main_json)

        except Exception as err:
            log.error(f"Failed to get threads of {tieba_name} reason:{err}")
            threads = Threads()

        return threads

    def get_posts(self, tid: int, pn: int = 1) -> Posts:
        """
        使用客户端api获取主题帖内回复
        get_posts(tid,pn=1)

        参数:
            tid: int 主题帖tid
            pn: int 页码

        返回值:
            has_next: bool 是否还有下一页
            posts: Posts
        """

        payload = {'_client_version': '12.20.0.3',
                   'kz': tid,
                   'pn': pn,
                   'rn': 30
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/f/pb/page", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            posts = Posts(main_json)

        except Exception as err:
            log.error(f"Failed to get posts of {tid} reason:{err}")
            posts = Posts()

        return posts

    def get_comments(self, tid: int, pid: int, pn: int = 1) -> Comments:
        """
        使用客户端api获取楼中楼回复
        get_comments(tid,pid,pn=1)

        参数:
            tid: int 主题帖tid
            pid: int 回复pid
            pn: int 页码

        返回值:
            has_next: bool 是否还有下一页
            comments: Comments
        """

        payload = {'_client_version': '12.20.0.3',
                   'kz': tid,
                   'pid': pid,
                   'pn': pn
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/f/pb/floor", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            comments = Comments(main_json)

        except Exception as err:
            log.error(f"Failed to get comments of {pid} in {tid} reason:{err}")
            comments = Comments()

        return comments

    def block(self, tieba_name: str, user: UserInfo, day: int, reason: str = '') -> bool:
        """
        使用客户端api的封禁，支持小吧主、语音小编封10天
        block(tieba_name,user,day,reason='')

        参数:
            tieba_name: str 贴吧名
            user: UserInfo 待封禁用户信息
            day: int 封禁天数
            reason: str 封禁理由（可选）

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   'day': day,
                   'fid': self.get_fid(tieba_name),
                   'nick_name': user.show_name,
                   'ntn': 'banid',
                   'portrait': user.portrait,
                   'reason': reason,
                   'tbs': self.tbs,
                   'un': user.user_name,
                   'word': tieba_name,
                   'z': '9998732423',
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/bawu/commitprison", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(
                f"Failed to block {user.log_name} in {tieba_name} reason:{err}")
            return False, user

        log.info(
            f"Successfully blocked {user.log_name} in {tieba_name} for {payload['day']} days")
        return True, user

    def unblock(self, tieba_name: str, user: BasicUserInfo) -> bool:
        """
        解封用户
        unblock(tieba_name,user)

        参数:
            tieba_name: str 贴吧名
            user: BasicUserInfo 基本用户信息

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'fn': tieba_name,
                   'fid': self.get_fid(tieba_name),
                   'block_un': user.user_name,
                   'block_uid': user.user_id,
                   'block_nickname': user.nick_name,
                   'tbs': self.tbs
                   }

        try:
            self._set_host("http://tieba.baidu.com/")
            res = self.sessions.web.post(
                "https://tieba.baidu.com/mo/q/bawublockclear", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['no']):
                raise ValueError(main_json['error'])

        except Exception as err:
            log.error(
                f"Failed to unblock {user.log_name} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully unblocked {user.log_name} in {tieba_name}")
        return True

    def del_thread(self, tieba_name: str, tid: int, is_frs_mask: bool = False) -> bool:
        """
        删除主题帖
        del_thread(tieba_name,tid,is_frs_mask=False)

        参数:
            tieba_name: str 帖子所在的贴吧名
            tid: int 待删除的主题帖tid
            is_frs_mask: bool False则删帖，True则屏蔽帖，默认为False

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   'fid': self.get_fid(tieba_name),
                   'is_frs_mask': int(is_frs_mask),
                   'tbs': self.tbs,
                   'z': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/bawu/delthread", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(
                f"Failed to delete thread {tid} in {tieba_name} reason:{err}")
            return False

        log.info(
            f"Successfully deleted thread {tid} hide:{is_frs_mask} in {tieba_name}")
        return True

    def del_post(self, tieba_name: str, tid: int, pid: int) -> bool:
        """
        删除回复
        del_post(tieba_name,tid,pid)

        参数:
            tieba_name: str 帖子所在的贴吧名
            tid: int 回复所在的主题帖tid
            pid: int 待删除的回复pid

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   'fid': self.get_fid(tieba_name),
                   'pid': pid,
                   'tbs': self.tbs,
                   'z': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/bawu/delpost", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(
                f"Failed to delete post {pid} in {tid} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully deleted post {pid} in {tid} in {tieba_name}")
        return True

    def recover(self, tieba_name, tid: int = 0, pid: int = 0, is_frs_mask: bool = False) -> bool:
        """
        恢复帖子
        recover(tieba_name,tid=0,pid=0,is_frs_mask=False)

        参数:
            tieba_name: str 帖子所在的贴吧名
            tid: int 回复所在的主题帖tid
            pid: int 待恢复的回复pid
            is_frs_mask: bool False则恢复删帖，True则取消屏蔽主题帖，默认为False

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'fn': tieba_name,
                   'fid': self.get_fid(tieba_name),
                   'tid_list[]': tid,
                   'pid_list[]': pid,
                   'type_list[]': 1 if pid else 0,
                   'is_frs_mask_list[]': int(is_frs_mask)
                   }

        try:
            self._set_host("http://tieba.baidu.com/")
            res = self.sessions.web.post(
                "https://tieba.baidu.com/mo/q/bawurecoverthread", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['no']):
                raise ValueError(main_json['error'])

        except Exception as err:
            log.error(
                f"Failed to recover tid:{tid} pid:{pid} in {tieba_name}. reason:{err}")
            return False

        log.info(
            f"Successfully recovered tid:{tid} pid:{pid} hide:{is_frs_mask} in {tieba_name}")
        return True

    def recommend(self, tieba_name: str, tid: int) -> bool:
        """
        推荐上首页
        recommend(tieba_name,tid)

        参数:
            tieba_name: str 帖子所在贴吧名
            tid: int 待推荐的主题帖tid

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   'forum_id': self.get_fid(tieba_name),
                   'thread_id': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/bawu/pushRecomToPersonalized", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if int(main_json['data']['is_push_success']) != 1:
                raise ValueError(main_json['data']['msg'])

        except Exception as err:
            log.error(
                f"Failed to recommend {tid} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully recommended {tid} in {tieba_name}")
        return True

    def good(self, tieba_name: str, tid: int, cid: int = 0) -> bool:
        """
        加精主题帖
        good(tieba_name,tid,cid=0)

        参数:
            tieba_name: str 帖子所在贴吧名
            tid: int 待加精的主题帖tid
            cid: int 将主题帖加到从左往右数的第cid个（不包括“全部”在内）精华分区。cid默认为0即不分区

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   'cid': cid,
                   'fid': self.get_fid(tieba_name),
                   'ntn': 'set',
                   'tbs': self.tbs,
                   'word': tieba_name,
                   'z': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/bawu/commitgood", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(
                f"Failed to add {tid} to goodlist in {tieba_name}. reason:{err}")
            return False

        log.info(
            f"Successfully add {tid} to goodlist in {tieba_name}. cid:{cid}")
        return True

    def ungood(self, tieba_name: str, tid: int) -> bool:
        """
        撤精主题帖
        ungood(tieba_name,tid)

        参数:
            tieba_name: str 帖子所在贴吧名
            tid: int 待撤精的主题帖tid

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   'fid': self.get_fid(tieba_name),
                   'tbs': self.tbs,
                   'word': tieba_name,
                   'z': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/bawu/commitgood", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(
                f"Failed to remove {tid} from goodlist in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully removed {tid} from goodlist in {tieba_name}")
        return True

    def top(self, tieba_name: str, tid: int) -> bool:
        """
        置顶主题帖
        top(tieba_name,tid)

        参数:
            tieba_name: str 帖子所在贴吧名
            tid: int 待置顶的主题帖tid

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   'fid': self.get_fid(tieba_name),
                   'ntn': 'set',
                   'tbs': self.tbs,
                   'word': tieba_name,
                   'z': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/bawu/committop", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(
                f"Failed to add {tid} to toplist in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully add {tid} to toplist in {tieba_name}")
        return True

    def untop(self, tieba_name: str, tid: int) -> bool:
        """
        撤销置顶主题帖
        untop(tieba_name,tid)

        参数:
            tieba_name: str 帖子所在贴吧名
            tid: int 待撤销置顶的主题帖tid

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   'fid': self.get_fid(tieba_name),
                   'tbs': self.tbs,
                   'word': tieba_name,
                   'z': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/bawu/committop", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(
                f"Failed to remove {tid} from toplist in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully removed {tid} from toplist in {tieba_name}")
        return True

    def get_blacklist(self, tieba_name: str) -> BasicUserInfo:
        """
        获取贴吧黑名单
        get_blacklist(tieba_name)

        参数:
            tieba_name: str 贴吧名

        迭代返回值:
            user: BasicUserInfo 基本用户信息
        """

        def _get_pn_blacklist(pn: int) -> BasicUserInfo:
            """
            获取pn页的黑名单
            _get_pn_blacklist(pn)

            迭代返回值:
                user: BasicUserInfo 基本用户信息
            """

            try:
                res = self.sessions.web.get(
                    "http://tieba.baidu.com/bawu2/platform/listBlackUser", params={'word': tieba_name, 'pn': pn})
                res.raise_for_status()

                soup = BeautifulSoup(res.text, 'lxml')
                items = soup.find_all('td', class_='left_cell')
                if not items:
                    raise StopIteration

                for item in items:
                    user_info_item = item.previous_sibling.input
                    user = BasicUserInfo(user_name=user_info_item['data-user-name'],
                                         user_id=int(
                                             user_info_item['data-user-id']),
                                         portrait=item.a.img['src'][43:])
                    yield user

            except StopIteration:
                raise
            except Exception as err:
                log.error(
                    f"Failed to get blacklist of {tieba_name} pn:{pn} reason:{err}")

        for pn in range(1, sys.maxsize):
            try:
                yield from _get_pn_blacklist(pn)
            except RuntimeError:  # need Python 3.7+ https://www.python.org/dev/peps/pep-0479/
                return

    def blacklist_add(self, tieba_name: str, user: BasicUserInfo) -> bool:
        """
        添加用户至黑名单
        blacklist_add(tieba_name,user)

        参数:
            tieba_name: str 贴吧名
            user: BasicUserInfo 基本用户信息

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'tbs': self.tbs,
                   'user_id': user.user_id,
                   'word': tieba_name,
                   'ie': 'utf-8'
                   }

        try:
            self._set_host("http://tieba.baidu.com/")
            res = self.sessions.web.post(
                "http://tieba.baidu.com/bawu2/platform/addBlack", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['errno']):
                raise ValueError(main_json['errmsg'])

        except Exception as err:
            log.error(
                f"Failed to add {user.log_name} to black_list in {tieba_name}. reason:{err}")
            return False

        log.info(
            f"Successfully added {user.log_name} to black_list in {tieba_name}")
        return True

    def blacklist_cancels(self, tieba_name: str, users: list[BasicUserInfo]) -> bool:
        """
        解除黑名单
        blacklist_cancels(tieba_name,users)

        参数:
            tieba_name: str 贴吧名
            users: List[BasicUserInfo] 基本用户信息的列表

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'word': tieba_name,
                   'tbs': self.tbs,
                   'list[]': [user.user_id for user in users],
                   'ie': 'utf-8'
                   }

        try:
            self._set_host("http://tieba.baidu.com/")
            res = self.sessions.web.post(
                "http://tieba.baidu.com/bawu2/platform/cancelBlack", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['errno']):
                raise ValueError(main_json['errmsg'])

        except Exception as err:
            log.error(
                f"Failed to remove users from black_list in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully removed users from black_list in {tieba_name}")
        return True

    def blacklist_cancel(self, tieba_name: str, user: BasicUserInfo) -> bool:
        """
        解除黑名单
        blacklist_cancel(tieba_name,user)

        参数:
            tieba_name: str 贴吧名
            user: BasicUserInfo 基本用户信息

        返回值:
            flag: bool 操作是否成功
        """

        if tieba_name and user.user_id:
            return self.blacklist_cancels(tieba_name, [user, ])
        else:
            return False

    def refuse_appeals(self, tieba_name: str) -> bool:
        """
        拒绝吧内所有解封申诉
        refuse_appeals(tieba_name)

        参数:
            tieba_name: str 贴吧名

        返回值:
            flag: bool 操作是否成功
        """

        def _appeal_handle(appeal_id: int, refuse: bool = True) -> bool:
            """
            拒绝或通过解封申诉
            _appeal_handle(appeal_id,refuse=True)

            参数:
                appeal_id: int 申诉请求的编号
                refuse: bool 是否拒绝申诉
            """

            payload = {'fn': tieba_name,
                       'fid': self.get_fid(tieba_name),
                       'status': 2 if refuse else 1,
                       'refuse_reason': 'Auto Refuse',
                       'appeal_id': appeal_id
                       }

            try:
                self._set_host("https://tieba.baidu.com/")
                res = self.sessions.web.post(
                    "https://tieba.baidu.com/mo/q/bawuappealhandle", data=payload, timeout=(3, 10))
                res.raise_for_status()

                main_json = res.json()
                if int(main_json['no']):
                    raise ValueError(main_json['error'])

            except Exception as err:
                log.error(
                    f"Failed to handle {appeal_id} in {tieba_name}. reason:{err}")
                return False

            log.info(
                f"Successfully handled {appeal_id} in {tieba_name}. refuse:{refuse}")
            return True

        def _get_appeal_list() -> int:
            """
            迭代返回申诉请求的编号(appeal_id)
            _get_appeal_list()

            迭代返回值:
                appeal_id: int 申诉请求的编号
            """

            params = {'fn': tieba_name,
                      'fid': self.get_fid(tieba_name)
                      }

            try:
                self._set_host("https://tieba.baidu.com/")
                while 1:
                    res = self.sessions.web.get(
                        "https://tieba.baidu.com/mo/q/bawuappeal", params=params, timeout=(3, 10))
                    res.raise_for_status()

                    soup = BeautifulSoup(res.text, 'lxml')

                    items = soup.find_all(
                        'li', class_='appeal_list_item j_appeal_list_item')
                    if not items:
                        return
                    for item in items:
                        appeal_id = int(
                            re.search('aid=(\d+)', item.a['href']).group(1))
                        yield appeal_id

            except Exception as err:
                log.error(
                    f"Failed to get appeal_list of {tieba_name}. reason:{err}")
                return

        for appeal_id in _get_appeal_list():
            _appeal_handle(appeal_id)

    def url2image(self, img_url: str) -> Optional[np.ndarray]:
        """
        从链接获取静态图像。若为gif则仅读取第一帧即透明通道帧
        url2image(img_url)

        返回值:
            image: numpy.array 图像
        """

        try:
            self._set_host(img_url)
            res = self.sessions.web.get(img_url, timeout=(3, 10))
            pil_image = Image.open(BytesIO(res.content))
            image = cv.cvtColor(np.asarray(pil_image), cv.COLOR_RGB2BGR)

        except Exception as err:
            log.error(f"Failed to get image {img_url}. reason:{err}")
            image = None

        return image

    def get_self_info(self) -> BasicUserInfo:
        """
        获取本账号信息
        get_self_info()

        返回值:
            user: BasicUserInfo 简略版用户信息，仅保证包含portrait、user_id和user_name
        """

        payload = {'_client_version': '12.19.1.0',
                   'bdusstoken': self.sessions.BDUSS,
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/s/login", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            user_dict = main_json['user']
            user = BasicUserInfo(user_name=user_dict['name'],
                                 portrait=user_dict['portrait'],
                                 user_id=user_dict['id'])

        except Exception as err:
            log.error(f"Failed to get msg reason:{err}")
            user = BasicUserInfo()

        return user

    def get_newmsg(self) -> dict[str, bool]:
        """
        获取消息通知
        get_newmsg()

        返回值:
            msg: Dict[str,bool] msg字典，True表示有新内容
            {'fans': 新粉丝,
             'replyme': 新回复,
             'atme': 新@,
             'agree': 新赞同,
             'pletter': 新私信,
             'bookmark': 新收藏,
             'count': 新通知}
        """

        payload = {'BDUSS': self.sessions.BDUSS}
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/s/msg", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            msg = {key: bool(int(value))
                   for key, value in main_json['message'].items()}

        except Exception as err:
            log.error(f"Failed to get msg reason:{err}")
            msg = {'fans': False,
                   'replyme': False,
                   'atme': False,
                   'agree': False,
                   'pletter': False,
                   'bookmark': False,
                   'count': False}

        return msg

    def get_ats(self) -> list[At]:
        """
        获取@信息
        get_ats()

        返回值:
            Ats: at列表
        """

        payload = {'BDUSS': self.sessions.BDUSS}
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/u/feed/atme", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            ats = Ats(main_json)

        except Exception as err:
            log.error(f"Failed to get ats reason:{err}")
            ats = Ats()

        return ats

    def get_homepage(self, portrait: str) -> Tuple[UserInfo, list[Thread]]:
        """
        获取用户个人页
        get_homepage(portrait)

        参数:
            portrait: str 用户portrait

        返回值:
            user: UserInfo 用户信息
            threads: List[Thread] 帖子列表
        """

        payload = {'_client_type': 2,  # 删除该字段会导致post_list为空
                   '_client_version': '12.19.1.0',  # 删除该字段会导致post_list和dynamic_list为空
                   'friend_uid_portrait': portrait,
                   'need_post_count': 1,  # 删除该字段会导致无法获取发帖回帖数量
                   # 'uid':user_id  # 用该字段检查共同关注的吧
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/u/user/profile", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if not main_json.__contains__('user'):
                raise ValueError("Invalid params")

        except Exception as err:
            log.error(
                f"Failed to get profile of {portrait}. reason:{err}")
            return UserInfo(), []

        try:
            user_dict = main_json['user']
            user = UserInfo(user_name=user_dict['name'],
                            nick_name=user_dict['name_show'],
                            portrait=user_dict['portrait'],
                            user_id=user_dict['id'],
                            gender=user_dict['sex'],
                            is_vip=int(user_dict['vipInfo']['v_level']) != 0,
                            is_god=user_dict['new_god_data']['field_id'] != '',
                            priv_like=user_dict['priv_sets']['like'],
                            priv_reply=user_dict['priv_sets']['reply'])
        except Exception as err:
            log.error(
                f"Failed to init UserInfo. reason:{traceback.format_tb(err.__traceback__)[-1]}")
            user = UserInfo()

        threads = []
        for thread_raw in main_json['post_list']:
            try:
                texts = []
                for fragment in thread_raw.get('first_post_content', []):
                    ftype = int(fragment['type'])
                    if ftype in [0, 4, 9, 18]:
                        texts.append(fragment['text'])
                    elif ftype == 1:
                        texts.append(
                            f"{fragment['link']} {fragment['text']}")
                first_floor_text = ''.join(texts)

                thread = Thread(fid=int(thread_raw['forum_id']),
                                tid=int(thread_raw['thread_id']),
                                pid=int(thread_raw['post_id']),
                                user=user,
                                title=thread_raw['title'],
                                first_floor_text=first_floor_text,
                                view_num=int(thread_raw['freq_num']),
                                reply_num=int(thread_raw['reply_num']),
                                like=int(thread_raw['agree']['agree_num']),
                                dislike=int(
                                    thread_raw['agree']['disagree_num']),
                                create_time=int(thread_raw['create_time'])
                                )
            except Exception as err:
                log.error(
                    f"Failed to init Thread. reason:{traceback.format_tb(err.__traceback__)[-1]}")
                thread = Thread()

            threads.append(thread)

        return user, threads

    def get_self_forumlist(self) -> Tuple[str, int, int, int]:
        """
        获取本人关注贴吧列表
        get_self_forumlist()

        迭代返回值:
            tieba_name: str 贴吧名
            fid: int 贴吧id
            level: int 等级
            exp: int 经验值
        """

        user = self.get_self_info()

        def _parse_foruminfo(forum_dict: dict[str, str]) -> Tuple[str, int, int, int]:
            """
            解析关注贴吧的信息
            _parse_foruminfo(forum_dict)

            返回值:
                tieba_name: str 贴吧名
                fid: int 贴吧id
                level: int 等级
                exp: int 经验值
            """

            tieba_name = forum_dict['name']
            fid = int(forum_dict['id'])
            level = int(forum_dict['level_id'])
            exp = int(forum_dict['cur_score'])
            return tieba_name, fid, level, exp

        def _get_pn_forumlist(pn):
            """
            获取pn页的关注贴吧信息
            _get_pn_forumlist(pn)

            迭代返回值:
                tieba_name: str 贴吧名
                fid: int 贴吧id
                level: int 等级
                exp: int 经验值
            """

            payload = {'BDUSS': self.sessions.BDUSS,
                       '_client_version': '12.19.1.0',  # 删除该字段可直接获取前200个吧，但无法翻页
                       'friend_uid': user.user_id,
                       'page_no': pn  # 加入client_version后，使用该字段控制页数
                       }
            payload['sign'] = self._app_sign(payload)

            try:
                res = self.sessions.app.post(
                    "http://c.tieba.baidu.com/c/f/forum/like", data=payload, timeout=(3, 10))
                res.raise_for_status()

                main_json = res.json()
                if int(main_json['error_code']):
                    raise ValueError(main_json['error_msg'])

                forum_list = main_json.get('forum_list', None)
                if not forum_list:
                    return

            except Exception as err:
                log.error(
                    f"Failed to get forumlist of {user.user_id}. reason:{err}")
                return

            nonofficial_forums = forum_list.get('non-gconforum', [])
            official_forums = forum_list.get('gconforum', [])

            for forum_dict in nonofficial_forums:
                yield _parse_foruminfo(forum_dict)
            for forum_dict in official_forums:
                yield _parse_foruminfo(forum_dict)

            if len(nonofficial_forums)+len(official_forums) != 50:
                raise StopIteration

        for pn in range(1, sys.maxsize):
            try:
                yield from _get_pn_forumlist(pn)
            except RuntimeError:  # need Python 3.7+ https://www.python.org/dev/peps/pep-0479/
                return

    def get_forumlist(self, user_id: int) -> Tuple[str, int, int, int]:
        """
        获取用户关注贴吧列表
        get_forumlist(user_id)

        参数:
            user_id: int

        迭代返回值:
            tieba_name: str 贴吧名
            fid: int 贴吧id
            level: int 等级
            exp: int 经验值
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   'friend_uid': user_id,
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/f/forum/like", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            for forum in main_json.get('forum_list', []):
                fid = int(forum['id'])
                tieba_name = forum['name']
                level = int(forum['level_id'])
                exp = int(forum['cur_score'])
                yield tieba_name, fid, level, exp

        except Exception as err:
            log.error(f"Failed to get forumlist of {user_id}. reason:{err}")
            return

    def get_adminlist(self, tieba_name: str) -> str:
        """
        获取吧务用户名列表
        get_adminlist(tieba_name)

        参数:
            tieba_name: str 贴吧名

        迭代返回值:
            user_name: str 用户名
        """

        try:
            self._set_host("http://tieba.baidu.com/")
            res = self.sessions.web.get(
                "http://tieba.baidu.com/f/bawu/admin_group", params={'kw': tieba_name, 'ie': 'utf-8'}, timeout=(3, 10))
            res.raise_for_status()

            soup = BeautifulSoup(res.text, 'lxml')

            yield from {a.text for a in soup.find_all('a')}

        except Exception as err:
            log.error(f"Failed to get adminlist reason: {err}")
            return

    def get_rank(self, tieba_name: str, level_thre: int = 4) -> Tuple[str, int, int, bool]:
        """
        获取贴吧等级排行榜
        get_rank(tieba_name,level_thre=4)

        参数:
            tieba_name: str 贴吧名
            level_thre: int 等级下限阈值，等级大于等于该值的用户都会被采集

        迭代返回值:
            user_name: str 用户名
            level: int 等级
            exp: int 经验值
            is_vip: bool 是否vip
        """

        def _get_pn_rank(pn: int) -> Tuple[str, int, int, bool]:
            """
            获取pn页的排行
            _get_pn_rank(pn)
            """

            try:
                res = self.sessions.web.get(
                    "http://tieba.baidu.com/f/like/furank", params={'kw': tieba_name, 'pn': pn, 'ie': 'utf-8'})
                res.raise_for_status()

                soup = BeautifulSoup(res.text, 'lxml')
                items = soup.select('tr[class^=drl_list_item]')
                if not items:
                    raise StopIteration

                for item in items:
                    user_name_item = item.td.next_sibling
                    user_name = user_name_item.text
                    is_vip = 'drl_item_vip' in user_name_item.div['class']
                    level_item = user_name_item.next_sibling
                    # e.g. get level 16 from string "bg_lv16" by slicing [5:]
                    level = int(level_item.div['class'][0][5:])
                    if level < level_thre:
                        raise StopIteration
                    exp_item = level_item.next_sibling
                    exp = int(exp_item.text)

                    yield user_name, level, exp, is_vip

            except StopIteration:
                raise
            except Exception as err:
                log.error(
                    f"Failed to get rank of {tieba_name} pn:{pn} reason:{err}")

        for pn in range(1, sys.maxsize):
            try:
                yield from _get_pn_rank(pn)
            except RuntimeError:  # need Python 3.7+ https://www.python.org/dev/peps/pep-0479/
                return

    def get_member(self, tieba_name: str) -> Tuple[str, str, int]:
        """
        获取贴吧最新关注用户列表
        get_member(tieba_name)

        参数:
            tieba_name: str 贴吧名

        迭代返回值:
            user_name: str 用户名
            portrait: str
            level: int 等级
        """

        def _get_pn_member(pn: int) -> Tuple[str, str, int]:
            """
            获取pn页的最新关注用户列表
            _get_pn_member(pn)
            """

            try:
                res = self.sessions.web.get(
                    "http://tieba.baidu.com/bawu2/platform/listMemberInfo", params={'word': tieba_name, 'pn': pn, 'ie': 'utf-8'})
                res.raise_for_status()

                soup = BeautifulSoup(res.text, 'lxml')
                items = soup.find_all('div', class_='name_wrap')
                if not items:
                    raise StopIteration

                for item in items:
                    user_item = item.a
                    user_name = user_item['title']
                    portrait = user_item['href'][14:]
                    level_item = item.span
                    level = int(level_item['class'][1][12:])
                    yield user_name, portrait, level

            except StopIteration:
                raise
            except Exception as err:
                log.error(
                    f"Failed to get member of {tieba_name} pn:{pn} reason:{err}")

        for pn in range(1, 459):
            try:
                yield from _get_pn_member(pn)
            except RuntimeError:  # need Python 3.7+ https://www.python.org/dev/peps/pep-0479/
                return

    def like_forum(self, tieba_name: str) -> bool:
        """
        关注吧
        like_forum(tieba_name)

        参数:
            tieba_name :str 贴吧名

        返回值:
            flag: bool 操作是否成功
        """

        try:
            payload = {'BDUSS': self.sessions.BDUSS,
                       'fid': self.get_fid(tieba_name),
                       'tbs': self.tbs
                       }
            payload['sign'] = self._app_sign(payload)

            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/forum/like", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if int(main_json['error']['errno']):
                raise ValueError(main_json['error']['errmsg'])

        except Exception as err:
            log.error(f"Failed to like forum {tieba_name} reason:{err}")
            return False

        log.info(f"Successfully like forum {tieba_name}")
        return True

    def sign_forum(self, tieba_name: str) -> bool:
        """
        签到吧
        sign_forum(tieba_name)

        参数:
            tieba_name :str 贴吧名

        返回值:
            flag: bool 签到是否成功，不考虑cash的问题
        """

        try:
            # 这里列出的参数一条都不能少，少一条就不能拿cash
            payload = {'BDUSS': self.sessions.BDUSS,
                       '_client_id': 'NULL',
                       '_client_type': 2,
                       '_client_version': '12.19.1.0',
                       '_phone_imei': '000000000000000',
                       'c3_aid': 'NULL',
                       'cmode': 1,
                       'cuid': 'NULL',
                       'cuid_galaxy2': 'NULL',
                       'cuid_gid': '',
                       'event_day': '000000',
                       'fid': self.get_fid(tieba_name),
                       'first_install_time': 0,
                       'kw': tieba_name,
                       'last_update_time': 0,
                       'sign_from': 'frs',
                       'tbs': self.tbs,
                       }
            payload['sign'] = self._app_sign(payload)

            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/forum/sign", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if int(main_json['user_info']['sign_bonus_point']) == 0:
                raise ValueError("sign_bonus_point is 0")

            cash = main_json['user_info'].__contains__('get_packet_cash')

        except Exception as err:
            log.error(f"Failed to sign forum {tieba_name} reason:{err}")
            return False

        log.info(f"Successfully sign forum {tieba_name}. cash:{cash}")
        return True

    def add_post(self, tieba_name: str, tid: int, content: str) -> bool:
        """
        回帖
        add_post(tieba_name,tid,content)

        注意：
        本接口仍处于测试阶段，有一定永封风险！请谨慎使用！
        已通过的测试：cookie白板号（无头像无关注吧无发帖记录，2元/个）通过异地阿里云ip出口以3分钟的发送间隔发15条回复不吞楼不封号

        参数:
            tieba_name: str 要回复的主题帖所在吧名
            tid: int 要回复的主题帖的tid
            content: str 回复内容

        返回值:
            flag: bool 回帖是否成功
        """

        try:
            payload = {'BDUSS': self.sessions.BDUSS,
                       '_client_id': 'wappc_1643365995770_873',
                       '_client_type': 2,
                       '_client_version': '9.1.0.0',
                       '_phone_imei': '000000000000000',
                       'anonymous': 1,
                       'barrage_time': 0,
                       'can_no_forum': 0,
                       'content': content,
                       'cuid': '89EC02B413436B80CB1A8873CD56AFFF|V6JXX7UB7',
                       'cuid_galaxy2': '89EC02B413436B80CB1A8873CD56AFFF|V6JXX7UB7',
                       'cuid_gid': '',
                       'entrance_type': 0,
                       'fid': self.get_fid(tieba_name),
                       'from': '1008621x',
                       'from_fourm_id': 'null',
                       'is_ad': 0,
                       'is_barrage': 0,
                       'is_feedback': 0,
                       'kw': tieba_name,
                       'model': 'LIO-AN00',
                       'name_show': '',
                       'net_type': 1,
                       'new_vcode': 1,
                       'post_from': 3,
                       'reply_uid': 'null',
                       'stoken': '',
                       'subapp_type': 'mini',
                       'tbs': self.tbs,
                       'tid': tid,
                       'timestamp': int(time.time()),
                       'v_fid': '',
                       'v_fname': '',
                       'vcode_tag': 12,
                       'z_id': 'NULL'
                       }
            payload['sign'] = self._app_sign(payload)

            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/post/add", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(f"Failed to add post in {tid} reason:{err}")
            return False

        log.info(f"Successfully add post in {tid}")
        return True

    def set_privacy(self, tid: int, hide: bool = True) -> bool:
        """
        隐藏主题帖
        set_privacy(tid)

        参数:
            tid: int 主题帖tid
            hide: bool 是否设为隐藏

        返回值:
            flag: bool 操作是否成功
        """

        posts = self.get_posts(tid)
        if not posts:
            log.error(f"Failed to set privacy to {tid}")
            return False

        try:
            payload = {'BDUSS': self.sessions.BDUSS,
                       'forum_id': posts[0].fid,
                       'is_hide': int(hide),
                       'post_id': posts[0].pid,
                       'thread_id': tid
                       }
            payload['sign'] = self._app_sign(payload)

            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/thread/setPrivacy", data=payload, timeout=(3, 10))
            res.raise_for_status()

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(f"Failed to set privacy to {tid} reason:{err}")
            return False

        log.info(f"Successfully set privacy to {tid}. is_hide:{hide}")
        return True
