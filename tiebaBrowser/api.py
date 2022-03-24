# -*- coding:utf-8 -*-
__all__ = ['Browser']

import asyncio
import hashlib
import json
import re
import socket
import sys
import time
from io import BytesIO
from types import TracebackType
from typing import Dict, NoReturn, Optional, Tuple, Type, Union

import aiohttp
import cv2 as cv
import numpy as np
import yarl
from bs4 import BeautifulSoup
from google.protobuf.json_format import ParseDict
from PIL import Image

from .config import config
from .data_structure import *
from .logger import log
from .tieba_proto import *


class Sessions(object):
    """
    保持会话

    参数:
        BDUSS_key: str 用于获取BDUSS
    """

    __slots__ = ['_timeout', '_connector', 'app',
                 'app_proto', 'web', 'BDUSS', 'STOKEN']

    def __init__(self, BDUSS_key: Optional[str] = None) -> NoReturn:

        self._timeout = aiohttp.ClientTimeout(
            connect=5, sock_connect=3, sock_read=10)
        self._connector = aiohttp.TCPConnector(
            verify_ssl=False, keepalive_timeout=90, limit=None, family=socket.AF_INET)

        # Init app client
        app_headers = {aiohttp.hdrs.USER_AGENT: 'bdtb for Android 12.22.1.0',
                       aiohttp.hdrs.CONNECTION: 'keep-alive',
                       aiohttp.hdrs.ACCEPT_ENCODING: 'gzip',
                       aiohttp.hdrs.HOST: 'c.tieba.baidu.com',
                       }
        self.app = aiohttp.ClientSession(connector=self._connector, headers=app_headers, version=aiohttp.HttpVersion11, cookie_jar=aiohttp.CookieJar(
        ), connector_owner=False, raise_for_status=True, timeout=self._timeout, trust_env=False)

        # Init app protobuf client
        app_proto_headers = {aiohttp.hdrs.USER_AGENT: 'bdtb for Android 12.22.1.0',
                             'x_bd_data_type': 'protobuf',
                             aiohttp.hdrs.CONNECTION: 'keep-alive',
                             aiohttp.hdrs.ACCEPT_ENCODING: 'gzip',
                             aiohttp.hdrs.HOST: 'c.tieba.baidu.com',
                             }
        self.app_proto = aiohttp.ClientSession(connector=self._connector, headers=app_proto_headers, version=aiohttp.HttpVersion11, cookie_jar=aiohttp.CookieJar(
        ), connector_owner=False, raise_for_status=True, timeout=self._timeout, trust_env=False)

        # Init web client
        web_headers = {aiohttp.hdrs.USER_AGENT: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
                       aiohttp.hdrs.ACCEPT_ENCODING: 'gzip, deflate, br',
                       aiohttp.hdrs.CACHE_CONTROL: 'no-cache',
                       aiohttp.hdrs.CONNECTION: 'keep-alive',
                       }

        web_cookie_jar = aiohttp.CookieJar()
        if BDUSS_key:
            self.BDUSS = config['BDUSS'][BDUSS_key]
            self.STOKEN = config['STOKEN'].get(BDUSS_key, '')
            web_cookie_jar.update_cookies(
                {'BDUSS': self.BDUSS, 'STOKEN': self.STOKEN}, yarl.URL("http://tieba.baidu.com"))
        else:
            self.BDUSS = ''
            self.STOKEN = ''
        self.web = aiohttp.ClientSession(connector=self._connector, headers=web_headers, version=aiohttp.HttpVersion11,
                                         cookie_jar=web_cookie_jar, connector_owner=False, raise_for_status=True, timeout=self._timeout, trust_env=False)

    async def close(self) -> NoReturn:
        await asyncio.gather(self.app.close(), self.app_proto.close(), self.web.close(), self._connector.close(), return_exceptions=True)

    async def __aenter__(self) -> "Sessions":
        return self

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> NoReturn:
        await self.close()


