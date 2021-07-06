# -*- coding:utf-8 -*-
__all__ = ('Browser',)


import os
import sys
import time
import traceback

import hashlib

import requests as req

import re
import json
import pickle

from .data_structure import *
from .logger import log


config = None
try:
    with SCRIPT_DIR.parent.joinpath('config/config.json').open('r', encoding='utf-8') as file:
        config = json.load(file)
except Exception:
    log.critical("Unable to read config.json!")
    raise


class Sessions(object):
    """
    保持会话

    参数:
        BDUSS_key: str 用于获取BDUSS
    """

    __slots__ = ['app', 'web', 'BDUSS']

    def __init__(self, BDUSS_key):

        self.app = req.Session()
        self.app.headers = req.structures.CaseInsensitiveDict({'Content-Type': 'application/x-www-form-urlencoded',
                                                               'Charset': 'UTF-8',
                                                               'User-Agent': 'bdtb for Android 12.6.3.0',
                                                               'Connection': 'Keep-Alive',
                                                               'client_logid': '1600505010776',
                                                               'client_user_token': '957339815',
                                                               'cuid': '573B24810C196E865FCB86C51EF8AC09|VDVSTWVBW',
                                                               'cuid_galaxy2': '573B24810C196E865FCB86C51EF8AC09|VDVSTWVBW',
                                                               'cuid_gid': '',
                                                               'c3_aid': 'A00-J63VLDXPDOTDMRZVGYYOLCWFVKGRXMQO-UVT3YYGX',
                                                               'client_type': '2',
                                                               'Accept-Encoding': 'gzip',
                                                               'Accept': '*/*',
                                                               'Host': 'c.tieba.baidu.com',
                                                               })

        self.web = req.Session()
        self.web.headers = req.structures.CaseInsensitiveDict({'Host': 'tieba.baidu.com',
                                                               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                                                               'Accept': '*/*',
                                                               'Accept-Language': 'zh-CN',
                                                               'Accept-Encoding': 'gzip, deflate, br',
                                                               'DNT': '1',
                                                               'Cache-Control': 'no-cache',
                                                               'Connection': 'keep-alive',
                                                               'Upgrade-Insecure-Requests': '1'
                                                               })

        self.renew_BDUSS(BDUSS_key)

    def close(self):
        self.app.close()
        self.web.close()

    def renew_BDUSS(self, BDUSS_key):
        """
        更新BDUSS

        参数:
            BDUSS_key: str
        """

        self.BDUSS = config['BDUSS'][BDUSS_key]
        self.web.cookies = req.cookies.cookiejar_from_dict(
            {'BDUSS': self.BDUSS})



