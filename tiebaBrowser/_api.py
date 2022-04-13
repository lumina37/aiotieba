# -*- coding:utf-8 -*-
__all__ = ['Browser']

import asyncio
import hashlib
import json
import socket
import sys
import time
from collections.abc import AsyncIterable
from io import BytesIO
from typing import Optional, Union

import aiohttp
import cv2 as cv
import numpy as np
from bs4 import BeautifulSoup
from google.protobuf.json_format import ParseDict
from PIL import Image

from tiebaBrowser.tieba_proto import ThreadInfo_pb2

from ._config import config
from ._logger import log
from ._types import (JSON_DECODER, Ats, BasicUserInfo, Comments, Posts, Replys, Searches, Thread, Threads, UserInfo)
from .tieba_proto import (CommonReq_pb2, FrsPageReqIdl_pb2, FrsPageResIdl_pb2, GetBawuInfoReqIdl_pb2,
                          GetBawuInfoResIdl_pb2, GetUserByTiebaUidReqIdl_pb2, GetUserByTiebaUidResIdl_pb2,
                          GetUserInfoReqIdl_pb2, GetUserInfoResIdl_pb2, PbFloorReqIdl_pb2, PbFloorResIdl_pb2,
                          PbPageReqIdl_pb2, PbPageResIdl_pb2, ReplyMeReqIdl_pb2, ReplyMeResIdl_pb2,
                          SearchPostForumReqIdl_pb2, SearchPostForumResIdl_pb2, User_pb2)


class Sessions(object):
    """
    保持会话

    Args:
        BDUSS_key (str, optional): 用于从config.json中提取BDUSS. Defaults to None.
    """

    __slots__ = ['_timeout', '_connector', 'app', 'app_proto', 'web', 'BDUSS', 'STOKEN']

    def __init__(self, BDUSS_key: Optional[str] = None) -> None:

        if BDUSS_key:
            self.BDUSS = config['BDUSS'][BDUSS_key]
            self.STOKEN = config['STOKEN'].get(BDUSS_key, '')
        else:
            self.BDUSS = ''
            self.STOKEN = ''

        self._timeout = aiohttp.ClientTimeout(connect=5, sock_connect=3, sock_read=10)
        self._connector = aiohttp.TCPConnector(ttl_dns_cache=600,
                                               keepalive_timeout=90,
                                               limit=0,
                                               family=socket.AF_INET,
                                               ssl=False)
        _read_bufsize = 1 << 17  # 128KiB
        _trust_env = False

        # Init app client
        app_headers = {
            aiohttp.hdrs.USER_AGENT: 'bdtb for Android 12.23.1.0',
            aiohttp.hdrs.CONNECTION: 'keep-alive',
            aiohttp.hdrs.ACCEPT_ENCODING: 'gzip',
            aiohttp.hdrs.HOST: 'c.tieba.baidu.com',
        }
        self.app = aiohttp.ClientSession(connector=self._connector,
                                         headers=app_headers,
                                         version=aiohttp.HttpVersion11,
                                         cookie_jar=aiohttp.CookieJar(),
                                         connector_owner=False,
                                         raise_for_status=True,
                                         timeout=self._timeout,
                                         read_bufsize=_read_bufsize,
                                         trust_env=_trust_env)

        # Init app protobuf client
        app_proto_headers = {
            aiohttp.hdrs.USER_AGENT: 'bdtb for Android 12.23.1.0',
            'x_bd_data_type': 'protobuf',
            aiohttp.hdrs.CONNECTION: 'keep-alive',
            aiohttp.hdrs.ACCEPT_ENCODING: 'gzip',
            aiohttp.hdrs.HOST: 'c.tieba.baidu.com',
        }
        self.app_proto = aiohttp.ClientSession(connector=self._connector,
                                               headers=app_proto_headers,
                                               version=aiohttp.HttpVersion11,
                                               cookie_jar=aiohttp.CookieJar(),
                                               connector_owner=False,
                                               raise_for_status=True,
                                               timeout=self._timeout,
                                               read_bufsize=_read_bufsize,
                                               trust_env=_trust_env)

        # Init web client
        web_headers = {
            aiohttp.hdrs.USER_AGENT: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
            aiohttp.hdrs.ACCEPT_ENCODING: 'gzip, deflate, br',
            aiohttp.hdrs.CACHE_CONTROL: 'no-cache',
            aiohttp.hdrs.CONNECTION: 'keep-alive',
        }
        web_cookie_jar = aiohttp.CookieJar()
        web_cookie_jar.update_cookies({'BDUSS': self.BDUSS, 'STOKEN': self.STOKEN})
        self.web = aiohttp.ClientSession(connector=self._connector,
                                         headers=web_headers,
                                         version=aiohttp.HttpVersion11,
                                         cookie_jar=web_cookie_jar,
                                         connector_owner=False,
                                         raise_for_status=True,
                                         timeout=self._timeout,
                                         read_bufsize=_read_bufsize,
                                         trust_env=_trust_env)

    async def close(self) -> None:
        await asyncio.gather(self.app.close(),
                             self.app_proto.close(),
                             self.web.close(),
                             self._connector.close(),
                             return_exceptions=True)

    async def __aenter__(self) -> "Sessions":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