class Browser(object):
    """
    贴吧浏览、参数获取等API的封装
    Browser(BDUSS_key)

    参数:
        BDUSS_key: str 用于获取BDUSS
    """

    __slots__ = ['BDUSS_key', 'fid_dict',
                 'sessions', '_tbs']

    def __init__(self, BDUSS_key: Optional[str]) -> NoReturn:
        self.BDUSS_key = BDUSS_key
        self.fid_dict = {}
        self.sessions = Sessions(BDUSS_key)
        self._tbs = ''

    async def close(self) -> NoReturn:
        await self.sessions.close()

    async def __aenter__(self) -> "Browser":
        return self

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> NoReturn:
        await self.close()

    @staticmethod
    def _app_sign(payload: dict) -> str:
        """
        计算字典payload的贴吧客户端签名值sign
        app_sign(payload)

        返回值:
            sign: str 贴吧客户端签名值sign
        """

        raw_list = [f"{key}={value}" for key,
                    value in payload.items() if key != 'sign']
        raw_list.append("tiebaclient!!!")
        raw_str = "".join(raw_list)

        md5 = hashlib.md5()
        md5.update(raw_str.encode('utf-8'))
        sign = md5.hexdigest().upper()

        return sign

    @staticmethod
    def get_tieba_multipart_writer(proto_bytes):
        """
        将proto封装为贴吧客户端专用的aiohttp.MultipartWriter

        参数:
            proto_bytes: Bytes protobuf序列化后的二进制数据

        返回值:
            writer: aiohttp.MultipartWriter 只可用于贴吧客户端
        """

        writer = aiohttp.MultipartWriter(
            'form-data', boundary="*--asoul-diana-bilibili-uid672328094")
        payload_headers = {aiohttp.hdrs.CONTENT_DISPOSITION: aiohttp.helpers.content_disposition_header(
            'form-data', name='data', filename='file')}
        payload = aiohttp.BytesPayload(
            proto_bytes, content_type='', headers=payload_headers)
        writer.append_payload(payload)

        # 删除无用参数
        writer._parts[0][0]._headers.popone(aiohttp.hdrs.CONTENT_TYPE)
        writer._parts[0][0]._headers.popone(aiohttp.hdrs.CONTENT_LENGTH)

        return writer

    async def get_tbs(self) -> str:
        """
        获取贴吧反csrf校验码tbs
        get_tbs()

        返回值:
            tbs: str 贴吧反csrf校验码tbs
        """

        if not self._tbs:
            await self.get_self_info()

        return self._tbs

    async def get_fid(self, tieba_name: str) -> int:
        """
        通过贴吧名获取forum_id
        get_fid(tieba_name)

        参数:
            tieba_name: str 贴吧名

        返回值:
            fid: int 该贴吧的forum_id
        """

        fid = self.fid_dict.get(tieba_name, 0)

        if not fid:
            try:
                res = await self.sessions.web.get("http://tieba.baidu.com/f/commit/share/fnameShareApi", params={'fname': tieba_name, 'ie': 'utf-8'})

                main_json = await res.json(content_type='text/html')
                if int(main_json['no']):
                    raise ValueError(main_json['error'])

                fid = int(main_json['data']['fid'])

            except Exception as err:
                log.warning(f"Failed to get fid of {tieba_name}. reason:{err}")
                fid = 0
            else:
                self.fid_dict[tieba_name] = fid

        return fid

    async def get_userinfo(self, _id: Union[str, int]) -> UserInfo:
        """
        补全完整版用户信息
        get_userinfo(user)

        参数:
            user: UserInfo 待补全的用户信息

        返回值:
            user: UserInfo 完整版用户信息
        """

        user = UserInfo(_id)
        if user.user_id:
            return await self._uid2userinfo(user)
        else:
            return await self._name2userinfo(user)

    async def get_userinfo_weak(self, _id: Union[str, int]) -> BasicUserInfo:
        """
        补全简略版用户信息
        get_userinfo_weak(user)

        参数:
            user: BasicUserInfo 待补全的用户信息

        返回值:
            user: BasicUserInfo 简略版用户信息，仅保证包含portrait、user_id和user_name
        """

        user = BasicUserInfo(_id)
        if user.user_id:
            return await self._uid2userinfo_weak(user)
        elif user.user_name:
            return await self._user_name2userinfo_weak(user)
        else:
            return await self._name2userinfo(user)

    async def _name2userinfo(self, user: UserInfo) -> UserInfo:
        """
        通过用户名或昵称补全完整版用户信息
        _name2userinfo(user)

        参数:
            user: UserInfo 待补全的用户信息

        返回值:
            user: UserInfo 完整版用户信息
        """

        try:
            res = await self.sessions.web.get("https://tieba.baidu.com/home/get/panel", params={'id': user.portrait, 'un': user.user_name or user.nick_name})

            main_json = await res.json()
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

            user = UserInfo()
            user.user_name = user_dict['name']
            user.nick_name = user_dict['show_nickname']
            user.portrait = user_dict['portrait']
            user.user_id = user_dict['id']
            user.gender = gender
            user.is_vip = bool(user_dict['vipInfo'])

        except Exception as err:
            log.warning(
                f"Failed to get UserInfo of {user.log_name}. reason:{err}")
            user = UserInfo()

        return user

    async def _user_name2userinfo_weak(self, user: BasicUserInfo) -> BasicUserInfo:
        """
        通过用户名补全简略版用户信息
        由于api的编码限制，仅支持补全user_id和portrait
        _user_name2userinfo_weak(user)

        参数:
            user: BasicUserInfo 待补全的用户信息

        返回值:
            user: BasicUserInfo 简略版用户信息，仅保证包含portrait、user_id和user_name
        """

        params = {'un': user.user_name, 'ie': 'utf-8'}

        try:
            res = await self.sessions.web.get("http://tieba.baidu.com/i/sys/user_json", params=params)

            text = await res.text(errors='ignore')
            main_json = json.loads(text)
            if not main_json:
                raise ValueError("empty response")

            user_dict = main_json['creator']
            user.user_id = user_dict['id']
            user.portrait = user_dict['portrait']

        except Exception as err:
            log.warning(
                f"Failed to get UserInfo of {user.user_name}. reason:{err}")
            user = BasicUserInfo()

        return user

    async def _uid2userinfo(self, user: UserInfo) -> UserInfo:
        """
        通过user_id补全用户信息
        _uid2userinfo(user)

        参数:
            user: UserInfo 待补全的用户信息

        返回值:
            user: UserInfo 完整版用户信息
        """

        common = CommonReq_pb2.CommonReq()
        data = GetUserInfoReqIdl_pb2.GetUserInfoReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.uid = user.user_id
        userinfo_req = GetUserInfoReqIdl_pb2.GetUserInfoReqIdl()
        userinfo_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(
            userinfo_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/u/user/getuserinfo", params={'cmd': 303024}, data=multipart_writer)

            main_proto = GetUserInfoResIdl_pb2.GetUserInfoResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            user_proto = main_proto.data.user
            user = UserInfo(user_proto=user_proto)

        except Exception as err:
            log.warning(
                f"Failed to get UserInfo of {user.user_id}. reason:{err}")
            user = UserInfo()

        return user

    async def _uid2userinfo_weak(self, user: BasicUserInfo) -> BasicUserInfo:
        """
        通过user_id补全简略版用户信息
        _uid2userinfo_weak(user)
        参数:
            user: UserInfo 待补全的用户信息
        返回值:
            user: UserInfo 简略版用户信息，仅保证包含portrait、user_id和user_name
        """

        try:
            res = await self.sessions.web.get("http://tieba.baidu.com/im/pcmsg/query/getUserInfo", params={'chatUid': user.user_id})

            main_json = await res.json()
            if int(main_json['errno']):
                raise ValueError(main_json['errmsg'])

            user_dict = main_json['chatUser']
            user.user_name = user_dict['uname']
            user.portrait = user_dict['portrait']

        except Exception as err:
            log.warning(
                f"Failed to get UserInfo of {user.user_id}. reason:{err}")
            user = BasicUserInfo()

        return user

    async def get_threads(self, tieba_name: str, pn: int = 1, sort: int = 5, is_good: bool = False) -> Threads:
        """
        获取首页帖子
        get_threads(tieba_name,pn=1)

        参数:
            tieba_name: str 贴吧名
            pn: int 页码
            sort: int 排序方式，对于有热门区的贴吧来说0是热门排序1是按发布时间2报错34都是热门排序>=5是按回复时间，对无热门区的贴吧来说0是按回复时间1是按发布时间2报错>=3是按回复时间
            is_good: bool True为获取精品区帖子，False为获取普通区帖子

        返回值:
            threads: Threads
        """

        common = CommonReq_pb2.CommonReq()
        common._client_version = '12.22.1.0'
        data = FrsPageReqIdl_pb2.FrsPageReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.kw = tieba_name
        data.pn = pn
        data.rn = 90
        data.rn_need = 30
        data.is_good = is_good
        data.q_type = 2
        data.sort_type = sort
        frspage_req = FrsPageReqIdl_pb2.FrsPageReqIdl()
        frspage_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(
            frspage_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/f/frs/page", params={'cmd': 301001}, data=multipart_writer)

            main_proto = FrsPageResIdl_pb2.FrsPageResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            threads = Threads(main_proto)

        except Exception as err:
            log.warning(f"Failed to get threads of {tieba_name}. reason:{err}")
            threads = Threads()

        return threads

    async def get_posts(self, tid: int, pn: int = 1, reverse: bool = False, with_comments: bool = False, comment_sort_by_agree: bool = True, comment_rn: int = 4) -> Posts:
        """
        获取主题帖内回复
        get_posts(tid,pn=1,reverse=False,with_comments=False,comment_sort_by_agree=True,comment_rn=4)

        参数:
            tid: int 主题帖tid
            pn: int 页码
            reverse: bool True则按时间倒序请求，Flase则按时间顺序请求
            with_comment: bool True则同时请求高赞楼中楼，False则comments字段为空列表
            comment_sort_by_agree: bool True则楼中楼按点赞数顺序，False则楼中楼按时间顺序
            comment_rn: int 请求的楼中楼数量

        返回值:
            posts: Posts
        """

        common = CommonReq_pb2.CommonReq()
        common._client_version = '12.22.1.0'
        data = PbPageReqIdl_pb2.PbPageReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.kz = tid
        data.pn = pn
        data.rn = 30
        data.q_type = 2
        data.r = reverse
        if with_comments:
            data.with_floor = with_comments
            data.floor_sort_type = comment_sort_by_agree
            data.floor_rn = comment_rn
        pbpage_req = PbPageReqIdl_pb2.PbPageReqIdl()
        pbpage_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(
            pbpage_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/f/pb/page", params={'cmd': 302001}, data=multipart_writer)

            main_proto = PbPageResIdl_pb2.PbPageResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            posts = Posts(main_proto)

        except Exception as err:
            log.warning(f"Failed to get posts of {tid}. reason:{err}")
            posts = Posts()

        return posts

    async def get_comments(self, tid: int, pid: int, pn: int = 1) -> Comments:
        """
        获取楼中楼回复
        get_comments(tid,pid,pn=1)

        参数:
            tid: int 主题帖tid
            pid: int 回复pid
            pn: int 页码

        返回值:
            comments: Comments
        """

        common = CommonReq_pb2.CommonReq()
        common._client_version = '12.22.1.0'
        data = PbFloorReqIdl_pb2.PbFloorReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.kz = tid
        data.pid = pid
        data.pn = pn
        pbfloor_req = PbFloorReqIdl_pb2.PbFloorReqIdl()
        pbfloor_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(
            pbfloor_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/f/pb/floor", params={'cmd': 302002}, data=multipart_writer)

            main_proto = PbFloorResIdl_pb2.PbFloorResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            comments = Comments(main_proto)

        except Exception as err:
            log.warning(
                f"Failed to get comments of {pid} in {tid}. reason:{err}")
            comments = Comments()

        return comments

    async def block(self, tieba_name: str, user: UserInfo, day: int, reason: str = '') -> bool:
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
            user: UserInfo 补全的用户信息
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   'day': day,
                   'fid': await self.get_fid(tieba_name),
                   'nick_name': user.show_name,
                   'ntn': 'banid',
                   'portrait': user.portrait,
                   'reason': reason,
                   'tbs': await self.get_tbs(),
                   'un': user.user_name,
                   'word': tieba_name,
                   'z': '672328094',
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/commitprison", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(
                f"Failed to block {user.log_name} in {tieba_name}. reason:{err}")
            return False, user

        log.info(
            f"Successfully blocked {user.log_name} in {tieba_name} for {payload['day']} days")
        return True, user

    async def unblock(self, tieba_name: str, user: BasicUserInfo) -> bool:
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
                   'fid': await self.get_fid(tieba_name),
                   'block_un': user.user_name,
                   'block_uid': user.user_id,
                   'block_nickname': user.nick_name,
                   'tbs': await self.get_tbs()
                   }

        try:
            res = await self.sessions.web.post("https://tieba.baidu.com/mo/q/bawublockclear", data=payload)

            main_json = await res.json()
            if int(main_json['no']):
                raise ValueError(main_json['error'])

        except Exception as err:
            log.warning(
                f"Failed to unblock {user.log_name} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully unblocked {user.log_name} in {tieba_name}")
        return True

    async def del_thread(self, tieba_name: str, tid: int, is_hide: bool = False) -> bool:
        """
        删除主题帖
        del_thread(tieba_name,tid,is_hide=False)

        参数:
            tieba_name: str 帖子所在的贴吧名
            tid: int 待删除的主题帖tid
            is_hide: bool False则删帖，True则屏蔽帖，默认为False

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   'fid': await self.get_fid(tieba_name),
                   'is_frs_mask': int(is_hide),
                   'tbs': await self.get_tbs(),
                   'z': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/delthread", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(
                f"Failed to delete thread {tid} in {tieba_name}. reason:{err}")
            return False

        log.info(
            f"Successfully deleted thread {tid} hide:{is_hide} in {tieba_name}")
        return True

    async def del_post(self, tieba_name: str, tid: int, pid: int) -> bool:
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
                   'fid': await self.get_fid(tieba_name),
                   'pid': pid,
                   'tbs': await self.get_tbs(),
                   'z': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/delpost", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(
                f"Failed to delete post {pid} in {tid} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully deleted post {pid} in {tid} in {tieba_name}")
        return True

    async def recover(self, tieba_name, tid: int = 0, pid: int = 0, is_hide: bool = False) -> bool:
        """
        恢复帖子
        recover(tieba_name,tid=0,pid=0,is_hide=False)

        参数:
            tieba_name: str 帖子所在的贴吧名
            tid: int 回复所在的主题帖tid
            pid: int 待恢复的回复pid
            is_hide: bool False则恢复删帖，True则取消屏蔽主题帖，默认为False

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'fn': tieba_name,
                   'fid': await self.get_fid(tieba_name),
                   'tid_list[]': tid,
                   'pid_list[]': pid,
                   'type_list[]': 1 if pid else 0,
                   'is_frs_mask_list[]': int(is_hide)
                   }

        try:
            res = await self.sessions.web.post("https://tieba.baidu.com/mo/q/bawurecoverthread", data=payload)

            main_json = await res.json()
            if int(main_json['no']):
                raise ValueError(main_json['error'])

        except Exception as err:
            log.warning(
                f"Failed to recover tid:{tid} pid:{pid} in {tieba_name}. reason:{err}")
            return False

        log.info(
            f"Successfully recovered tid:{tid} pid:{pid} hide:{is_hide} in {tieba_name}")
        return True

    async def move(self, tieba_name: str, tid: int, to_tab_id: int, from_tab_id: int = 0):
        """
        将主题帖移动至另一分区
        move(tieba_name,tid,to_tab_id,from_tab_id=0)

        参数:
            tieba_name: str 帖子所在贴吧名
            tid: int 待移动的主题帖tid
            to_tab_id: int 目标分区id
            from_tab_id: int 来源分区id

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   '_client_version': '12.22.1.0',
                   'forum_id': await self.get_fid(tieba_name),
                   'tbs': await self.get_tbs(),
                   'threads': str([{'thread_id': tid, 'from_tab_id': from_tab_id, 'to_tab_id': to_tab_id}]).replace('\'', '"'),
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/moveTabThread", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(
                f"Failed to add {tid} to tab:{to_tab_id} in {tieba_name}. reason:{err}")
            return False

        log.info(
            f"Successfully add {tid} to tab:{to_tab_id} in {tieba_name}")
        return True

    async def recommend(self, tieba_name: str, tid: int) -> bool:
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
                   'forum_id': await self.get_fid(tieba_name),
                   'thread_id': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/pushRecomToPersonalized", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if int(main_json['data']['is_push_success']) != 1:
                raise ValueError(main_json['data']['msg'])

        except Exception as err:
            log.warning(
                f"Failed to recommend {tid} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully recommended {tid} in {tieba_name}")
        return True

    async def good(self, tieba_name: str, tid: int, cname: str = '') -> bool:
        """
        加精主题帖
        good(tieba_name,tid,cname='')

        参数:
            tieba_name: str 帖子所在贴吧名
            tid: int 待加精的主题帖tid
            cname: str 待添加的精华分区名称。cname默认为''即不分区

        返回值:
            flag: bool 操作是否成功
        """

        async def _cname2cid() -> int:
            """
            _cname2cid()
            由加精分区名cname获取cid

            闭包参数:
                tieba_name
                cname

            返回值:
                cid: int
            """

            payload = {'BDUSS': self.sessions.BDUSS,
                       'word': tieba_name,
                       }
            payload['sign'] = self._app_sign(payload)

            try:
                res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/goodlist", data=payload)

                main_json = await res.json(content_type='application/x-javascript')
                if int(main_json['error_code']):
                    raise ValueError(main_json['error_msg'])

                cid = 0
                for item in main_json['cates']:
                    if cname == item['class_name']:
                        cid = int(item['class_id'])
                        break

            except Exception as err:
                log.warning(
                    f"Failed to get cid of {cname} in {tieba_name}. reason:{err}")
                return 0

            return cid

        async def _good(cid: int = 0) -> bool:
            """
            加精主题帖
            good(cid=0)

            参数:
                cid: int 将主题帖加到cid对应的精华分区。cid默认为0即不分区

            闭包参数:
                tieba_name
                tid

            返回值:
                flag: bool 操作是否成功
            """

            payload = {'BDUSS': self.sessions.BDUSS,
                       'cid': cid,
                       'fid': await self.get_fid(tieba_name),
                       'ntn': 'set',
                       'tbs': await self.get_tbs(),
                       'word': tieba_name,
                       'z': tid
                       }
            payload['sign'] = self._app_sign(payload)

            try:
                res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/commitgood", data=payload)

                main_json = await res.json(content_type='application/x-javascript')
                if int(main_json['error_code']):
                    raise ValueError(main_json['error_msg'])

            except Exception as err:
                log.warning(
                    f"Failed to add {tid} to good:{cname} in {tieba_name}. reason:{err}")
                return False

            log.info(
                f"Successfully add {tid} to good:{cname} in {tieba_name}")
            return True

        return await _good(await _cname2cid())

    async def ungood(self, tieba_name: str, tid: int) -> bool:
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
                   'fid': await self.get_fid(tieba_name),
                   'tbs': await self.get_tbs(),
                   'word': tieba_name,
                   'z': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/commitgood", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(
                f"Failed to remove {tid} from goodlist in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully removed {tid} from goodlist in {tieba_name}")
        return True

    async def top(self, tieba_name: str, tid: int) -> bool:
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
                   'fid': await self.get_fid(tieba_name),
                   'ntn': 'set',
                   'tbs': await self.get_tbs(),
                   'word': tieba_name,
                   'z': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/committop", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(
                f"Failed to add {tid} to toplist in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully add {tid} to toplist in {tieba_name}")
        return True

    async def untop(self, tieba_name: str, tid: int) -> bool:
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
                   'fid': await self.get_fid(tieba_name),
                   'tbs': await self.get_tbs(),
                   'word': tieba_name,
                   'z': tid
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/committop", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(
                f"Failed to remove {tid} from toplist in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully removed {tid} from toplist in {tieba_name}")
        return True

    async def get_pn_blacklist(self, tieba_name: str, pn: int = 1) -> BasicUserInfo:
        """
        获取pn页的黑名单
        get_pn_blacklist(tieba_name,pn=1)

        参数:
            tieba_name: str 贴吧名
            pn: int 页码

        迭代返回值:
            user: BasicUserInfo 基本用户信息
        """

        try:
            res = await self.sessions.web.get("http://tieba.baidu.com/bawu2/platform/listBlackUser", params={'word': tieba_name, 'pn': pn})

            soup = BeautifulSoup(await res.text(), 'lxml')
            items = soup.find_all('td', class_='left_cell')
            if not items:
                return

            for item in items:
                user_info_item = item.previous_sibling.input
                user = BasicUserInfo()
                user.user_name = user_info_item['data-user-name']
                user.user_id = int(user_info_item['data-user-id'])
                user.portrait = item.a.img['src'][43:]
                yield user

        except Exception as err:
            log.warning(
                f"Failed to get blacklist of {tieba_name} pn:{pn}. reason:{err}")
            return

    async def blacklist_add(self, tieba_name: str, user: BasicUserInfo) -> bool:
        """
        添加用户至黑名单
        blacklist_add(tieba_name,user)

        参数:
            tieba_name: str 贴吧名
            user: BasicUserInfo 基本用户信息

        返回值:
            flag: bool 操作是否成功
        """

        payload = {'tbs': await self.get_tbs(),
                   'user_id': user.user_id,
                   'word': tieba_name,
                   'ie': 'utf-8'
                   }

        try:
            res = await self.sessions.web.post("http://tieba.baidu.com/bawu2/platform/addBlack", data=payload)

            main_json = await res.json()
            if int(main_json['errno']):
                raise ValueError(main_json['errmsg'])

        except Exception as err:
            log.warning(
                f"Failed to add {user.log_name} to black_list in {tieba_name}. reason:{err}")
            return False

        log.info(
            f"Successfully added {user.log_name} to black_list in {tieba_name}")
        return True

    async def blacklist_cancels(self, tieba_name: str, users: list[BasicUserInfo]) -> bool:
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
                   'tbs': await self.get_tbs(),
                   'list[]': [user.user_id for user in users],
                   'ie': 'utf-8'
                   }

        try:
            res = await self.sessions.web.post("http://tieba.baidu.com/bawu2/platform/cancelBlack", data=payload)

            main_json = await res.json()
            if int(main_json['errno']):
                raise ValueError(main_json['errmsg'])

        except Exception as err:
            log.warning(
                f"Failed to remove users from black_list in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully removed users from black_list in {tieba_name}")
        return True

    async def blacklist_cancel(self, tieba_name: str, user: BasicUserInfo) -> bool:
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
            return await self.blacklist_cancels(tieba_name, [user, ])
        else:
            return False

    async def refuse_appeals(self, tieba_name: str) -> bool:
        """
        拒绝吧内所有解封申诉
        refuse_appeals(tieba_name)

        参数:
            tieba_name: str 贴吧名

        返回值:
            flag: bool 操作是否成功
        """

        async def _appeal_handle(appeal_id: int, refuse: bool = True) -> bool:
            """
            拒绝或通过解封申诉
            _appeal_handle(appeal_id,refuse=True)

            闭包参数:
                tieba_name

            参数:
                appeal_id: int 申诉请求的编号
                refuse: bool 是否拒绝申诉
            """

            payload = {'fn': tieba_name,
                       'fid': await self.get_fid(tieba_name),
                       'status': 2 if refuse else 1,
                       'refuse_reason': 'Auto Refuse',
                       'appeal_id': appeal_id
                       }

            try:
                res = await self.sessions.web.post("https://tieba.baidu.com/mo/q/bawuappealhandle", data=payload)

                main_json = await res.json()
                if int(main_json['no']):
                    raise ValueError(main_json['error'])

            except Exception as err:
                log.warning(
                    f"Failed to handle {appeal_id} in {tieba_name}. reason:{err}")
                return False

            log.info(
                f"Successfully handled {appeal_id} in {tieba_name}. refuse:{refuse}")
            return True

        async def _get_appeal_list() -> int:
            """
            迭代返回申诉请求的编号(appeal_id)
            _get_appeal_list()

            闭包参数:
                tieba_name

            迭代返回值:
                appeal_id: int 申诉请求的编号
            """

            params = {'fn': tieba_name,
                      'fid': await self.get_fid(tieba_name)
                      }

            try:
                while 1:
                    res = await self.sessions.web.get("https://tieba.baidu.com/mo/q/bawuappeal", params=params)

                    soup = BeautifulSoup(await res.text(), 'lxml')

                    items = soup.find_all(
                        'li', class_='appeal_list_item j_appeal_list_item')
                    if not items:
                        return
                    for item in items:
                        appeal_id = int(
                            re.search('aid=(\d+)', item.a['href']).group(1))
                        yield appeal_id

            except Exception as err:
                log.warning(
                    f"Failed to get appeal_list of {tieba_name}. reason:{err}")
                return

        async for appeal_id in _get_appeal_list():
            await _appeal_handle(appeal_id)

    async def url2image(self, img_url: str) -> Optional[np.ndarray]:
        """
        从链接获取静态图像。若为gif则仅读取第一帧即透明通道帧
        url2image(img_url)

        返回值:
            image: numpy.array | None 图像
        """

        try:
            res = await self.sessions.web.get(img_url)

            content = await res.content.read()
            if not content:
                raise ValueError("empty response")

            pil_image = Image.open(BytesIO(content))
            image = cv.cvtColor(np.asarray(pil_image), cv.COLOR_RGB2BGR)

        except Exception as err:
            log.warning(f"Failed to get image {img_url}. reason:{err}")
            image = None

        return image

    async def get_self_info(self) -> BasicUserInfo:
        """
        获取本账号信息
        get_self_info()

        返回值:
            user: BasicUserInfo 简略版用户信息，仅保证包含portrait、user_id和user_name
        """

        payload = {'_client_version': '12.22.1.0',
                   'bdusstoken': self.sessions.BDUSS,
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/s/login", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            user_dict = main_json['user']
            user_proto = ParseDict(
                user_dict, User_pb2.User(), ignore_unknown_fields=True)
            user = BasicUserInfo(user_proto=user_proto)

            self._tbs = main_json['anti']['tbs']

        except Exception as err:
            log.warning(f"Failed to get UserInfo. reason:{err}")
            user = BasicUserInfo()
            self._tbs = ''

        return user

    async def get_newmsg(self) -> dict[str, bool]:
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
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/s/msg", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            msg = {key: bool(int(value))
                   for key, value in main_json['message'].items()}

        except Exception as err:
            log.warning(f"Failed to get msg reason:{err}")
            msg = {'fans': False,
                   'replyme': False,
                   'atme': False,
                   'agree': False,
                   'pletter': False,
                   'bookmark': False,
                   'count': False}

        return msg

    async def get_ats(self) -> list[At]:
        """
        获取@信息
        get_ats()

        返回值:
            Ats: at列表
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   '_client_version': '12.22.1.0'
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/u/feed/atme", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            ats = Ats(main_json)

        except Exception as err:
            log.warning(f"Failed to get ats reason:{err}")
            ats = Ats()

        return ats

    async def get_homepage(self, portrait: str) -> Tuple[UserInfo, list[Thread]]:
        """
        获取用户主页
        get_homepage(portrait)

        参数:
            portrait: str 用户portrait

        返回值:
            user: UserInfo 用户信息
            threads: List[Thread] 帖子列表
        """

        payload = {'_client_type': 2,  # 删除该字段会导致post_list为空
                   '_client_version': '12.22.1.0',  # 删除该字段会导致post_list和dynamic_list为空
                   'friend_uid_portrait': portrait,
                   'need_post_count': 1,  # 删除该字段会导致无法获取发帖回帖数量
                   # 'uid':user_id  # 用该字段检查共同关注的吧
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/u/user/profile", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if not main_json.__contains__('user'):
                raise ValueError("invalid params")

        except Exception as err:
            log.warning(
                f"Failed to get profile of {portrait}. reason:{err}")
            return UserInfo(), []

        user_dict = main_json['user']
        user = UserInfo()
        user.user_name = user_dict['name']
        user.nick_name = user_dict['name_show']
        user.portrait = user_dict['portrait']
        user.user_id = user_dict['id']
        user.gender = user_dict['sex']
        user.is_vip = int(user_dict['vipInfo']['v_status']) != 0
        user.is_god = bool(user_dict['new_god_data']['field_id'])
        priv_dict = user_dict['priv_sets']
        if not priv_dict:
            priv_dict = {}
        user.priv_like = priv_dict.get('like', None)
        user.priv_reply = priv_dict.get('reply', None)

        def _contents(content_dicts: list[dict]):
            for content_dict in content_dicts:
                yield ParseDict(content_dict, PbContent_pb2.PbContent(), ignore_unknown_fields=True)

        def _init_thread(thread_dict: dict):
            thread = Thread()
            thread.contents = Fragments(
                _contents(thread_dict.get('first_post_content', [])))
            thread.fid = int(thread_dict['forum_id'])
            thread.tid = int(thread_dict['thread_id'])
            thread.pid = int(thread_dict['post_id'])
            thread.user = user
            thread.author_id = int(thread_dict['user_id'])

            thread.title = thread_dict['title']
            thread.view_num = int(thread_dict['freq_num'])
            thread.reply_num = int(thread_dict['reply_num'])
            thread.agree = int(thread_dict['agree']['agree_num'])
            thread.disagree = int(thread_dict['agree']['disagree_num'])
            thread.create_time = int(thread_dict['create_time'])
            return thread

        threads = [_init_thread(thread_dict)
                   for thread_dict in main_json['post_list']]

        return user, threads

    async def get_self_forum_list(self) -> Tuple[str, int, int, int]:
        """
        获取本人关注贴吧列表
        get_self_forum_list()

        迭代返回值:
            tieba_name: str 贴吧名
            fid: int 贴吧id
            level: int 等级
            exp: int 经验值
        """

        user = await self.get_self_info()

        def _parse_forum_info(forum_dict: dict[str, str]) -> Tuple[str, int, int, int]:
            """
            解析关注贴吧的信息
            _parse_forum_info(forum_dict)

            参数:
                forum_dict: dict 关注贴吧信息

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

        async def _get_pn_forum_list(pn: int):
            """
            获取pn页的关注贴吧信息
            _get_pn_forum_list(pn)

            参数:
                pn: int 页数

            闭包参数:
                user

            迭代返回值:
                tieba_name: str 贴吧名
                fid: int 贴吧id
                level: int 等级
                exp: int 经验值
            """

            payload = {'BDUSS': self.sessions.BDUSS,
                       '_client_version': '12.22.1.0',  # 删除该字段可直接获取前200个吧，但无法翻页
                       'friend_uid': user.user_id,
                       'page_no': pn  # 加入client_version后，使用该字段控制页数
                       }
            payload['sign'] = self._app_sign(payload)

            try:
                res = await self.sessions.app.post("http://c.tieba.baidu.com/c/f/forum/like", data=payload)

                main_json = await res.json(content_type='application/x-javascript')
                if int(main_json['error_code']):
                    raise ValueError(main_json['error_msg'])

                forum_list = main_json.get('forum_list', None)
                if not forum_list:
                    return

            except Exception as err:
                log.warning(
                    f"Failed to get forumlist of {user.user_id}. reason:{err}")
                raise StopAsyncIteration

            nonofficial_forums = forum_list.get('non-gconforum', [])
            official_forums = forum_list.get('gconforum', [])

            for forum_dict in nonofficial_forums:
                yield _parse_forum_info(forum_dict)
            for forum_dict in official_forums:
                yield _parse_forum_info(forum_dict)

            if len(nonofficial_forums)+len(official_forums) != 50:
                raise StopAsyncIteration

        for pn in range(1, sys.maxsize):
            try:
                async for _ in _get_pn_forum_list(pn):
                    yield _
            except RuntimeError:
                return

    async def get_forum_list(self, user_id: int) -> Tuple[str, int, int, int]:
        """
        获取用户关注贴吧列表
        get_forum_list(user_id)

        参数:
            user_id: int 用户user_id

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
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/f/forum/like", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            for forum in main_json.get('forum_list', []):
                fid = int(forum['id'])
                tieba_name = forum['name']
                level = int(forum['level_id'])
                exp = int(forum['cur_score'])
                yield tieba_name, fid, level, exp

        except Exception as err:
            log.warning(f"Failed to get forumlist of {user_id}. reason:{err}")
            return

    async def get_bawu_dict(self, tieba_name: str) -> dict[str, list[BasicUserInfo]]:
        """
        获取吧务信息
        get_bawu_dict(tieba_name)

        参数:
            tieba_name: str 贴吧名

        返回值:
            bawu_dict: dict[str,list[BasicUserInfo]] {吧务类型:吧务信息列表}
        """

        common = CommonReq_pb2.CommonReq()
        common._client_version = '12.22.1.0'
        data = GetBawuInfoReqIdl_pb2.GetBawuInfoReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.forum_id = await self.get_fid(tieba_name)
        bawuinfo_req = GetBawuInfoReqIdl_pb2.GetBawuInfoReqIdl()
        bawuinfo_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(
            bawuinfo_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/f/forum/getBawuInfo", params={'cmd': 301007}, data=multipart_writer)

            main_proto = GetBawuInfoResIdl_pb2.GetBawuInfoResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            def _parse_roleinfo(roleinfo_proto):

                user = BasicUserInfo()
                user.user_name = roleinfo_proto.user_name
                user.nick_name = roleinfo_proto.name_show
                user.portrait = roleinfo_proto.portrait
                user.user_id = roleinfo_proto.user_id

                return user

            roledes_protos = main_proto.data.bawu_team_info.bawu_team_list
            bawu_dict = {roledes_proto.role_name: [_parse_roleinfo(
                roleinfo_proto) for roleinfo_proto in roledes_proto.role_info] for roledes_proto in roledes_protos}

        except Exception as err:
            log.warning(f"Failed to get adminlist reason: {err}")
            bawu_dict = {}

        return bawu_dict

    async def get_tab_map(self, tieba_name: str) -> Dict[str, int]:
        """
        get_tab_map()
        获取分区名到分区id的映射字典

        参数:
            tieba_name: str 贴吧名

        返回值:
            tab_map: Dict[str, int] 分区名:分区id
        """

        common = CommonReq_pb2.CommonReq()
        common.BDUSS = self.sessions.BDUSS
        common._client_version = '12.22.1.0'
        data = SearchPostForumReqIdl_pb2.SearchPostForumReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.word = tieba_name
        searchforum_req = SearchPostForumReqIdl_pb2.SearchPostForumReqIdl()
        searchforum_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(
            searchforum_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/f/forum/searchPostForum", params={'cmd': 309466}, data=multipart_writer)

            main_proto = SearchPostForumResIdl_pb2.SearchPostForumResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            tab_map = {
                tab_proto.tab_name: tab_proto.tab_id for tab_proto in main_proto.data.exact_match.tab_info}

        except Exception as err:
            log.warning(
                f"Failed to get tab_map of {tieba_name}. reason:{err}")
            tab_map = {}

        return tab_map

    async def get_recom_list(self, tieba_name: str):
        """
        获取大吧主推荐帖列表
        get_recom_list(tieba_name)

        参数:
            tieba_name: str 贴吧名

        迭代返回值:
            thread: Thread 被推荐帖子信息
            add_view: int 新增浏览量
        """

        async def _get_pn_recom_list(pn: int):
            """
            获取pn页的大吧主推荐帖列表
            _get_pn_recom_list(pn)

            参数:
                pn: int 页数

            闭包参数:
                tieba_name

            迭代返回值:
                thread: Thread 被推荐帖子信息
                add_view: int 新增浏览量
            """

            payload = {'BDUSS': self.sessions.BDUSS,
                       '_client_version': '12.22.1.0',
                       'forum_id': await self.get_fid(tieba_name),
                       'pn': pn,
                       'rn': 30,
                       }
            payload['sign'] = self._app_sign(payload)

            try:
                res = await self.sessions.app.post("http://c.tieba.baidu.com/c/f/bawu/getRecomThreadHistory", data=payload)

                main_json = await res.json(content_type='application/x-javascript')
                if int(main_json['error_code']):
                    raise ValueError(main_json['error_msg'])

            except Exception as err:
                log.warning(
                    f"Failed to get recom_list of {tieba_name}. reason:{err}")
                raise StopAsyncIteration

            def _contents(content_dicts: list[dict]):
                for content_dict in content_dicts:
                    yield ParseDict(content_dict, PbContent_pb2.PbContent(), ignore_unknown_fields=True)

            for data_dict in main_json['recom_thread_list']:

                thread_dict = data_dict['thread_list']
                thread = Thread()
                thread.contents = Fragments(
                    _contents(thread_dict.get('first_post_content', [])))
                thread.fid = int(thread_dict['fid'])
                thread.tid = int(thread_dict['id'])
                thread.pid = int(thread_dict['first_post_id'])
                thread.author_id = int(thread_dict['author_id'])
                thread.title = thread_dict['title']
                thread.view_num = int(thread_dict['view_num'])
                thread.reply_num = int(thread_dict['reply_num'])
                thread.agree = int(thread_dict['agree']['agree_num'])
                thread.disagree = int(thread_dict['agree']['disagree_num'])
                thread.create_time = int(thread_dict['create_time'])
                thread.last_time = int(thread_dict['last_time_int'])

                user_dict = thread_dict['author']
                user = UserInfo()
                user.user_name = user_dict['name']
                user.nick_name = user_dict['name_show']
                user.portrait = user_dict['portrait']
                user.user_id = user_dict['id']
                user.gender = user_dict['sex']
                user.is_vip = bool(user_dict['vipInfo'])
                user.is_god = bool(user_dict['new_god_data']['field_id'])
                priv_dict = user_dict['priv_sets']
                if not priv_dict:
                    priv_dict = {}
                user.priv_like = priv_dict.get('like', None)
                user.priv_reply = priv_dict.get('reply', None)
                thread.user = user

                add_view = thread.view_num-int(data_dict['current_pv'])

                yield thread, add_view

            if int(main_json['is_has_more']) == 0:
                raise StopAsyncIteration

        for pn in range(1, sys.maxsize):
            try:
                async for _ in _get_pn_recom_list(pn):
                    yield _
            except RuntimeError:
                return

    async def get_recom_status(self, tieba_name: str):
        """
        获取大吧主推荐功能的月度配额状态
        get_recom_status(tieba_name)

        参数:
            tieba_name: str 贴吧名

        返回值:
            total_recom_num: int 本月总推荐配额
            used_recom_num: int 本月已使用的推荐配额
        """

        payload = {'BDUSS': self.sessions.BDUSS,
                   '_client_version': '12.22.1.0',
                   'forum_id': await self.get_fid(tieba_name),
                   'pn': 1,
                   'rn': 0,
                   }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/f/bawu/getRecomThreadList", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            total_recom_num = int(main_json['total_recommend_num'])
            used_recom_num = int(main_json['used_recommend_num'])

        except Exception as err:
            log.warning(
                f"Failed to get recom_status of {tieba_name}. reason:{err}")
            total_recom_num = 0
            used_recom_num = 0

        return total_recom_num, used_recom_num

    async def get_rank(self, tieba_name: str, level_thre: int = 4) -> Tuple[str, int, int, bool]:
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

        async def _get_pn_rank(pn: int) -> Tuple[str, int, int, bool]:
            """
            获取pn页的排行
            _get_pn_rank(pn)

            参数:
                pn: int 页数

            闭包参数:
                tieba_name

            返回值:
                user_name: str 用户名
                level: int 等级
                exp: int 经验值
                is_vip: bool 是否vip
            """

            try:
                res = await self.sessions.web.get("http://tieba.baidu.com/f/like/furank", params={'kw': tieba_name, 'pn': pn, 'ie': 'utf-8'})

                soup = BeautifulSoup(await res.text(), 'lxml')
                items = soup.select('tr[class^=drl_list_item]')
                if not items:
                    raise StopAsyncIteration

                for item in items:
                    user_name_item = item.td.next_sibling
                    user_name = user_name_item.text
                    is_vip = 'drl_item_vip' in user_name_item.div['class']
                    level_item = user_name_item.next_sibling
                    # e.g. get level 16 from string "bg_lv16" by slicing [5:]
                    level = int(level_item.div['class'][0][5:])
                    if level < level_thre:
                        raise StopAsyncIteration
                    exp_item = level_item.next_sibling
                    exp = int(exp_item.text)

                    yield user_name, level, exp, is_vip

            except StopAsyncIteration:
                raise
            except Exception as err:
                log.warning(
                    f"Failed to get rank of {tieba_name} pn:{pn}. reason:{err}")

        for pn in range(1, sys.maxsize):
            try:
                async for _ in _get_pn_rank(pn):
                    yield _
            except RuntimeError:
                return

    async def get_member(self, tieba_name: str) -> Tuple[str, str, int]:
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

        async def _get_pn_member(pn: int) -> Tuple[str, str, int]:
            """
            获取pn页的最新关注用户列表
            _get_pn_member(pn)

            参数:
                pn: int 页数

            闭包参数:
                tieba_name

            返回值:
                user_name: str 用户名
                portrait: str
                level: int 等级
            """

            try:
                res = await self.sessions.web.get("http://tieba.baidu.com/bawu2/platform/listMemberInfo", params={'word': tieba_name, 'pn': pn, 'ie': 'utf-8'})

                soup = BeautifulSoup(await res.text(), 'lxml')
                items = soup.find_all('div', class_='name_wrap')
                if not items:
                    raise StopAsyncIteration

                for item in items:
                    user_item = item.a
                    user_name = user_item['title']
                    portrait = user_item['href'][14:]
                    level_item = item.span
                    level = int(level_item['class'][1][12:])
                    yield user_name, portrait, level

            except StopAsyncIteration:
                raise
            except Exception as err:
                log.warning(
                    f"Failed to get member of {tieba_name} pn:{pn}. reason:{err}")

        for pn in range(1, 459):
            try:
                async for _ in _get_pn_member(pn):
                    yield _
            except RuntimeError:
                return

    async def like_forum(self, tieba_name: str) -> bool:
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
                       'fid': await self.get_fid(tieba_name),
                       'tbs': await self.get_tbs()
                       }
            payload['sign'] = self._app_sign(payload)

            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/forum/like", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if int(main_json['error']['errno']):
                raise ValueError(main_json['error']['errmsg'])

        except Exception as err:
            log.warning(f"Failed to like forum {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully like forum {tieba_name}")
        return True

    async def sign_forum(self, tieba_name: str) -> bool:
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
                       '_client_version': '12.22.1.0',
                       '_phone_imei': '000000000000000',
                       'c3_aid': 'NULL',
                       'cmode': 1,
                       'cuid': 'NULL',
                       'cuid_galaxy2': 'NULL',
                       'cuid_gid': '',
                       'event_day': '000000',
                       'fid': await self.get_fid(tieba_name),
                       'first_install_time': 0,
                       'kw': tieba_name,
                       'last_update_time': 0,
                       'sign_from': 'frs',
                       'tbs': await self.get_tbs(),
                       }
            payload['sign'] = self._app_sign(payload)

            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/forum/sign", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if int(main_json['user_info']['sign_bonus_point']) == 0:
                raise ValueError("sign_bonus_point is 0")

            cash = main_json['user_info'].__contains__('get_packet_cash')

        except Exception as err:
            log.warning(f"Failed to sign forum {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully sign forum {tieba_name}. cash:{cash}")
        return True

    async def add_post(self, tieba_name: str, tid: int, content: str) -> bool:
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
            fid = await self.get_fid(tieba_name)
            ts = time.time()
            ts_ms = int(ts * 1000)
            ts_struct = time.localtime(ts)
            payload = {'BDUSS': self.sessions.BDUSS,
                       '_client_id': 'wappc_1643725546500_150',
                       '_client_type': 2,
                       '_client_version': '9.1.0.0',
                       '_phone_imei': '000000000000000',
                       'android_id': '31760cd1d096538d',
                       'anonymous': 1,
                       'authsid': 'null',
                       'barrage_time': 0,
                       'brand': 'HUAWEI',
                       'c3_aid': 'A00-WGF47YI5OMGPRPDQI5HFKD4J56B6B5YX-AZRCBBHI',
                       'can_no_forum': 0,
                       'cmode': 1,
                       'content': content,
                       'cuid': '89EC02B413436B80CB1A8873CD56AFFF|V6JXX7UB7',
                       'cuid_galaxy2': '89EC02B413436B80CB1A8873CD56AFFF|V6JXX7UB7',
                       'cuid_gid': '',
                       'entrance_type': 0,
                       'event_day': f'{ts_struct.tm_year}{ts_struct.tm_mon}{ts_struct.tm_mday}',
                       'fid': fid,
                       'from': '1008621x',
                       'from_fourm_id': fid,
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
                       'stoken': self.sessions.STOKEN,
                       'subapp_type': 'mini',
                       'takephoto_num': 0,
                       'tbs': await self.get_tbs(),
                       'tid': tid,
                       'timestamp': ts_ms,
                       'v_fid': '',
                       'v_fname': '',
                       'vcode_tag': 12,
                       'z_id': ''
                       }
            payload['sign'] = self._app_sign(payload)

            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/post/add", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if int(main_json['info']['need_vcode']):
                raise ValueError(f"need verify code")

        except Exception as err:
            log.warning(f"Failed to add post in {tid}. reason:{err}")
            return False

        log.info(f"Successfully add post in {tid}")
        return True

    async def set_privacy(self, tid: int, hide: bool = True) -> bool:
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
            log.warning(f"Failed to set privacy to {tid}")
            return False

        try:
            payload = {'BDUSS': self.sessions.BDUSS,
                       'forum_id': posts[0].fid,
                       'is_hide': int(hide),
                       'post_id': posts[0].pid,
                       'thread_id': tid
                       }
            payload['sign'] = self._app_sign(payload)

            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/thread/setPrivacy", data=payload)

            main_json = await res.json(content_type='application/x-javascript')
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(f"Failed to set privacy to {tid}. reason:{err}")
            return False

        log.info(f"Successfully set privacy to {tid}. is_hide:{hide}")
        return True