class Browser(object):
    """
    贴吧浏览、参数获取等API的封装
    Browser(BDUSS_key)

    参数:
        BDUSS_key: str 用于获取BDUSS
    """

    __slots__ = ['fid_dict',
                 'sessions']

    def __init__(self, BDUSS_key):

        cache_dir = MODULE_DIR.joinpath('cache')
        cache_dir.mkdir(0o700, exist_ok=True)
        fid_cache_filepath = cache_dir.joinpath('fid_cache.pk')

        try:
            with fid_cache_filepath.open('rb') as pickle_file:
                self.fid_dict = pickle.load(pickle_file)
        except:
            log.warning(
                f"Failed to read fid_cache in `{fid_cache_filepath}`. Create a new one.")
            self.fid_dict = {}

        self.sessions = Sessions(BDUSS_key)

    def close(self):
        """
        自动缓存fid信息
        """

        fid_cache_filepath = MODULE_DIR.joinpath('cache/fid_cache.pk')

        try:
            with fid_cache_filepath.open('wb') as pickle_file:
                pickle.dump(self.fid_dict, pickle_file)
        except AttributeError:
            log.error("Failed to save fid cache!")

    @staticmethod
    def _app_sign(data: dict):
        """
        对参数字典做贴吧客户端签名
        """

        if data.__contains__('sign'):
            del data['sign']

        raw_list = []
        for key, value in data.items():
            raw_list.extend([str(key), '=', str(value)])
        raw_str = "".join(raw_list) + "tiebaclient!!!"

        md5 = hashlib.md5()
        md5.update(raw_str.encode('utf-8'))
        data['sign'] = md5.hexdigest().upper()

        return data

    def set_host(self, url):
        """
        设置消息头的host字段
        set_host(url)

        参数:
            url: str 待请求的地址
        """

        if self.sessions.set_host(url):
            return True
        else:
            log.warning(f"Wrong type of url `{url}`")
            return False

    def _get_tbs(self):
        """
        获取贴吧反csrf校验码tbs
        _get_tbs()

        返回值:
            tbs: str 反csrf校验码tbs
        """

        try:
            res = self.sessions.web.get("http://tieba.baidu.com/dc/common/tbs", timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            tbs = main_json['tbs']

        except Exception as err:
            log.error(f"Failed to get tbs Reason: {err}")
            tbs = ''

        return tbs

    def _tbname2fid(self, tieba_name):
        """
        通过贴吧名获取forum_id
        _tbname2fid(tieba_name)

        参数:
            tieba_name: str 贴吧名

        返回值:
            fid: int 该贴吧的forum_id
        """

        fid = self.fid_dict.get(tieba_name, None)

        if not fid:
            try:
                res = self.sessions.web.get(
                    "http://tieba.baidu.com/sign/info", params={'kw': tieba_name, 'ie': 'utf-8'}, timeout=(3, 10))

                if res.status_code != 200:
                    raise ValueError("status code is not 200")

                main_json = res.json()
                if int(main_json['no']):
                    raise ValueError(main_json['error'])
                if int(main_json['data']['errno']):
                    raise ValueError(main_json['data']['errmsg'])

                fid = int(main_json['data']['forum_info']
                          ['forum_info']['forum_id'])

            except Exception as err:
                error_msg = f"Failed to get fid of {tieba_name} Reason:{err}"
                log.critical(error_msg)
                raise ValueError(error_msg)

            self.fid_dict[tieba_name] = fid

        return fid

    def _get_userinfo(self, id):
        """
        通过用户名或昵称或portrait获取用户信息
        _name2portrait(name)

        参数:
            id: str user_name或nick_name或portrait

        返回值:
            user: UserInfo 用户信息
        """

        if id.startswith('tb.'):
            params = {'id': id}
        else:
            params = {'un': id}

        try:
            res = self.sessions.web.get(
                "https://tieba.baidu.com/home/get/panel", params=params, timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['no']):
                raise ValueError(main_json['error'])

            user = UserInfo(main_json['data'])

        except Exception as err:
            log.error(f"Failed to get UserInfo of {id} Reason:{err}")
            user = UserInfo()

        return user

    def get_threads(self, tieba_name, pn=1, rn=30):
        """
        使用客户端api获取首页帖子
        get_threads(tieba_name,pn=1,rn=30)

        参数:
            tieba_name: str 贴吧名
            pn: int 页码
            rn: int 每页帖子数

        返回值:
            threads: core.Threads
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   '_client_version': '12.6.3.0',
                   'kw': tieba_name,
                   'pn': pn,
                   'rn': rn
                   }

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/f/frs/page", data=self._app_sign(payload), timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            threads = Threads(main_json)

        except Exception as err:
            log.error(f"Failed to get threads of {tieba_name} Reason:{err}")
            threads = Threads()

        return threads

    def get_posts(self, tid, pn=1, rn=30):
        """
        使用客户端api获取主题帖内回复
        get_posts(tid,pn=1,rn=30)

        参数:
            tid: int 主题帖tid
            pn: int 页码
            rn: int 每页帖子数

        返回值:
            has_next: bool 是否还有下一页
            posts: core.Posts
        """

        payload = {'_client_version': '12.6.3.0',
                   'kz': tid,
                   'pn': pn,
                   'rn': rn
                   }

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/f/pb/page", data=self._app_sign(payload), timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            posts = Posts(main_json)

        except Exception as err:
            log.error(f"Failed to get posts of {tid} Reason:{err}")
            posts = Posts()

        return posts

    def get_comments(self, tid, pid, pn=1):
        """
        使用客户端api获取楼中楼回复
        get_comments(tid,pid,pn=1)

        参数:
            tid: int 主题帖tid
            pid: int 回复pid
            pn: int 页码

        返回值:
            has_next: bool 是否还有下一页
            comments: core.Comments
        """

        payload = {'_client_version': '12.6.3.0',
                   'kz': tid,
                   'pid': pid,
                   'pn': pn
                   }

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/f/pb/floor", data=self._app_sign(payload), timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            comments = Comments(main_json)

        except Exception as err:
            log.error(f"Failed to get comments of {pid} in {tid} Reason:{err}")
            comments = Comments()

        return comments

    def get_self_ats(self):
        """
        获取@信息

        get_self_at()
        """

        payload = {'BDUSS': self.sessions.BDUSS}

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/u/feed/atme", data=self._app_sign(payload), timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(f"Failed to get ats Reason:{err}")
            return []

        ats = []
        for at_raw in main_json['at_list']:
            at = At()
            at.tieba_name = at_raw['fname']
            at.tid = at_raw['thread_id']
            at.pid = at_raw['post_id']
            at._text = at_raw['content'].lstrip()
            at.user = UserInfo(at_raw['quote_user'])
            at.create_time = at_raw['time']
            ats.append(at)

        return ats

    def set_privacy(self, tid, hide=True):
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
                       '_client_id': 'wappc_1600500414046_633',
                       '_client_type': 2,
                       '_client_version': '12.6.3.0',
                       '_phone_imei': '000000000000000',
                       'cuid': self.sessions.app_headers['cuid'],
                       'cuid_galaxy2': self.sessions.app_headers['cuid_galaxy2'],
                       'cuid_gid': '',
                       'forum_id': posts[0].fid,
                       'is_hide': hide,
                       'model': 'TAS-AN00',
                       'net_type': 1,
                       'post_id': posts[0].pid,
                       'tbs': self._get_tbs(),
                       'thread_id': tid
                       }

            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/thread/setPrivacy", data=self._app_sign(payload), timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(f"Failed to set privacy to {tid} Reason:{err}")
            return False

        log.info(f"Successfully set privacy to {tid}")
        return True

    def block(self, tieba_name, user, day, reason='null'):
        """
        使用客户端api的封禁，支持小吧主、语音小编封10天
        block(tieba_name,user,day,reason='null')

        参数:
            tieba_name: str 吧名
            user: UserInfo类 待封禁用户信息
            day: int 封禁天数
            reason: str 封禁理由（可选）

        返回值:
            flag: bool 操作是否成功
            user: UserInfo类 补充后的用户信息
        """

        if not user.user_name:
            if user.portrait:
                user = self._get_userinfo(user.portrait)
            elif user.nick_name:
                user = self._get_userinfo(user.nick_name)
            else:
                log.error(f"Empty params in {tieba_name}")
                return False, user

        payload = {'BDUSS': self.sessions.BDUSS,
                   '_client_version': '12.6.3.0',
                   'day': day,
                   'fid': self._tbname2fid(tieba_name),
                   'nick_name': user.nick_name if user.nick_name else user.user_name,
                   'ntn': 'banid',
                   'portrait': user.portrait,
                   'post_id': 'null',
                   'reason': reason,
                   'tbs': self._get_tbs(),
                   'un': user.user_name,
                   'word': tieba_name,
                   'z': '6955178525',
                   }

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/bawu/commitprison", data=self._app_sign(payload), timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(
                f"Failed to block {user.logname} in {tieba_name} Reason:{err}")
            return False, user

        log.info(
            f"Successfully blocked {user.logname} in {tieba_name} for {payload['day']} days")
        return True, user

    def del_thread(self, tieba_name, tid):
        """
        删除主题帖
        del_thread(tieba_name,tid)

        参数:
            tieba_name: str 帖子所在的贴吧名
            tid: int 待删除的主题帖tid

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'commit_from': 'pb',
                   'ie': 'utf-8',
                   'tbs': self._get_tbs(),
                   'kw': tieba_name,
                   'fid': self._tbname2fid(tieba_name),
                   'tid': tid
                   }

        try:
            res = self.sessions.web.post(
                "https://tieba.baidu.com/f/commit/thread/delete", data=payload, timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['err_code']):
                raise ValueError(main_json['err_code'])

        except Exception as err:
            log.error(
                f"Failed to delete thread {tid} in {tieba_name} Reason:{err}")
            return False

        log.info(f"Successfully deleted thread {tid} in {tieba_name}")
        return True

    def del_threads(self, tieba_name, tids):
        """
        批量删除主题帖
        del_threads(tieba_name,tids)

        参数:
            tieba_name: str 帖子所在的贴吧名
            tids: list(int) 待删除的主题帖tid列表

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'ie': 'utf-8',
                   'tbs': self._get_tbs(),
                   'kw': tieba_name,
                   'fid': self._tbname2fid(tieba_name),
                   'tid': '_'.join([str(tid) for tid in tids]),
                   'isBan': 0
                   }

        try:
            res = self.sessions.web.post(
                "https://tieba.baidu.com/f/commit/thread/batchDelete", data=payload, timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['err_code']):
                raise ValueError(main_json['err_code'])

        except Exception as err:
            log.error(
                f"Failed to delete thread {tids} in {tieba_name}. Reason:{err}")
            return False

        log.info(f"Successfully deleted thread {tid} in {tieba_name}")
        return True

    def del_post(self, tieba_name, tid, pid):
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
                   '_client_version': '12.6.3.0',
                   'fid': self._tbname2fid(tieba_name),
                   'is_vipdel': 0,
                   'pid': pid,
                   'tbs': self._get_tbs(),
                   'z': tid
                   }

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/bawu/delpost", data=self._app_sign(payload), timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.error(f"Failed to delete post {pid} in {tid} in {tieba_name}. Reason:{err}")
            return False

        log.info(f"Successfully deleted post {pid} in {tid} in {tieba_name}")
        return True

    def blacklist_add(self, tieba_name, id):
        """
        添加用户至黑名单
        blacklist_add(tieba_name,name)

        参数:
            tieba_name: str 所在贴吧名
            id: str 用户名或昵称或portrait

        返回值:
            flag: bool 操作是否成功
        """

        user = self._get_userinfo(id)
        payload = {'tbs': self._get_tbs(),
                   'user_id': user.user_id,
                   'word': tieba_name,
                   'ie': 'utf-8'
                   }

        try:
            res = self.sessions.web.post(
                "http://tieba.baidu.com/bawu2/platform/addBlack", data=payload, timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['errno']):
                raise ValueError(main_json['errmsg'])

        except Exception as err:
            log.error(
                f"Failed to add {user.logname} to black_list in {tieba_name}. Reason:{err}")
            return False

        log.info(
            f"Successfully added {user.logname} to black_list in {tieba_name}")
        return True

    def blacklist_get(self, tieba_name, pn=1):
        """
        获取黑名单列表
        blacklist_get(tieba_name,pn=1)

        参数:
            tieba_name: str 所在贴吧名
            pn: int 页数

        返回值:
            flag: bool 操作是否成功
            black_list: list(str) 黑名单用户列表
        """

        params = {'word': tieba_name,
                  'pn': pn
                  }

        try:
            res = self.sessions.web.get(
                "http://tieba.baidu.com/bawu2/platform/listBlackUser", params=params, timeout=(3, 10))

            has_next = True if re.search(
                'class="next_page"', res.text) else False
            raw = re.search('<tbody>.*</tbody>', res.text, re.S).group()

            content = BeautifulSoup(raw, 'lxml')
            black_list = [black_raw.find("a", class_='avatar_link').text.strip(
            ) for black_raw in content.find_all("tr")]

        except Exception as err:
            log.error(
                f"Failed to get black_list of {tieba_name}. Reason:{err}")
            return False, []

        return has_next, black_list

    def blacklist_cancels(self, tieba_name, ids):
        """
        解除黑名单
        blacklist_cancels(tieba_name,ids)

        参数:
            tieba_name: str 所在贴吧名
            ids: list(str) 用户名或昵称或portrait的列表

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'ie': 'utf-8',
                   'word': tieba_name,
                   'tbs': self._get_tbs(),
                   'list[]': []}

        for id in ids:
            user = self._get_userinfo(id)
            if user.user_id:
                payload['list[]'].append(user.user_id)
        if not payload['list[]']:
            return False

        try:
            res = self.sessions.web.post(
                "http://tieba.baidu.com/bawu2/platform/cancelBlack", data=payload, timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['errno']):
                raise ValueError(main_json['errmsg'])

        except Exception as err:
            log.error(
                f"Failed to delete {ids} from black_list in {tieba_name}. Reason:{err}")
            return False

        log.info(f"Successfully deleted {ids} from black_list in {tieba_name}")
        return True

    def blacklist_cancel(self, tieba_name, id):
        """
        解除黑名单
        blacklist_cancel(tieba_name,id)

        参数:
            tieba_name: str 所在贴吧名
            id: str 用户名或昵称

        返回值:
            flag: bool 操作是否成功
        """

        if tieba_name and id:
            return self.blacklist_cancels(tieba_name, [str(id), ])
        else:
            return False

    def recover(self, tieba_name, tid, pid=0):
        """
        恢复帖子
        recover(tieba_name,tid,pid=0)

        参数:
            tieba_name: str 帖子所在的贴吧名
            tid: int 回复所在的主题帖tid
            pid: int 待恢复的回复pid

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'fn': tieba_name,
                   'fid': self._tbname2fid(tieba_name),
                   'tid_list[]': tid,
                   'pid_list[]': pid,
                   'type_list[]': 1 if pid else 0
                   }

        try:
            res = self.sessions.web.post(
                "https://tieba.baidu.com/mo/q/bawurecoverthread", data=payload, timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['no']):
                raise ValueError(main_json['error'])

        except Exception as err:
            log.error(
                f"Failed to recover tid:{tid} pid:{pid} in {tieba_name}. Reason:{err}")
            return False

        log.info(f"Successfully recovered tid:{tid} pid:{pid} in {tieba_name}")
        return True

    def unblock(self, tieba_name, id):
        """
        解封用户
        unblock(tieba_name,id)

        参数:
            tieba_name: str 所在贴吧名
            id: str 用户名或昵称或portrait

        返回值:
            flag: bool 操作是否成功
        """

        user = self._get_userinfo(id)

        payload = {'fn': tieba_name,
                   'fid': self._tbname2fid(tieba_name),
                   'block_un': user.user_name,
                   'block_uid': user.user_id,
                   'block_nickname': user.nick_name,
                   'tbs': self._get_tbs()
                   }

        try:
            res = self.sessions.web.post(
                "https://tieba.baidu.com/mo/q/bawublockclear", data=payload, timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['no']):
                raise ValueError(main_json['error'])

        except Exception as err:
            log.error(
                f"Failed to unblock {user.logname} in {tieba_name}. Reason:{err}")
            return False

        log.info(f"Successfully unblocked {user.logname} in {tieba_name}")
        return True

    def recommend(self, tieba_name, tid):
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
                   '_client_version': '12.6.3.0',
                   'forum_id': self._tbname2fid(tieba_name),
                   'tbs': self._get_tbs(),
                   'thread_id': tid
                   }

        try:
            res = self.sessions.app.post(
                "http://c.tieba.baidu.com/c/c/bawu/pushRecomToPersonalized", data=self._app_sign(payload), timeout=(3, 10))

            if res.status_code != 200:
                raise ValueError("status code is not 200")

            main_json = res.json()
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if int(main_json['data']['is_push_success']) != 1:
                raise ValueError(main_json['data']['msg'])

        except Exception as err:
            log.error(
                f"Failed to recommend {tid} in {tieba_name}. Reason:{err}")
            return False

        log.info(f"Successfully recommended {tid} in {tieba_name}")
        return True

    def refuse_appeals(self, tieba_name):
        """
        拒绝吧内所有解封申诉
        refuse_appeals(self,tieba_name)

        参数:
            tieba_name: str 所在贴吧名
        """

        def __appeal_handle(appeal_id, refuse=True):
            """
            拒绝或通过解封申诉
            __appeal_handle(appeal_id,refuse=True)

            参数:
                appeal_id: int 申诉请求的编号
                refuse: bool 是否拒绝申诉
            """

            payload = {'status': 2 if refuse else 1,
                       'reason': 'null',
                       'tbs': self._get_tbs(),
                       'appeal_id': appeal_id,
                       'forum_id': self._tbname2fid(tieba_name),
                       'ie': 'gbk'
                       }

            try:
                res = self.sessions.web.post(
                    "http://tieba.baidu.com/bawu2/appeal/commit", data=payload, timeout=(3, 10))

                if res.status_code != 200:
                    raise ValueError("status code is not 200")

                main_json = res.json()
                if int(main_json['errno']):
                    raise ValueError(main_json['errmsg'])

            except Exception as err:
                log.error(
                    f"Failed to handle {appeal_id} in {tieba_name}. Reason:{err}")
                return False

            log.info(
                f"Successfully handled {appeal_id} in {tieba_name} refuse:{refuse}")
            return True

        def __get_appeal_list(pn=1):
            """
            获取吧申诉列表
            __get_appeal_list(pn=1)

            参数:
                pn: int 页数
            """

            params = {'forum_id': self._tbname2fid(tieba_name),
                      'page': pn
                      }

            try:
                res = self.sessions.web.get(
                    "http://tieba.baidu.com/bawu2/appeal/list", params=params, timeout=(3, 10))

                if res.status_code != 200:
                    raise ValueError("status code is not 200")

                main_json = res.json()
                if int(main_json['errno']):
                    raise ValueError(main_json['errmsg'])

                has_next = True if int(
                    main_json['pageInfo']['totalPage']) else Flase

                appeal_ids = [int(raw['appeal_id'])
                              for raw in main_json['appealRecordList']]

            except Exception as err:
                log.error(
                    f"Failed to get appeal_list of {tieba_name}. Reason:{err}")
                has_next = False
                appeal_ids = []

            return has_next, appeal_ids

        has_next = True
        while has_next:
            has_next, appeal_ids = __get_appeal_list()
            for appeal_id in appeal_ids:
                __appeal_handle(appeal_id)