class Browser(object):
    """
    贴吧浏览、参数获取等API的封装

    Args:
        BDUSS_key (str, optional): 用于从config.json中提取BDUSS. Defaults to None.
    """

    __slots__ = ['BDUSS_key', 'sessions', '_tbs']

    fid_dict: dict[str, int] = {}

    def __init__(self, BDUSS_key: Optional[str] = None) -> None:
        self.BDUSS_key = BDUSS_key
        self.sessions = Sessions(BDUSS_key)
        self._tbs: str = ''

    async def close(self) -> None:
        await self.sessions.close()

    async def __aenter__(self) -> "Browser":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @staticmethod
    def _app_sign(payload: dict) -> str:
        """
        计算form参数字典的贴吧客户端签名值sign

        Args:
            payload (dict): form参数字典

        Returns:
            str: 贴吧客户端签名值sign
        """

        raw_list = [f"{key}={value}" for key, value in payload.items() if key != 'sign']
        raw_list.append("tiebaclient!!!")
        raw_str = "".join(raw_list)

        md5 = hashlib.md5()
        md5.update(raw_str.encode('utf-8'))
        sign = md5.hexdigest().upper()

        return sign

    @staticmethod
    def get_tieba_multipart_writer(proto_bytes: bytes) -> aiohttp.MultipartWriter:
        """
        将proto_bytes封装为贴吧客户端专用的aiohttp.MultipartWriter

        Args:
            proto_bytes (bytes): protobuf序列化后的二进制数据

        Returns:
            aiohttp.MultipartWriter: 只可用于贴吧客户端
        """

        writer = aiohttp.MultipartWriter('form-data', boundary="*--asoul-diana-bili-uid672328094")
        payload_headers = {
            aiohttp.hdrs.CONTENT_DISPOSITION:
            aiohttp.helpers.content_disposition_header('form-data', name='data', filename='file')
        }
        payload = aiohttp.BytesPayload(proto_bytes, content_type='', headers=payload_headers)
        writer.append_payload(payload)

        # 删除无用参数
        writer._parts[0][0]._headers.popone(aiohttp.hdrs.CONTENT_TYPE)
        writer._parts[0][0]._headers.popone(aiohttp.hdrs.CONTENT_LENGTH)

        return writer

    async def get_tbs(self) -> str:
        """
        获取贴吧反csrf校验码tbs

        Returns:
            str: 贴吧反csrf校验码tbs
        """

        if not self._tbs:
            await self.get_self_info()

        return self._tbs

    async def get_fid(self, tieba_name: str) -> int:
        """
        通过贴吧名获取forum_id

        Args:
            tieba_name (str): 贴吧名

        Returns:
            int: 该贴吧的forum_id
        """

        if fid := self.fid_dict.get(tieba_name, 0):
            return fid

        try:
            res = await self.sessions.web.get("http://tieba.baidu.com/f/commit/share/fnameShareApi",
                                              params={
                                                  'fname': tieba_name,
                                                  'ie': 'utf-8'
                                              })

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['no']):
                raise ValueError(main_json['error'])

            fid = int(main_json['data']['fid'])

        except Exception as err:
            log.warning(f"Failed to get fid of {tieba_name}. reason:{err}")
            fid = 0

        if fid:
            self.fid_dict[tieba_name] = fid

        return fid

    async def get_user_info(self, _id: Union[str, int]) -> UserInfo:
        """
        补全完整版用户信息

        Args:
            _id (Union[str, int]): 用户id user_name或portrait或user_id

        Returns:
            UserInfo: 完整版用户信息
        """

        user = UserInfo(_id)
        if user.user_id:
            return await self._user_id2user_info(user)
        else:
            return await self._id2user_info(user)

    async def get_basic_user_info(self, _id: Union[str, int]) -> BasicUserInfo:
        """
        补全简略版用户信息

        Args:
            _id (Union[str, int]): 用户id user_id/user_name/portrait

        Returns:
            BasicUserInfo: 简略版用户信息 仅保证包含user_name/portrait/user_id
        """

        user = BasicUserInfo(_id)
        if user.user_id:
            return await self._user_id2basic_user_info(user)
        elif user.user_name:
            return await self._user_name2basic_user_info(user)
        else:
            return await self._id2basic_user_info(user)

    async def _id2user_info(self, user: UserInfo) -> UserInfo:
        """
        通过用户名或昵称或portrait补全完整版用户信息

        Args:
            user (UserInfo): 待补全的用户信息

        Returns:
            UserInfo: 完整版用户信息
        """

        try:
            res = await self.sessions.web.get("https://tieba.baidu.com/home/get/panel",
                                              params={
                                                  'id': user.portrait,
                                                  'un': user.user_name or user.nick_name
                                              })

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['no']):
                raise ValueError(main_json['error'])

            user_dict: dict = main_json['data']
            sex: str = user_dict['sex']
            if sex.startswith('m'):
                gender = 1
            elif sex.startswith('f'):
                gender = 2
            else:
                gender = 0

            user.user_name = user_dict['name']
            user.nick_name = user_dict['show_nickname']
            user.portrait = user_dict['portrait']
            user.user_id = user_dict['id']
            user.gender = gender
            user.is_vip = int(vip_dict['v_status']) if (vip_dict := user_dict['vipInfo']) else False

        except Exception as err:
            log.warning(f"Failed to get UserInfo of {user.log_name}. reason:{err}")
            user = UserInfo()

        return user

    async def _id2basic_user_info(self, user: BasicUserInfo) -> BasicUserInfo:
        """
        通过用户名或昵称或portrait补全简略版用户信息

        Args:
            user (BasicUserInfo): 待补全的用户信息

        Returns:
            BasicUserInfo: 简略版用户信息 仅保证包含user_name/portrait/user_id
        """

        try:
            res = await self.sessions.web.get("https://tieba.baidu.com/home/get/panel",
                                              params={
                                                  'id': user.portrait,
                                                  'un': user.user_name or user.nick_name
                                              })

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['no']):
                raise ValueError(main_json['error'])

            user_dict = main_json['data']
            user.user_name = user_dict['name']
            user.nick_name = user_dict['show_nickname']
            user.portrait = user_dict['portrait']
            user.user_id = user_dict['id']

        except Exception as err:
            log.warning(f"Failed to get BasicUserInfo of {user.log_name}. reason:{err}")
            user = UserInfo()

        return user

    async def _user_name2basic_user_info(self, user: BasicUserInfo) -> BasicUserInfo:
        """
        通过用户名补全简略版用户信息

        Args:
            user (BasicUserInfo): 待补全的用户信息

        Returns:
            BasicUserInfo: 简略版用户信息 仅保证包含user_name/portrait/user_id
        """

        params = {'un': user.user_name, 'ie': 'utf-8'}

        try:
            res = await self.sessions.web.get("http://tieba.baidu.com/i/sys/user_json", params=params)

            text = await res.text(encoding='utf-8', errors='ignore')
            main_json = json.loads(text)
            if not main_json:
                raise ValueError("empty response")

            user_dict = main_json['creator']
            user.user_id = user_dict['id']
            user.portrait = user_dict['portrait']

        except Exception as err:
            log.warning(f"Failed to get BasicUserInfo of {user.user_name}. reason:{err}")
            user = BasicUserInfo()

        return user

    async def _user_id2user_info(self, user: UserInfo) -> UserInfo:
        """
        通过user_id补全用户信息

        Args:
            user (UserInfo): 待补全的用户信息

        Returns:
            UserInfo: 完整版用户信息
        """

        common = CommonReq_pb2.CommonReq()
        data = GetUserInfoReqIdl_pb2.GetUserInfoReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.uid = user.user_id
        userinfo_req = GetUserInfoReqIdl_pb2.GetUserInfoReqIdl()
        userinfo_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(userinfo_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/u/user/getuserinfo",
                                                     params={'cmd': 303024},
                                                     data=multipart_writer)

            main_proto = GetUserInfoResIdl_pb2.GetUserInfoResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            user_proto = main_proto.data.user
            user = UserInfo(user_proto=user_proto)

        except Exception as err:
            log.warning(f"Failed to get UserInfo of {user.user_id}. reason:{err}")
            user = UserInfo()

        return user

    async def _user_id2basic_user_info(self, user: BasicUserInfo) -> BasicUserInfo:
        """
        通过user_id补全简略版用户信息

        Args:
            user (BasicUserInfo): 待补全的用户信息

        Returns:
            BasicUserInfo: 简略版用户信息 仅保证包含user_name/portrait/user_id
        """

        try:
            res = await self.sessions.web.get("http://tieba.baidu.com/im/pcmsg/query/getUserInfo",
                                              params={'chatUid': user.user_id})

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['errno']):
                raise ValueError(main_json['errmsg'])

            user_dict = main_json['chatUser']
            user.user_name = user_dict['uname']
            user.portrait = user_dict['portrait']

        except Exception as err:
            log.warning(f"Failed to get BasicUserInfo of {user.user_id}. reason:{err}")
            user = BasicUserInfo()

        return user

    async def get_threads(self, tieba_name: str, pn: int = 1, sort: int = 5, is_good: bool = False) -> Threads:
        """
        获取首页帖子

        Args:
            tieba_name (str): 贴吧名
            pn (int, optional): 页码. Defaults to 1.
            sort (int, optional): 排序方式 对于有热门分区的贴吧0是热门排序1是按发布时间2报错34都是热门排序>=5是按回复时间
                对于无热门分区的贴吧0是按回复时间1是按发布时间2报错>=3是按回复时间. Defaults to 5.
            is_good (bool, optional): True为获取精品区帖子 False为获取普通区帖子. Defaults to False.

        Returns:
            Threads: 帖子列表
        """

        common = CommonReq_pb2.CommonReq()
        common._client_version = '12.23.1.0'
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

        multipart_writer = self.get_tieba_multipart_writer(frspage_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/f/frs/page",
                                                     params={'cmd': 301001},
                                                     data=multipart_writer)

            main_proto = FrsPageResIdl_pb2.FrsPageResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            threads = Threads(main_proto)

        except Exception as err:
            log.warning(f"Failed to get threads of {tieba_name}. reason:{err}")
            threads = Threads()

        return threads

    async def get_posts(self,
                        tid: int,
                        pn: int = 1,
                        rn: int = 30,
                        sort: int = 0,
                        only_thread_author: bool = False,
                        with_comments: bool = False,
                        comment_sort_by_agree: bool = True,
                        comment_rn: int = 10) -> Posts:
        """
        获取主题帖内回复

        Args:
            tid (int): 所在主题帖tid
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30.
            sort (int, optional): 0则按时间顺序请求 1则按时间倒序请求 2则按热门序请求. Defaults to 0.
            only_thread_author (bool, optional): True则只看楼主 False则请求全部. Defaults to False.
            with_comments (bool, optional): True则同时请求高赞楼中楼 False则返回的Posts.comments为空. Defaults to False.
            comment_sort_by_agree (bool, optional): True则楼中楼按点赞数顺序 False则楼中楼按时间顺序. Defaults to True.
            comment_rn (int, optional): 请求的楼中楼数量. Defaults to 10.

        Returns:
            Posts: 回复列表
        """

        common = CommonReq_pb2.CommonReq()
        common._client_version = '12.23.1.0'
        data = PbPageReqIdl_pb2.PbPageReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.kz = tid
        data.pn = pn
        data.rn = rn
        data.q_type = 2
        data.r = sort
        data.lz = only_thread_author
        if with_comments:
            data.with_floor = with_comments
            data.floor_sort_type = comment_sort_by_agree
            data.floor_rn = comment_rn
        pbpage_req = PbPageReqIdl_pb2.PbPageReqIdl()
        pbpage_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(pbpage_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/f/pb/page",
                                                     params={'cmd': 302001},
                                                     data=multipart_writer)

            main_proto = PbPageResIdl_pb2.PbPageResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            posts = Posts(main_proto)

        except Exception as err:
            log.warning(f"Failed to get posts of {tid}. reason:{err}")
            posts = Posts()

        return posts

    async def get_comments(self, tid: int, pid: int, pn: int = 1, is_floor: bool = False) -> Comments:
        """
        获取楼中楼回复

        Args:
            tid (int): 所在主题帖tid
            pid (int): 所在回复pid或楼中楼pid
            pn (int, optional): 页码. Defaults to 1.
            is_floor (bool, optional): pid是否指向楼中楼. Defaults to False.

        Returns:
            Comments: 楼中楼列表
        """

        common = CommonReq_pb2.CommonReq()
        common._client_version = '12.23.1.0'
        data = PbFloorReqIdl_pb2.PbFloorReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.kz = tid
        if is_floor:
            data.spid = pid
        else:
            data.pid = pid
        data.pn = pn
        pbfloor_req = PbFloorReqIdl_pb2.PbFloorReqIdl()
        pbfloor_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(pbfloor_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/f/pb/floor",
                                                     params={'cmd': 302002},
                                                     data=multipart_writer)

            main_proto = PbFloorResIdl_pb2.PbFloorResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            comments = Comments(main_proto)

        except Exception as err:
            log.warning(f"Failed to get comments of {pid} in {tid}. reason:{err}")
            comments = Comments()

        return comments

    async def block(self, tieba_name: str, user: BasicUserInfo, day: int, reason: str = '') -> bool:
        """
        封禁用户 支持小吧主/语音小编封3/10天

        Args:
            tieba_name (str): 贴吧名
            user (BasicUserInfo): 待封禁用户信息
            day (int): 封禁天数
            reason (str, optional): 封禁理由. Defaults to ''.

        Returns:
            bool: 操作是否成功
        """

        payload = {
            'BDUSS': self.sessions.BDUSS,
            'day': day,
            'fid': await self.get_fid(tieba_name),
            'nick_name': user.show_name,
            'ntn': 'banid',
            'portrait': user.portrait,
            'reason': reason,
            'tbs': await self.get_tbs(),
            'un': user.user_name,
            'word': tieba_name,
            'z': 672328094,
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/commitprison", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(f"Failed to block {user.log_name} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully blocked {user.log_name} in {tieba_name} for {payload['day']} days")
        return True

    async def unblock(self, tieba_name: str, user: BasicUserInfo) -> bool:
        """
        解封用户

        Args:
            tieba_name (str): 贴吧名
            user (BasicUserInfo): 基本用户信息

        Returns:
            bool: 操作是否成功
        """

        payload = {
            'fn': tieba_name,
            'fid': await self.get_fid(tieba_name),
            'block_un': user.user_name,
            'block_uid': user.user_id,
            'block_nickname': user.nick_name,
            'tbs': await self.get_tbs()
        }

        try:
            res = await self.sessions.web.post("https://tieba.baidu.com/mo/q/bawublockclear", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['no']):
                raise ValueError(main_json['error'])

        except Exception as err:
            log.warning(f"Failed to unblock {user.log_name} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully unblocked {user.log_name} in {tieba_name}")
        return True

    async def hide_thread(self, tieba_name: str, tid: int) -> bool:
        """
        屏蔽主题帖

        Args:
            tieba_name (str): 帖子所在的贴吧名
            tid (int): 待屏蔽的主题帖tid

        Returns:
            bool: 操作是否成功
        """

        return await self._del_thread(tieba_name, tid, is_hide=True)

    async def del_thread(self, tieba_name: str, tid: int) -> bool:
        """
        删除主题帖

        Args:
            tieba_name (str): 帖子所在的贴吧名
            tid (int): 待删除的主题帖tid

        Returns:
            bool: 操作是否成功
        """

        return await self._del_thread(tieba_name, tid, is_hide=False)

    async def _del_thread(self, tieba_name: str, tid: int, is_hide: bool = False) -> bool:
        """
        删除/屏蔽主题帖

        Args:
            tieba_name (str): 帖子所在的贴吧名
            tid (int): 待删除/屏蔽的主题帖tid
            is_hide (bool, optional): True则屏蔽帖 False则删除帖. Defaults to False.

        Returns:
            bool: 操作是否成功
        """

        payload = {
            'BDUSS': self.sessions.BDUSS,
            'fid': await self.get_fid(tieba_name),
            'is_frs_mask': int(is_hide),
            'tbs': await self.get_tbs(),
            'z': tid
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/delthread", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(f"Failed to delete thread {tid} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully deleted thread {tid} hide:{is_hide} in {tieba_name}")
        return True

    async def del_post(self, tieba_name: str, tid: int, pid: int) -> bool:
        """
        删除回复

        Args:
            tieba_name (str): 帖子所在的贴吧名
            tid (int): 回复所在的主题帖tid
            pid (int): 待删除的回复pid

        Returns:
            bool: 操作是否成功
        """

        payload = {
            'BDUSS': self.sessions.BDUSS,
            'fid': await self.get_fid(tieba_name),
            'pid': pid,
            'tbs': await self.get_tbs(),
            'z': tid
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/delpost", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(f"Failed to delete post {pid} in {tid} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully deleted post {pid} in {tid} in {tieba_name}")
        return True

    async def unhide_thread(self, tieba_name, tid: int) -> bool:
        """
        解除主题帖屏蔽

        Args:
            tieba_name (str): 帖子所在的贴吧名
            tid (int, optional): 待解除屏蔽的主题帖tid

        Returns:
            bool: 操作是否成功
        """

        return await self._recover(tieba_name, tid=tid, is_hide=True)

    async def recover_thread(self, tieba_name, tid: int) -> bool:
        """
        恢复主题帖

        Args:
            tieba_name (str): 帖子所在的贴吧名
            tid (int, optional): 待恢复的主题帖tid

        Returns:
            bool: 操作是否成功
        """

        return await self._recover(tieba_name, tid=tid, is_hide=False)

    async def recover_post(self, tieba_name, pid: int) -> bool:
        """
        恢复主题帖

        Args:
            tieba_name (str): 帖子所在的贴吧名
            pid (int, optional): 待恢复的回复pid

        Returns:
            bool: 操作是否成功
        """

        return await self._recover(tieba_name, pid=pid, is_hide=False)

    async def _recover(self, tieba_name, tid: int = 0, pid: int = 0, is_hide: bool = False) -> bool:
        """
        恢复帖子

        Args:
            tieba_name (str): 帖子所在的贴吧名
            tid (int, optional): 待恢复的主题帖tid. Defaults to 0.
            pid (int, optional): 待恢复的回复pid. Defaults to 0.
            is_hide (bool, optional): True则取消屏蔽主题帖 False则恢复删帖. Defaults to False.

        Returns:
            bool: 操作是否成功
        """

        payload = {
            'fn': tieba_name,
            'fid': await self.get_fid(tieba_name),
            'tid_list[]': tid,
            'pid_list[]': pid,
            'type_list[]': 1 if pid else 0,
            'is_frs_mask_list[]': int(is_hide)
        }

        try:
            res = await self.sessions.web.post("https://tieba.baidu.com/mo/q/bawurecoverthread", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['no']):
                raise ValueError(main_json['error'])

        except Exception as err:
            log.warning(f"Failed to recover tid:{tid} pid:{pid} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully recovered tid:{tid} pid:{pid} hide:{is_hide} in {tieba_name}")
        return True

    async def move(self, tieba_name: str, tid: int, to_tab_id: int, from_tab_id: int = 0) -> bool:
        """
        将主题帖移动至另一分区

        Args:
            tieba_name (str): 帖子所在贴吧名
            tid (int): 待移动的主题帖tid
            to_tab_id (int): 目标分区id
            from_tab_id (int, optional): 来源分区id 默认为0即无分区. Defaults to 0.

        Returns:
            bool: 操作是否成功
        """

        payload = {
            'BDUSS': self.sessions.BDUSS,
            '_client_version': '12.23.1.0',
            'forum_id': await self.get_fid(tieba_name),
            'tbs': await self.get_tbs(),
            'threads': str([{
                'thread_id': tid,
                'from_tab_id': from_tab_id,
                'to_tab_id': to_tab_id
            }]).replace('\'', '"'),
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/moveTabThread", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(f"Failed to add {tid} to tab:{to_tab_id} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully add {tid} to tab:{to_tab_id} in {tieba_name}")
        return True

    async def recommend(self, tieba_name: str, tid: int) -> bool:
        """
        大吧主首页推荐

        Args:
            tieba_name (str): 帖子所在贴吧名
            tid (int): 待推荐的主题帖tid

        Returns:
            bool: 操作是否成功
        """

        payload = {'BDUSS': self.sessions.BDUSS, 'forum_id': await self.get_fid(tieba_name), 'thread_id': tid}
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/pushRecomToPersonalized",
                                               data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if int(main_json['data']['is_push_success']) != 1:
                raise ValueError(main_json['data']['msg'])

        except Exception as err:
            log.warning(f"Failed to recommend {tid} in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully recommended {tid} in {tieba_name}")
        return True

    async def good(self, tieba_name: str, tid: int, cname: str = '') -> bool:
        """
        加精主题帖

        Args:
            tieba_name (str): 帖子所在贴吧名
            tid (int): 待加精的主题帖tid
            cname (str, optional): 待添加的精华分区名称 默认为''即不分区. Defaults to ''.

        Returns:
            bool: 操作是否成功
        """

        async def _cname2cid() -> int:
            """
            由加精分区名cname获取cid

            Closure Args:
                tieba_name (str): 帖子所在贴吧名
                cname (str, optional): 待添加的精华分区名称 默认为''即不分区. Defaults to ''.

            Returns:
                int: cname对应的分区id
            """

            payload = {
                'BDUSS': self.sessions.BDUSS,
                'word': tieba_name,
            }
            payload['sign'] = self._app_sign(payload)

            try:
                res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/goodlist", data=payload)

                main_json: dict = await res.json(encoding='utf-8', content_type=None)
                if int(main_json['error_code']):
                    raise ValueError(main_json['error_msg'])

                cid = 0
                for item in main_json['cates']:
                    if cname == item['class_name']:
                        cid = int(item['class_id'])
                        break

            except Exception as err:
                log.warning(f"Failed to get cid of {cname} in {tieba_name}. reason:{err}")
                return 0

            return cid

        async def _good(cid: int = 0) -> bool:
            """
            加精主题帖

            Args:
                cid (int, optional): 将主题帖加到cid对应的精华分区 cid默认为0即不分区. Defaults to 0.

            Closure Args:
                tieba_name (str): 帖子所在贴吧名

            Returns:
                bool: 操作是否成功
            """

            payload = {
                'BDUSS': self.sessions.BDUSS,
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

                main_json: dict = await res.json(encoding='utf-8', content_type=None)
                if int(main_json['error_code']):
                    raise ValueError(main_json['error_msg'])

            except Exception as err:
                log.warning(f"Failed to add {tid} to good_list:{cname} in {tieba_name}. reason:{err}")
                return False

            log.info(f"Successfully add {tid} to good_list:{cname} in {tieba_name}")
            return True

        return await _good(await _cname2cid())

    async def ungood(self, tieba_name: str, tid: int) -> bool:
        """
        撤精主题帖

        Args:
            tieba_name (str): 帖子所在贴吧名
            tid (int): 待撤精的主题帖tid

        Returns:
            bool: 操作是否成功
        """

        payload = {
            'BDUSS': self.sessions.BDUSS,
            'fid': await self.get_fid(tieba_name),
            'tbs': await self.get_tbs(),
            'word': tieba_name,
            'z': tid
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/commitgood", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(f"Failed to remove {tid} from good_list in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully removed {tid} from good_list in {tieba_name}")
        return True

    async def top(self, tieba_name: str, tid: int) -> bool:
        """
        置顶主题帖

        Args:
            tieba_name (str): 帖子所在贴吧名
            tid (int): 待置顶的主题帖tid

        Returns:
            bool: 操作是否成功
        """

        payload = {
            'BDUSS': self.sessions.BDUSS,
            'fid': await self.get_fid(tieba_name),
            'ntn': 'set',
            'tbs': await self.get_tbs(),
            'word': tieba_name,
            'z': tid
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/committop", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(f"Failed to add {tid} to top_list in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully add {tid} to top_list in {tieba_name}")
        return True

    async def untop(self, tieba_name: str, tid: int) -> bool:
        """
        撤销置顶主题帖

        Args:
            tieba_name (str): 帖子所在贴吧名
            tid (int): 待撤销置顶的主题帖tid

        Returns:
            bool: 操作是否成功
        """

        payload = {
            'BDUSS': self.sessions.BDUSS,
            'fid': await self.get_fid(tieba_name),
            'tbs': await self.get_tbs(),
            'word': tieba_name,
            'z': tid
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/bawu/committop", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(f"Failed to remove {tid} from top_list in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully removed {tid} from top_list in {tieba_name}")
        return True

    async def get_recover_list(self,
                               tieba_name: str,
                               pn: int = 1,
                               name: str = '') -> tuple[list[tuple[int, int, bool]], bool]:
        """
        获取pn页的待恢复帖子列表

        Args:
            tieba_name (str): 贴吧名
            pn (int, optional): 页码. Defaults to 1.
            name (str, optional): 通过被删帖作者的用户名/昵称查询 默认为空即查询全部. Defaults to ''.

        Returns:
            tuple[list[tuple[int, int, bool]], bool]: list[tid,pid,是否为屏蔽], 是否还有下一页
        """

        params = {'fn': tieba_name, 'fid': await self.get_fid(tieba_name), 'word': name, 'is_ajax': 1, 'pn': pn}

        try:
            res = await self.sessions.web.get("https://tieba.baidu.com/mo/q/bawurecover", params=params)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['no']):
                raise ValueError(main_json['error'])

            data = main_json['data']
            soup = BeautifulSoup(data['content'], 'lxml')
            items = soup.find_all('a', class_='recover_list_item_btn')

        except Exception as err:
            log.warning(f"Failed to get recover_list of {tieba_name} pn:{pn}. reason:{err}")
            res_list = []
            has_more = False

        else:

            def _parse_item(item):
                tid = int(item['attr-tid'])
                pid = int(item['attr-pid'])
                is_frs_mask = bool(int(item['attr-isfrsmask']))

                return tid, pid, is_frs_mask

            res_list = [_parse_item(item) for item in items]
            has_more = data['page']['have_next']

        return res_list, has_more

    async def get_black_list(self, tieba_name: str, pn: int = 1) -> tuple[list[BasicUserInfo], bool]:
        """
        获取pn页的黑名单

        Args:
            tieba_name (str): 贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            tuple[list[BasicUserInfo], bool]: list[基本用户信息], 是否还有下一页
        """

        try:
            res = await self.sessions.web.get("http://tieba.baidu.com/bawu2/platform/listBlackUser",
                                              params={
                                                  'word': tieba_name,
                                                  'pn': pn
                                              })

            soup = BeautifulSoup(await res.text(), 'lxml')
            items = soup.find_all('td', class_='left_cell')

        except Exception as err:
            log.warning(f"Failed to get black_list of {tieba_name} pn:{pn}. reason:{err}")
            res_list = []
            has_more = False

        else:

            def _parse_item(item):
                user_info_item = item.previous_sibling.input
                user = BasicUserInfo()
                user.user_name = user_info_item['data-user-name']
                user.user_id = int(user_info_item['data-user-id'])
                user.portrait = item.a.img['src'][43:]
                return user

            res_list = [_parse_item(item) for item in items]
            has_more = len(items) == 15

        return res_list, has_more

    async def blacklist_add(self, tieba_name: str, user: BasicUserInfo) -> bool:
        """
        添加贴吧黑名单

        Args:
            tieba_name (str): 贴吧名
            user (BasicUserInfo): 基本用户信息

        Returns:
            bool: 操作是否成功
        """

        payload = {'tbs': await self.get_tbs(), 'user_id': user.user_id, 'word': tieba_name, 'ie': 'utf-8'}

        try:
            res = await self.sessions.web.post("http://tieba.baidu.com/bawu2/platform/addBlack", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['errno']):
                raise ValueError(main_json['errmsg'])

        except Exception as err:
            log.warning(f"Failed to add {user.log_name} to black_list in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully added {user.log_name} to black_list in {tieba_name}")
        return True

    async def blacklist_del(self, tieba_name: str, user: BasicUserInfo) -> bool:
        """
        移出贴吧黑名单

        Args:
            tieba_name (str): 贴吧名
            user (BasicUserInfo): 基本用户信息

        Returns:
            bool: 操作是否成功
        """

        payload = {'word': tieba_name, 'tbs': await self.get_tbs(), 'list[]': user.user_id, 'ie': 'utf-8'}

        try:
            res = await self.sessions.web.post("http://tieba.baidu.com/bawu2/platform/cancelBlack", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['errno']):
                raise ValueError(main_json['errmsg'])

        except Exception as err:
            log.warning(f"Failed to remove {user.log_name} from black_list in {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully removed {user.log_name} from black_list in {tieba_name}")
        return True

    async def refuse_appeals(self, tieba_name: str) -> bool:
        """
        拒绝吧内所有解封申诉

        Args:
            tieba_name (str): 贴吧名

        Returns:
            bool: 操作是否成功
        """

        async def _appeal_handle(appeal_id: int, refuse: bool = True) -> bool:
            """
            拒绝或通过解封申诉

            Args:
                appeal_id (int): 申诉请求的appeal_id
                refuse (bool, optional): True则拒绝申诉 False则接受申诉. Defaults to True.

            Closure Args:
                tieba_name (str): 贴吧名

            Returns:
                bool: 操作是否成功
            """

            payload = {
                'fn': tieba_name,
                'fid': await self.get_fid(tieba_name),
                'status': 2 if refuse else 1,
                'refuse_reason': 'Auto Refuse',
                'appeal_id': appeal_id
            }

            try:
                res = await self.sessions.web.post("https://tieba.baidu.com/mo/q/bawuappealhandle", data=payload)

                main_json: dict = await res.json(encoding='utf-8', content_type=None)
                if int(main_json['no']):
                    raise ValueError(main_json['error'])

            except Exception as err:
                log.warning(f"Failed to handle {appeal_id} in {tieba_name}. reason:{err}")
                return False

            log.info(f"Successfully handled {appeal_id} in {tieba_name}. refuse:{refuse}")
            return True

        async def _get_appeal_list() -> list[int]:
            """
            获取申诉请求的appeal_id的列表

            Closure Args:
                tieba_name (str): 贴吧名

            Returns:
                list[int]: 申诉请求的appeal_id的列表
            """

            params = {'fn': tieba_name, 'fid': await self.get_fid(tieba_name)}

            try:
                res = await self.sessions.web.get("https://tieba.baidu.com/mo/q/bawuappeal", params=params)

                soup = BeautifulSoup(await res.text(), 'lxml')

                items = soup.find_all('a', class_='appeal_list_item_btn')

            except Exception as err:
                log.warning(f"Failed to get appeal_list of {tieba_name}. reason:{err}")
                res_list = []

            else:

                def _parse_item(item):
                    search_str = 'aid='
                    start_idx = (href := item['href']).rindex(search_str) + len(search_str)
                    aid = int(href[start_idx:])
                    return aid

                res_list = [_parse_item(item) for item in items]

            return res_list

        while appeal_ids := await _get_appeal_list():
            await asyncio.gather(*[_appeal_handle(appeal_id) for appeal_id in appeal_ids])

        return True

    async def url2image(self, img_url: str) -> Optional[np.ndarray]:
        """
        从链接获取静态图像 若为gif则仅读取第一帧即透明通道帧

        Args:
            img_url (str): 图像链接

        Returns:
            Optional[np.ndarray]: 图像或None
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

        Returns:
            BasicUserInfo: 简略版用户信息 仅保证包含user_name/portrait/user_id
        """

        payload = {
            '_client_version': '12.23.1.0',
            'bdusstoken': self.sessions.BDUSS,
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/s/login", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            user_dict = main_json['user']
            user_proto = ParseDict(user_dict, User_pb2.User(), ignore_unknown_fields=True)
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

        Returns:
            dict[str, bool]: msg字典 value=True则表示有新内容
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

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            msg = {key: bool(int(value)) for key, value in main_json['message'].items()}

        except Exception as err:
            log.warning(f"Failed to get msg reason:{err}")
            msg = {
                'fans': False,
                'replyme': False,
                'atme': False,
                'agree': False,
                'pletter': False,
                'bookmark': False,
                'count': False
            }

        return msg

    async def get_replys(self) -> Replys:
        """
        获取回复信息

        Returns:
            Replys: 回复列表
        """

        common = CommonReq_pb2.CommonReq()
        common.BDUSS = self.sessions.BDUSS
        common._client_version = '12.23.1.0'
        data = ReplyMeReqIdl_pb2.ReplyMeReqIdl.DataReq()
        data.common.CopyFrom(common)
        replyme_req = ReplyMeReqIdl_pb2.ReplyMeReqIdl()
        replyme_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(replyme_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/u/feed/replyme",
                                                     params={'cmd': 303007},
                                                     data=multipart_writer)

            main_proto = ReplyMeResIdl_pb2.ReplyMeResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            replys = Replys(main_proto)

        except Exception as err:
            log.warning(f"Failed to get replys reason:{err}")
            replys = Replys()

        return replys

    async def get_ats(self) -> Ats:
        """
        获取@信息

        Returns:
            Ats: at列表
        """

        payload = {'BDUSS': self.sessions.BDUSS, '_client_version': '12.23.1.0'}
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/u/feed/atme", data=payload)

            main_json: dict = await res.json(encoding='utf-8', loads=JSON_DECODER.decode, content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            ats = Ats(main_json)

        except Exception as err:
            log.warning(f"Failed to get ats reason:{err}")
            ats = Ats()

        return ats

    async def get_homepage(self, _id: Union[str, int]) -> tuple[UserInfo, list[Thread]]:
        """
        获取用户个人页信息

        Args:
            _id (Union[str, int]): 用户id user_id/user_name/portrait

        Returns:
            tuple[UserInfo, list[Thread]]: 用户信息/帖子列表
        """

        if not BasicUserInfo.is_portrait(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = {
            '_client_type': 2,  # 删除该字段会导致post_list为空
            '_client_version': '12.23.1.0',  # 删除该字段会导致post_list和dynamic_list为空
            'friend_uid_portrait': user.portrait,
            'need_post_count': 1,  # 删除该字段会导致无法获取发帖回帖数量
            # 'uid':user_id  # 用该字段检查共同关注的吧
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/u/user/profile", data=payload)

            main_json: dict = await res.json(encoding='utf-8', loads=JSON_DECODER.decode, content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if not main_json.__contains__('user'):
                raise ValueError("invalid params")

        except Exception as err:
            log.warning(f"Failed to get profile of {user.portrait}. reason:{err}")
            return UserInfo(), []

        user = UserInfo(user_proto=ParseDict(main_json['user'], User_pb2.User(), ignore_unknown_fields=True))

        def _init_thread(thread_dict: dict) -> Thread:
            thread = Thread(ParseDict(thread_dict, ThreadInfo_pb2.ThreadInfo(), ignore_unknown_fields=True))
            thread.user = user
            return thread

        threads = [_init_thread(thread_dict) for thread_dict in main_json['post_list']]

        return user, threads

    async def search_post(self,
                          tieba_name: str,
                          query: str,
                          pn: int = 1,
                          rn: int = 30,
                          query_type: int = 0,
                          only_thread: bool = False) -> Searches:
        """
        贴吧搜索

        Args:
            tieba_name (str): 贴吧名
            query (str): 查询文本
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30.
            query_type (int, optional): 查询模式 0为全部搜索结果并且app似乎不提供这一模式 1为app时间倒序 2为app相关性排序. Defaults to 0.
            only_thread (bool, optional): 是否仅查询主题帖. Defaults to False.

        Returns:
            Searches: 搜索结果列表
        """

        payload = {
            '_client_version': '12.23.1.0',
            'kw': tieba_name,
            'only_thread': int(only_thread),
            'pn': pn,
            'rn': rn,
            'sm': query_type,
            'word': query
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/s/searchpost", data=payload)

            main_json: dict = await res.json(encoding='utf-8', loads=JSON_DECODER.decode, content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            searches = Searches(main_json)

        except Exception as err:
            log.warning(f"Failed to search {query} in {tieba_name}. reason:{err}")
            searches = Searches()

        return searches

    async def get_self_forums(self) -> AsyncIterable[tuple[str, int, int, int]]:
        """
        获取本人关注贴吧列表

        Yields:
            AsyncIterable[tuple[str, int, int, int]]: 贴吧名/贴吧id/等级/经验值
        """

        user = await self.get_self_info()

        async def _get_pn_forum_list(_pn: int) -> AsyncIterable[tuple[str, int, int, int]]:
            """
            获取pn页的关注贴吧信息

            Args:
                _pn (int): 页数

            Closure Args:
                user (BasicUserInfo): 本人信息

            Yields:
                AsyncIterable[tuple[str, int, int, int]]: 贴吧名/贴吧id/等级/经验值
            """

            payload = {
                'BDUSS': self.sessions.BDUSS,
                '_client_version': '12.23.1.0',  # 删除该字段可直接获取前200个吧，但无法翻页
                'friend_uid': user.user_id,
                'page_no': _pn  # 加入client_version后，使用该字段控制页数
            }
            payload['sign'] = self._app_sign(payload)

            try:
                res = await self.sessions.app.post("http://c.tieba.baidu.com/c/f/forum/like", data=payload)

                main_json: dict = await res.json(encoding='utf-8', content_type=None)
                if int(main_json['error_code']):
                    raise ValueError(main_json['error_msg'])

                forum_list = main_json.get('forum_list', None)
                if not forum_list:
                    return

            except Exception as err:
                log.warning(f"Failed to get forumlist of {user.user_id}. reason:{err}")
                raise StopAsyncIteration

            nonofficial_forums = forum_list.get('non-gconforum', [])
            official_forums = forum_list.get('gconforum', [])

            def _parse_forum_dict(_forum_dict: dict[str, str]) -> tuple[str, int, int, int]:
                """
                解析关注贴吧的信息

                Args:
                    _forum_dict (dict[str, str]): 关注贴吧信息

                Returns:
                    tuple[str, int, int, int]: 贴吧名/贴吧id/等级/经验值
                """

                tieba_name = _forum_dict['name']
                fid = int(_forum_dict['id'])
                level = int(_forum_dict['level_id'])
                exp = int(_forum_dict['cur_score'])
                return tieba_name, fid, level, exp

            for forum_dict in nonofficial_forums:
                yield _parse_forum_dict(forum_dict)
            for forum_dict in official_forums:
                yield _parse_forum_dict(forum_dict)

            if len(nonofficial_forums) + len(official_forums) != 50:
                raise StopAsyncIteration

        for pn in range(1, sys.maxsize):
            try:
                async for _ in _get_pn_forum_list(pn):
                    yield _
            except RuntimeError:
                return

    async def get_forums(self, _id: Union[str, int]) -> AsyncIterable[tuple[str, int, int, int]]:
        """
        获取用户关注贴吧列表

        Args:
            _id (Union[str, int]): 用户id user_id/user_name/portrait

        Yields:
            AsyncIterable[tuple[str, int, int, int]]: 贴吧名/贴吧id/等级/经验值
        """

        if not UserInfo.is_user_id(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = {
            'BDUSS': self.sessions.BDUSS,
            'friend_uid': user.user_id,
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/f/forum/like", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            for forum in main_json.get('forum_list', []):
                fid = int(forum['id'])
                tieba_name = forum['name']
                level = int(forum['level_id'])
                exp = int(forum['cur_score'])
                yield tieba_name, fid, level, exp

        except Exception as err:
            log.warning(f"Failed to get forumlist of {user.user_id}. reason:{err}")
            return

    async def get_bawu_dict(self, tieba_name: str) -> dict[str, list[BasicUserInfo]]:
        """
        获取吧务信息

        Args:
            tieba_name (str): 贴吧名

        Returns:
            dict[str, list[BasicUserInfo]]: {吧务类型:吧务信息列表}
        """

        common = CommonReq_pb2.CommonReq()
        common._client_version = '12.23.1.0'
        data = GetBawuInfoReqIdl_pb2.GetBawuInfoReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.forum_id = await self.get_fid(tieba_name)
        bawuinfo_req = GetBawuInfoReqIdl_pb2.GetBawuInfoReqIdl()
        bawuinfo_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(bawuinfo_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/f/forum/getBawuInfo",
                                                     params={'cmd': 301007},
                                                     data=multipart_writer)

            main_proto = GetBawuInfoResIdl_pb2.GetBawuInfoResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            roledes_protos = main_proto.data.bawu_team_info.bawu_team_list
            bawu_dict = {
                roledes_proto.role_name:
                [BasicUserInfo(user_proto=roleinfo_proto) for roleinfo_proto in roledes_proto.role_info]
                for roledes_proto in roledes_protos
            }

        except Exception as err:
            log.warning(f"Failed to get adminlist reason: {err}")
            bawu_dict = {}

        return bawu_dict

    async def get_tab_map(self, tieba_name: str) -> dict[str, int]:
        """
        获取分区名到分区id的映射字典

        Args:
            tieba_name (str): 贴吧名

        Returns:
            dict[str, int]: {分区名:分区id}
        """

        common = CommonReq_pb2.CommonReq()
        common.BDUSS = self.sessions.BDUSS
        common._client_version = '12.23.1.0'
        data = SearchPostForumReqIdl_pb2.SearchPostForumReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.word = tieba_name
        searchforum_req = SearchPostForumReqIdl_pb2.SearchPostForumReqIdl()
        searchforum_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(searchforum_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/f/forum/searchPostForum",
                                                     params={'cmd': 309466},
                                                     data=multipart_writer)

            main_proto = SearchPostForumResIdl_pb2.SearchPostForumResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            tab_map = {tab_proto.tab_name: tab_proto.tab_id for tab_proto in main_proto.data.exact_match.tab_info}

        except Exception as err:
            log.warning(f"Failed to get tab_map of {tieba_name}. reason:{err}")
            tab_map = {}

        return tab_map

    async def get_recom_list(self, tieba_name: str, pn: int = 1) -> tuple[list[tuple[Thread, int]], bool]:
        """
        获取pn页的大吧主推荐帖列表

        Args:
            tieba_name (str): 贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            tuple[list[tuple[Thread, int]], bool]: list[被推荐帖子信息,新增浏览量], 是否还有下一页
        """

        payload = {
            'BDUSS': self.sessions.BDUSS,
            '_client_version': '12.23.1.0',
            'forum_id': await self.get_fid(tieba_name),
            'pn': pn,
            'rn': 30,
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/f/bawu/getRecomThreadHistory", data=payload)

            main_json: dict = await res.json(encoding='utf-8', loads=JSON_DECODER.decode, content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(f"Failed to get recom_list of {tieba_name}. reason:{err}")
            res_list = []
            has_more = False

        else:

            def _parse_data_dict(data_dict):
                thread = Thread(
                    ParseDict(data_dict['thread_list'], ThreadInfo_pb2.ThreadInfo(), ignore_unknown_fields=True))
                add_view = thread.view_num - int(data_dict['current_pv'])
                return thread, add_view

            res_list = [_parse_data_dict(data_dict) for data_dict in main_json['recom_thread_list']]
            has_more = bool(int(main_json['is_has_more']))

        return res_list, has_more

    async def get_recom_status(self, tieba_name: str) -> tuple[int, int]:
        """
        获取大吧主推荐功能的月度配额状态

        Args:
            tieba_name (str): 贴吧名

        Returns:
            tuple[int, int]: 本月总推荐配额/本月已使用的推荐配额
        """

        payload = {
            'BDUSS': self.sessions.BDUSS,
            '_client_version': '12.23.1.0',
            'forum_id': await self.get_fid(tieba_name),
            'pn': 1,
            'rn': 0,
        }
        payload['sign'] = self._app_sign(payload)

        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/f/bawu/getRecomThreadList", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            total_recom_num = int(main_json['total_recommend_num'])
            used_recom_num = int(main_json['used_recommend_num'])

        except Exception as err:
            log.warning(f"Failed to get recom_status of {tieba_name}. reason:{err}")
            total_recom_num = 0
            used_recom_num = 0

        return total_recom_num, used_recom_num

    async def get_statistics(self, tieba_name: str) -> dict[str, list[int]]:
        """
        获取吧务后台中最近29天的统计数据

        Args:
            tieba_name (str): 贴吧名

        Returns:
            dict[str, list[int]]: {字段名:按时间顺序排列的统计数据}
            {'view': 浏览量,
             'thread': 主题帖数,
             'member': 关注数,
             'post': 回复数,
             'sign_ratio': 签到率,
             'average_time': 人均浏览时长,
             'average_times': 人均进吧次数,
             'recommend': 首页推荐数}
        """

        payload = {
            'BDUSS': self.sessions.BDUSS,
            '_client_version': '12.23.1.0',
            'forum_id': await self.get_fid(tieba_name),
        }
        payload['sign'] = self._app_sign(payload)

        field_names = ['view', 'thread', 'member', 'post', 'sign_ratio', 'average_time', 'average_times', 'recommend']
        try:
            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/f/forum/getforumdata", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

            data = main_json['data']
            stat = {
                field_name: [int(item['value']) for item in reversed(data_i['group'][1]['values'])]
                for field_name, data_i in zip(field_names, data)
            }

        except Exception as err:
            log.warning(f"Failed to get recom_status of {tieba_name}. reason:{err}")
            stat = {field_name: [] for field_name in field_names}

        return stat

    async def get_rank_list(self, tieba_name: str, pn: int = 1) -> tuple[list[tuple[str, int, int, bool]], bool]:
        """
        获取pn页的贴吧等级排行榜

        Args:
            tieba_name (str): 贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            tuple[list[tuple[str, int, int, bool]], bool]: list[用户名,等级,经验值,是否vip], 是否还有下一页
        """

        try:
            res = await self.sessions.web.get("http://tieba.baidu.com/f/like/furank",
                                              params={
                                                  'kw': tieba_name,
                                                  'pn': pn,
                                                  'ie': 'utf-8'
                                              })

            soup = BeautifulSoup(await res.text(), 'lxml')
            items = soup.select('tr[class^=drl_list_item]')

        except Exception as err:
            log.warning(f"Failed to get rank_list of {tieba_name} pn:{pn}. reason:{err}")
            res_list = []
            has_more = False

        else:

            def _parse_item(item):
                user_name_item = item.td.next_sibling
                user_name = user_name_item.text
                is_vip = 'drl_item_vip' in user_name_item.div['class']
                level_item = user_name_item.next_sibling
                # e.g. get level 16 from string "bg_lv16" by slicing [5:]
                level = int(level_item.div['class'][0][5:])
                exp_item = level_item.next_sibling
                exp = int(exp_item.text)

                return user_name, level, exp, is_vip

            res_list = [_parse_item(item) for item in items]
            has_more = len(items) == 20

        return res_list, has_more

    async def get_member_list(self, tieba_name: str, pn: int = 1) -> tuple[list[tuple[str, str, int]], bool]:
        """
        获取pn页的贴吧最新关注用户列表

        Args:
            tieba_name (str): 贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            tuple[list[tuple[str, str, int]], bool]: list[用户名,portrait,等级], 是否还有下一页
        """

        try:
            res = await self.sessions.web.get("http://tieba.baidu.com/bawu2/platform/listMemberInfo",
                                              params={
                                                  'word': tieba_name,
                                                  'pn': pn,
                                                  'ie': 'utf-8'
                                              })

            soup = BeautifulSoup(await res.text(), 'lxml')
            items = soup.find_all('div', class_='name_wrap')

        except Exception as err:
            log.warning(f"Failed to get member_list of {tieba_name} pn:{pn}. reason:{err}")
            res_list = []
            has_more = False

        else:

            def _parse_item(item):
                user_item = item.a
                user_name = user_item['title']
                portrait = user_item['href'][14:]
                level_item = item.span
                level = int(level_item['class'][1][12:])
                return user_name, portrait, level

            res_list = [_parse_item(item) for item in items]
            has_more = len(items) == 24

        return res_list, has_more

    async def like_forum(self, tieba_name: str) -> bool:
        """
        关注吧

        Args:
            tieba_name (str): 贴吧名

        Returns:
            bool: 操作是否成功
        """

        try:
            payload = {'BDUSS': self.sessions.BDUSS, 'fid': await self.get_fid(tieba_name), 'tbs': await self.get_tbs()}
            payload['sign'] = self._app_sign(payload)

            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/forum/like", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
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

        Args:
            tieba_name (str): 贴吧名

        Returns:
            bool: 签到是否成功
        """

        try:
            payload = {
                'BDUSS': self.sessions.BDUSS,
                '_client_version': '12.23.1.0',
                'kw': tieba_name,
                'tbs': await self.get_tbs(),
            }
            payload['sign'] = self._app_sign(payload)

            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/forum/sign", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if int(main_json['user_info']['sign_bonus_point']) == 0:
                raise ValueError("sign_bonus_point is 0")

        except Exception as err:
            log.warning(f"Failed to sign forum {tieba_name}. reason:{err}")
            return False

        log.info(f"Successfully sign forum {tieba_name}")
        return True

    async def add_post(self, tieba_name: str, tid: int, content: str) -> bool:
        """
        回帖

        Args:
            tieba_name (str): 要回复的主题帖所在吧名
            tid (int): 要回复的主题帖的tid
            content (str): 回复内容

        Returns:
            bool: 回帖是否成功

        Notice:
            本接口仍处于测试阶段，有一定永封风险！请谨慎使用！
            已通过的测试: cookie白板号(无头像无关注吧无发帖记录 2元/个) 通过异地阿里云ip出口以3分钟的发送间隔发15条回复不吞楼不封号
        """

        try:
            payload = {
                'BDUSS': self.sessions.BDUSS,
                '_client_id': 'wappc_1641793173806_732',
                '_client_type': 2,
                '_client_version': '9.1.0.0',
                '_phone_imei': '000000000000000',
                'anonymous': 1,
                'apid': 'sw',
                'barrage_time': 0,
                'can_no_forum': 0,
                'content': content,
                'cuid': 'baidutiebaapp75036bd3-8ae0-4b61-ac4e-c3192b6e6fa9',
                'cuid_galaxy2': '1782A7D2758F38EA4B4EAFE1AD4881CB|VLJONH23W',
                'cuid_gid': '',
                'entrance_type': 0,
                'fid': await self.get_fid(tieba_name),
                'from': '1021099l',
                'from_fourm_id': 'null',
                'is_ad': 0,
                'is_barrage': 0,
                'is_feedback': 0,
                'kw': tieba_name,
                'model': 'M2012K11AC',
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
                'timestamp': int(time.time() * 1000),
                'v_fid': '',
                'v_fname': '',
                'vcode_tag': 12,
                'z_id': '9JaXHshXKDw1xkGLIi91_Qd4cduxNFKS_nguQ4kfe7zYZQfdOlA-7jU2pYbkMfw23NdB1awUpuWmTeoON13r-Uw'
            }
            payload['sign'] = self._app_sign(payload)

            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/post/add", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])
            if int(main_json['info']['need_vcode']):
                raise ValueError("need verify code")

        except Exception as err:
            log.warning(f"Failed to add post in {tid}. reason:{err}")
            return False

        log.info(f"Successfully add post in {tid}")
        return True

    async def set_privacy(self, tid: int, hide: bool = True) -> bool:
        """
        隐藏主题帖

        Args:
            tid (int): 主题帖tid
            hide (bool, optional): True则设为隐藏 False则取消隐藏. Defaults to True.

        Returns:
            bool: 操作是否成功
        """

        if not (posts := await self.get_posts(tid)):
            log.warning(f"Failed to set privacy to {tid}")
            return False

        try:
            payload = {
                'BDUSS': self.sessions.BDUSS,
                'forum_id': posts[0].fid,
                'is_hide': int(hide),
                'post_id': posts[0].pid,
                'thread_id': tid
            }
            payload['sign'] = self._app_sign(payload)

            res = await self.sessions.app.post("http://c.tieba.baidu.com/c/c/thread/setPrivacy", data=payload)

            main_json: dict = await res.json(encoding='utf-8', content_type=None)
            if int(main_json['error_code']):
                raise ValueError(main_json['error_msg'])

        except Exception as err:
            log.warning(f"Failed to set privacy to {tid}. reason:{err}")
            return False

        log.info(f"Successfully set privacy to {tid}. is_hide:{hide}")
        return True

    async def tieba_uid2user_info(self, tieba_uid: int) -> UserInfo:
        """
        通过tieba_uid补全用户信息

        Args:
            tieba_uid (int): 新版tieba_uid 请注意与旧版user_id的区别

        Returns:
            UserInfo: 完整版用户信息
        """

        common = CommonReq_pb2.CommonReq()
        data = GetUserByTiebaUidReqIdl_pb2.GetUserByTiebaUidReqIdl.DataReq()
        data.common.CopyFrom(common)
        data.tieba_uid = str(tieba_uid)
        userinfo_req = GetUserByTiebaUidReqIdl_pb2.GetUserByTiebaUidReqIdl()
        userinfo_req.data.CopyFrom(data)

        multipart_writer = self.get_tieba_multipart_writer(userinfo_req.SerializeToString())

        try:
            res = await self.sessions.app_proto.post("http://c.tieba.baidu.com/c/u/user/getUserByTiebaUid",
                                                     params={'cmd': 309702},
                                                     data=multipart_writer)

            main_proto = GetUserByTiebaUidResIdl_pb2.GetUserByTiebaUidResIdl()
            main_proto.ParseFromString(await res.content.read())
            if int(main_proto.error.errorno):
                raise ValueError(main_proto.error.errmsg)

            user_proto = main_proto.data.user
            user = UserInfo(user_proto=user_proto)

        except Exception as err:
            log.warning(f"Failed to get UserInfo of {tieba_uid}. reason:{err}")
            user = UserInfo()

        return user
