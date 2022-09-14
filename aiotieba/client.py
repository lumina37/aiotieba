__all__ = ['Client']

try:
    import cv2 as cv
    import numpy as np
except ImportError:
    pass

import asyncio
import base64
import binascii
import gzip
import hashlib
import json
import random
import time
import uuid
import weakref
from typing import ClassVar, Dict, List, Literal, Optional, Tuple, Union

import aiohttp
import bs4
import yarl
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from google.protobuf.json_format import ParseDict

from ._config import CONFIG
from ._exceptions import ContentTypeError, TiebaServerError
from ._helpers import JSON_DECODE_FUNC
from ._logger import LOG
from .protobuf import (
    CommitPersonalMsgReqIdl_pb2,
    CommitPersonalMsgResIdl_pb2,
    FrsPageReqIdl_pb2,
    FrsPageResIdl_pb2,
    GetBawuInfoReqIdl_pb2,
    GetBawuInfoResIdl_pb2,
    GetDislikeListReqIdl_pb2,
    GetDislikeListResIdl_pb2,
    GetForumSquareReqIdl_pb2,
    GetForumSquareResIdl_pb2,
    GetUserByTiebaUidReqIdl_pb2,
    GetUserByTiebaUidResIdl_pb2,
    GetUserInfoReqIdl_pb2,
    GetUserInfoResIdl_pb2,
    PbFloorReqIdl_pb2,
    PbFloorResIdl_pb2,
    PbPageReqIdl_pb2,
    PbPageResIdl_pb2,
    ProfileReqIdl_pb2,
    ProfileResIdl_pb2,
    ReplyMeReqIdl_pb2,
    ReplyMeResIdl_pb2,
    SearchPostForumReqIdl_pb2,
    SearchPostForumResIdl_pb2,
    UpdateClientInfoReqIdl_pb2,
    UpdateClientInfoResIdl_pb2,
    User_pb2,
    UserPostReqIdl_pb2,
    UserPostResIdl_pb2,
)
from .typedefs import (
    Appeals,
    Ats,
    BasicUserInfo,
    BlacklistUsers,
    Comments,
    DislikeForums,
    Fans,
    FollowForums,
    Follows,
    Forum,
    MemberUsers,
    NewThread,
    Posts,
    RankUsers,
    RecomThreads,
    Recovers,
    Replys,
    Searches,
    SelfFollowForums,
    SquareForums,
    Threads,
    UserInfo,
    UserPosts,
)


class _WebsocketResponse(object):
    """
    websocket响应

    Attributes:
        timestamp (int): 请求时间戳
        req_id (int): 唯一的请求id
    """

    __slots__ = ['__weakref__', '__dict__', '_timestamp', '_req_id', '_data_future']

    ws_res_wait_dict: weakref.WeakValueDictionary[int, "_WebsocketResponse"] = weakref.WeakValueDictionary()
    _websocket_request_id: int = None

    def __init__(self) -> None:
        self._timestamp: int = int(time.time())
        self._req_id = None
        self._data_future: asyncio.Future = asyncio.Future()

        self.ws_res_wait_dict[self.req_id] = self

    def __hash__(self) -> int:
        return self.req_id

    def __eq__(self, obj: "_WebsocketResponse"):
        return self.req_id == obj.req_id

    @property
    def timestamp(self) -> int:
        """
        请求时间戳

        Note:
            13位时间戳
        """

        return self._timestamp

    @property
    def req_id(self) -> int:
        """
        返回一个唯一的请求id
        在初次生成后该属性便不会再发生变化
        """

        if self._req_id is None:

            if self._websocket_request_id is None:
                self._websocket_request_id = self._timestamp
            self._websocket_request_id += 1
            self._req_id = self._websocket_request_id

        return self._req_id

    async def read(self, timeout: float) -> bytes:
        """
        读取websocket返回数据

        Args:
            timeout (float): 设置超时秒数

        Raises:
            asyncio.TimeoutError: 超时后抛出该异常

        Returns:
            bytes: 从websocket接收到的数据
        """

        try:
            data: bytes = await asyncio.wait_for(self._data_future, timeout)
        except asyncio.TimeoutError:
            del self.ws_res_wait_dict[self.req_id]
            raise asyncio.TimeoutError("Timeout to read")

        del self.ws_res_wait_dict[self.req_id]
        return data


class Client(object):
    """
    贴吧客户端

    Args:
        BDUSS_key (str, optional): 用于快捷调用BDUSS. Defaults to None.
    """

    __slots__ = [
        '_BDUSS_key',
        '_BDUSS',
        '_STOKEN',
        '_user',
        '_tbs',
        '_client_id',
        '_cuid',
        '_cuid_galaxy2',
        '_ws_password',
        '_connector',
        '_loop',
        '_app_base_url',
        '_session_app',
        '_session_app_proto',
        '_session_web',
        '_session_websocket',
        'websocket',
        '_ws_aes_chiper',
        '_ws_dispatcher',
    ]

    _trust_env = False

    latest_version: ClassVar[str] = "12.29.0.1"  # 这是目前的最新版本
    # no_fold_version: ClassVar[str] = "12.12.1.0"  # 这是最后一个回复列表不发生折叠的版本
    post_version: ClassVar[str] = "9.1.0.0"  # 发帖使用极速版

    _fname2fid: ClassVar[Dict[str, int]] = {}
    _fid2fname: ClassVar[Dict[int, str]] = {}

    def __init__(self, BDUSS_key: Optional[str] = None) -> None:
        self._BDUSS_key = BDUSS_key

        user_cfg: Dict[str, str] = CONFIG['User'].get(BDUSS_key, {})
        self.BDUSS = user_cfg.get('BDUSS', '')
        self.STOKEN = user_cfg.get('STOKEN', '')

        self._user: BasicUserInfo = None
        self._tbs: str = None
        self._client_id: str = None
        self._cuid: str = None
        self._cuid_galaxy2: str = None
        self._ws_password: bytes = None

        self._loop = asyncio.get_running_loop()
        self._app_base_url = yarl.URL.build(scheme="http", host="tiebac.baidu.com")

        self._connector: aiohttp.TCPConnector = None
        self._session_app: aiohttp.ClientSession = None
        self._session_app_proto: aiohttp.ClientSession = None
        self._session_web: aiohttp.ClientSession = None
        self._session_websocket: aiohttp.ClientSession = None
        self.websocket: aiohttp.ClientWebSocketResponse = None
        self._ws_aes_chiper = None
        self._ws_dispatcher: asyncio.Task = None

    async def __aenter__(self) -> "Client":
        return self

    async def close(self) -> None:
        if self._ws_dispatcher is not None:
            self._ws_dispatcher.cancel()

        if self.websocket is not None and not self.websocket.closed:
            await self.websocket.close()

        if self._connector is not None:
            await self._connector.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @property
    def BDUSS_key(self) -> str:
        """
        当前账号的BDUSS_key
        """

        return self._BDUSS_key

    @property
    def BDUSS(self) -> str:
        """
        当前账号的BDUSS
        """

        return self._BDUSS

    @BDUSS.setter
    def BDUSS(self, new_BDUSS: str) -> None:

        if hasattr(self, "_BDUSS"):
            LOG.warning("BDUSS已初始化 无法修改")
            return

        if not new_BDUSS:
            self._BDUSS = ""
            return

        legal_length = 192
        if (len_new_BDUSS := len(new_BDUSS)) != legal_length:
            LOG.warning(f"BDUSS的长度应为{legal_length}个字符 而输入的{new_BDUSS}有{len_new_BDUSS}个字符")
            self._BDUSS = ""
            return

        self._BDUSS = new_BDUSS

    @property
    def STOKEN(self) -> str:
        """
        当前账号的STOKEN
        """

        return self._STOKEN

    @STOKEN.setter
    def STOKEN(self, new_STOKEN: str) -> None:

        if hasattr(self, "_STOKEN"):
            LOG.warning("STOKEN已初始化 无法修改")
            return

        if not new_STOKEN:
            self._STOKEN = ""
            return

        legal_length = 64
        if (len_new_STOKEN := len(new_STOKEN)) != legal_length:
            LOG.warning(f"STOKEN的长度应为{legal_length}个字符 而输入的{new_STOKEN}有{len_new_STOKEN}个字符")
            self._STOKEN = ""
            return

        self._STOKEN = new_STOKEN

    @property
    def timestamp_ms(self) -> int:
        """
        毫秒级本机时间戳 (13位整数)

        Returns:
            int: 毫秒级整数时间戳
        """

        return int(time.time() * 1000)

    @property
    def client_id(self) -> str:
        """
        返回一个可作为请求参数的client_id
        在初次生成后该属性便不会再发生变化

        Returns:
            str: 举例 wappc_1653660000000_123
        """

        if self._client_id is None:
            self._client_id = f"wappc_{self.timestamp_ms}_{random.randint(0,999):03d}"
        return self._client_id

    @property
    def cuid(self) -> str:
        """
        返回一个可作为请求参数的cuid
        在初次生成后该属性便不会再发生变化

        Returns:
            str: 举例 baidutiebaappe4200716-58a8-4170-af15-ea7edeb8e513
        """

        if self._cuid is None:
            self._cuid = "baidutiebaapp" + str(uuid.uuid4())
        return self._cuid

    @property
    def cuid_galaxy2(self) -> str:
        """
        返回一个可作为请求参数的cuid_galaxy2
        在初次生成后该属性便不会再发生变化

        Returns:
            str: 举例 159AB36E0E5C55E4AAE340CA046F1303|0
        """

        if self._cuid_galaxy2 is None:
            rand_str = binascii.hexlify(random.randbytes(16)).decode('ascii').upper()
            self._cuid_galaxy2 = rand_str + "|0"

        return self._cuid_galaxy2

    @property
    def ws_password(self) -> bytes:
        """
        返回一个供贴吧websocket使用的随机密码
        在初次生成后该属性便不会再发生变化

        Returns:
            bytes: 长度为36字节的随机密码
        """

        if self._ws_password is None:
            self._ws_password = random.randbytes(36)
        return self._ws_password

    @property
    def connector(self) -> aiohttp.TCPConnector:
        """
        TCP连接器

        Returns:
            aiohttp.TCPConnector
        """

        if self._connector is None:
            self._connector = aiohttp.TCPConnector(
                ttl_dns_cache=600,
                keepalive_timeout=60,
                limit=0,
                ssl=False,
                loop=self._loop,
            )

        return self._connector

    @property
    def session_app(self) -> aiohttp.ClientSession:
        """
        用于APP请求

        Returns:
            aiohttp.ClientSession
        """

        if self._session_app is None:
            headers = {
                aiohttp.hdrs.USER_AGENT: f"tieba/{self.latest_version}",
                aiohttp.hdrs.CONNECTION: "keep-alive",
                aiohttp.hdrs.ACCEPT_ENCODING: "gzip",
                aiohttp.hdrs.HOST: self._app_base_url.host,
            }
            timeout = aiohttp.ClientTimeout(connect=6.0, sock_connect=3.2, sock_read=12.0)

            self._session_app = aiohttp.ClientSession(
                base_url=self._app_base_url,
                connector=self.connector,
                loop=self._loop,
                headers=headers,
                connector_owner=False,
                raise_for_status=True,
                timeout=timeout,
                read_bufsize=1 << 18,  # 256KiB
                trust_env=self._trust_env,
            )

        return self._session_app

    @property
    def session_app_proto(self) -> aiohttp.ClientSession:
        """
        用于APP protobuf请求

        Returns:
            aiohttp.ClientSession
        """

        if self._session_app_proto is None:
            headers = {
                aiohttp.hdrs.USER_AGENT: f"tieba/{self.latest_version}",
                "x_bd_data_type": "protobuf",
                aiohttp.hdrs.CONNECTION: "keep-alive",
                aiohttp.hdrs.ACCEPT_ENCODING: "gzip",
                aiohttp.hdrs.HOST: self._app_base_url.host,
            }
            timeout = aiohttp.ClientTimeout(connect=6.0, sock_connect=3.2, sock_read=12.0)

            self._session_app_proto = aiohttp.ClientSession(
                base_url=self._app_base_url,
                connector=self.connector,
                loop=self._loop,
                headers=headers,
                connector_owner=False,
                raise_for_status=True,
                timeout=timeout,
                read_bufsize=1 << 18,  # 256KiB
                trust_env=self._trust_env,
            )

        return self._session_app_proto

    @property
    def session_web(self) -> aiohttp.ClientSession:
        """
        用于网页端请求

        Returns:
            aiohttp.ClientSession
        """

        if self._session_web is None:
            headers = {
                aiohttp.hdrs.USER_AGENT: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
                aiohttp.hdrs.ACCEPT_ENCODING: "gzip, deflate",
                aiohttp.hdrs.CACHE_CONTROL: "no-cache",
                aiohttp.hdrs.CONNECTION: "keep-alive",
            }
            timeout = aiohttp.ClientTimeout(connect=6.0, sock_connect=3.2, sock_read=12.0)
            cookie_jar = aiohttp.CookieJar(loop=self._loop)
            cookie_jar.update_cookies({'BDUSS': self.BDUSS, 'STOKEN': self.STOKEN})

            self._session_web = aiohttp.ClientSession(
                connector=self.connector,
                loop=self._loop,
                headers=headers,
                cookie_jar=cookie_jar,
                connector_owner=False,
                raise_for_status=True,
                timeout=timeout,
                read_bufsize=1 << 20,  # 1MiB
                trust_env=self._trust_env,
            )

        return self._session_web

    @property
    def session_websocket(self) -> aiohttp.ClientSession:
        """
        用于websocket请求

        Returns:
            aiohttp.ClientSession
        """

        if self._session_websocket is None:
            headers = {
                aiohttp.hdrs.HOST: "im.tieba.baidu.com:8000",
                aiohttp.hdrs.SEC_WEBSOCKET_EXTENSIONS: "im_version=2.3",
            }
            timeout = aiohttp.ClientTimeout(connect=6.0, sock_connect=3.2, sock_read=12.0)

            self._session_websocket = aiohttp.ClientSession(
                connector=self.connector,
                loop=self._loop,
                headers=headers,
                connector_owner=False,
                raise_for_status=True,
                timeout=timeout,
                read_bufsize=1 << 18,  # 256KiB
                trust_env=self._trust_env,
            )

        return self._session_websocket

    @staticmethod
    def pack_form(forms: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        打包form参数元组列表 为其添加贴吧客户端签名

        Args:
            payload (list[tuple[str, str]]): form参数元组列表

        Returns:
            list[tuple[str, str]]: 签名后的form参数元组列表
        """

        raw_list = [f"{k}={v}" for k, v in forms]
        raw_list.append("tiebaclient!!!")
        raw_str = "".join(raw_list)

        md5 = hashlib.md5()
        md5.update(raw_str.encode('utf-8'))
        forms.append(('sign', md5.hexdigest()))

        return forms

    @staticmethod
    def pack_proto_bytes(req_bytes: bytes) -> aiohttp.MultipartWriter:
        """
        将req_bytes打包为贴吧客户端专用的aiohttp.MultipartWriter

        Args:
            req_bytes (bytes): protobuf序列化后的二进制数据

        Returns:
            aiohttp.MultipartWriter: 只可用于贴吧客户端
        """

        writer = aiohttp.MultipartWriter('form-data', boundary=f"*-672328094-42-{random.randint(0,9)}")
        payload_headers = {
            aiohttp.hdrs.CONTENT_DISPOSITION: aiohttp.helpers.content_disposition_header(
                'form-data', name='data', filename='file'
            )
        }
        payload = aiohttp.BytesPayload(req_bytes, content_type='', headers=payload_headers)
        payload.headers.popone(aiohttp.hdrs.CONTENT_TYPE)
        writer.append_payload(payload)
        writer._parts[0][0].headers.popone(aiohttp.hdrs.CONTENT_LENGTH)

        return writer

    @property
    def ws_aes_chiper(self):
        """
        获取供贴吧websocket使用的AES加密器

        Returns:
            Any: AES chiper
        """

        if self._ws_aes_chiper is None:
            salt = b'\xa4\x0b\xc8\x34\xd6\x95\xf3\x13'
            ws_secret_key = hashlib.pbkdf2_hmac('sha1', self.ws_password, salt, 5, 32)
            self._ws_aes_chiper = AES.new(ws_secret_key, AES.MODE_ECB)

        return self._ws_aes_chiper

    def _pack_ws_bytes(
        self, ws_bytes: bytes, /, cmd: int, req_id: int, *, need_gzip: bool = True, need_encrypt: bool = True
    ) -> bytes:
        """
        对ws_bytes进行打包 压缩加密并添加9字节头部

        Args:
            ws_bytes (bytes): 待发送的websocket数据
            cmd (int): 请求的cmd类型
            req_id (int): 请求的id
            need_gzip (bool, optional): 是否需要gzip压缩. Defaults to False.
            need_encrypt (bool, optional): 是否需要aes加密. Defaults to False.

        Returns:
            bytes: 打包后的websocket数据
        """

        if need_gzip:
            ws_bytes = gzip.compress(ws_bytes, 5)

        if need_encrypt:
            pad_num = AES.block_size - (len(ws_bytes) % AES.block_size)
            ws_bytes += pad_num.to_bytes(1, 'big') * pad_num
            ws_bytes = self.ws_aes_chiper.encrypt(ws_bytes)

        flag = 0x08 | (need_gzip << 7) | (need_encrypt << 6)
        ws_bytes = b''.join(
            [
                flag.to_bytes(1, 'big'),
                cmd.to_bytes(4, 'big'),
                req_id.to_bytes(4, 'big'),
                ws_bytes,
            ]
        )

        return ws_bytes

    def _unpack_ws_bytes(self, ws_bytes: bytes) -> Tuple[bytes, int, int]:
        """
        对ws_bytes进行解包

        Args:
            ws_bytes (bytes): 接收到的websocket数据

        Returns:
            bytes: 解包后的websocket数据
            int: 对应请求的cmd类型
            int: 对应请求的id
        """

        if len(ws_bytes) < 9:
            return ws_bytes, 0, 0

        flag = ws_bytes[0]
        cmd = int.from_bytes(ws_bytes[1:5], 'big')
        req_id = int.from_bytes(ws_bytes[5:9], 'big')

        ws_bytes = ws_bytes[9:]
        if flag & 0b10000000:
            ws_bytes = self.ws_aes_chiper.decrypt(ws_bytes)
            ws_bytes = ws_bytes.rstrip(ws_bytes[-2:-1])
        if flag & 0b01000000:
            ws_bytes = gzip.decompress(ws_bytes)

        return ws_bytes, cmd, req_id

    async def _create_websocket(self, heartbeat: Optional[float] = None) -> None:
        """
        建立weboscket连接

        Args:
            heartbeat (float, optional): 是否定时ping. Defaults to None.

        Raises:
            aiohttp.WSServerHandshakeError: websocket握手失败
        """

        if self.session_websocket is None:
            await self.enter()

        if self._ws_dispatcher is not None and not self._ws_dispatcher.cancelled():
            self._ws_dispatcher.cancel()

        self.websocket = await self.session_websocket._ws_connect(
            yarl.URL.build(scheme="ws", host="im.tieba.baidu.com", port=8000), heartbeat=heartbeat, ssl=False
        )
        self._ws_dispatcher = asyncio.create_task(self._ws_dispatch(), name="ws_dispatcher")

    @property
    def is_ws_aviliable(self) -> bool:
        """
        self.websocket是否可用

        Returns:
            bool: True则self.websocket可用 反之不可用
        """

        return not (self.websocket is None or self.websocket.closed or self.websocket._writer.transport.is_closing())

    async def send_ws_bytes(
        self, ws_bytes: bytes, /, cmd: int, *, need_gzip: bool = True, need_encrypt: bool = True
    ) -> _WebsocketResponse:
        """
        将ws_bytes通过贴吧websocket发送

        Args:
            ws_bytes (bytes): 待发送的websocket数据
            cmd (int, optional): 请求的cmd类型
            need_gzip (bool, optional): 是否需要gzip压缩. Defaults to False.
            need_encrypt (bool, optional): 是否需要aes加密. Defaults to False.

        Returns:
            WebsocketResponse: 用于等待返回数据的WebsocketResponse实例
        """

        ws_res = _WebsocketResponse()
        ws_bytes = self._pack_ws_bytes(ws_bytes, cmd, ws_res.req_id, need_gzip=need_gzip, need_encrypt=need_encrypt)

        _WebsocketResponse.ws_res_wait_dict[ws_res.req_id] = ws_res
        await self.websocket.send_bytes(ws_bytes)

        return ws_res

    async def _ws_dispatch(self) -> None:
        """
        分发从贴吧websocket接收到的数据
        """

        try:
            async for msg in self.websocket:
                res_bytes, _, req_id = self._unpack_ws_bytes(msg.data)

                ws_res = _WebsocketResponse.ws_res_wait_dict.get(req_id, None)
                if ws_res:
                    ws_res._data_future.set_result(res_bytes)

        except asyncio.CancelledError:
            return

    async def _init_websocket(self) -> bool:
        """
        初始化weboscket连接对象并发送初始化信息

        Raises:
            ValueError: 服务端返回错误

        Returns:
            bool: True成功 False失败
        """

        if not self.is_ws_aviliable:
            await self._create_websocket()

            pub_key_bytes = base64.b64decode(
                "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwQpwBZxXJV/JVRF/uNfyMSdu7YWwRNLM8+2xbniGp2iIQHOikPpTYQjlQgMi1uvq1kZpJ32rHo3hkwjy2l0lFwr3u4Hk2Wk7vnsqYQjAlYlK0TCzjpmiI+OiPOUNVtbWHQiLiVqFtzvpvi4AU7C1iKGvc/4IS45WjHxeScHhnZZ7njS4S1UgNP/GflRIbzgbBhyZ9kEW5/OO5YfG1fy6r4KSlDJw4o/mw5XhftyIpL+5ZBVBC6E1EIiP/dd9AbK62VV1PByfPMHMixpxI3GM2qwcmFsXcCcgvUXJBa9k6zP8dDQ3csCM2QNT+CQAOxthjtp/TFWaD7MzOdsIYb3THwIDAQAB".encode(
                    'ascii'
                )
            )
            pub_key = RSA.import_key(pub_key_bytes)
            rsa_chiper = PKCS1_v1_5.new(pub_key)

            data_proto = UpdateClientInfoReqIdl_pb2.UpdateClientInfoReqIdl.DataReq()
            data_proto.bduss = self.BDUSS
            data_proto.device = f"""{{"subapp_type":"mini","_client_version":"{self.post_version}","pversion":"1.0.3","_msg_status":"1","_phone_imei":"000000000000000","from":"1021099l","cuid_galaxy2":"{self.cuid_galaxy2}","model":"LIO-AN00","_client_type":"2"}}"""
            data_proto.secretKey = rsa_chiper.encrypt(self.ws_password)
            req_proto = UpdateClientInfoReqIdl_pb2.UpdateClientInfoReqIdl()
            req_proto.data.CopyFrom(data_proto)
            req_proto.cuid = f"{self.cuid}|com.baidu.tieba_mini{self.post_version}"

            resp = await self.send_ws_bytes(
                req_proto.SerializeToString(), cmd=1001, need_gzip=False, need_encrypt=False
            )

            res_proto = UpdateClientInfoResIdl_pb2.UpdateClientInfoResIdl()
            res_proto.ParseFromString(await resp.read(timeout=5))
            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

        return True

    async def get_tbs(self) -> str:
        """
        获取贴吧反csrf校验码tbs

        Returns:
            str: 贴吧反csrf校验码tbs
        """

        if not self._tbs:
            await self.login()

        return self._tbs

    async def get_self_info(self) -> BasicUserInfo:
        """
        获取本账号信息

        Returns:
            BasicUserInfo: 简略版用户信息 仅保证包含user_name/portrait/user_id
        """

        if self._user is None:
            await self.login()

        return self._user

    async def login(self) -> bool:
        """
        登录并获取tbs和当前账号的简略版用户信息

        Returns:
            bool: True成功 False失败
        """

        payload = [
            ('_client_version', self.latest_version),
            ('bdusstoken', self.BDUSS),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/s/login"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            user_dict = res_json['user']
            user_proto = ParseDict(user_dict, User_pb2.User(), ignore_unknown_fields=True)
            self._user = BasicUserInfo(_raw_data=user_proto)
            self._tbs = res_json['anti']['tbs']

        except Exception as err:
            LOG.warning(err)
            self._user = BasicUserInfo()
            self._tbs = ""
            return False

        return True

    async def get_fid(self, fname: str) -> int:
        """
        通过贴吧名获取forum_id

        Args:
            fname (str): 贴吧名

        Returns:
            int: 该贴吧的forum_id
        """

        if fid := self._fname2fid.get(fname, 0):
            return fid

        try:
            async with self.session_web.get(
                yarl.URL.build(scheme="http", host="tieba.baidu.com", path="/f/commit/share/fnameShareApi"),
                allow_redirects=False,
                params={'fname': fname, 'ie': 'utf-8'},
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['no']):
                raise TiebaServerError(res_json['error'])

            if not (fid := int(res_json['data']['fid'])):
                raise TiebaServerError("fid is 0")

        except Exception as err:
            LOG.warning(f"{err}. fname={fname}")
            fid = 0

        self._add_forum_cache(fname, fid)

        return fid

    async def get_fname(self, fid: int) -> str:
        """
        通过forum_id获取贴吧名

        Args:
            fid (int): forum_id

        Returns:
            str: 该贴吧的贴吧名
        """

        if fname := self._fid2fname.get(fid, ''):
            return fname

        fname = (await self.get_forum_detail(fid)).fname

        self._add_forum_cache(fname, fid)

        return fname

    def _add_forum_cache(self, fname: str, fid: int) -> None:
        """
        将贴吧名与贴吧id的映射关系添加到缓存

        Args:
            fname (str): 贴吧名
            fid (int): 贴吧id
        """

        self._fname2fid[fname] = fid
        self._fid2fname[fid] = fname

    async def get_user_info(self, _id: Union[str, int]) -> UserInfo:
        """
        补全完整版用户信息

        Args:
            _id (str | int): 待补全用户的id user_id/user_name/portrait

        Returns:
            UserInfo: 完整版用户信息
        """

        user = UserInfo(_id)
        if user.user_id:
            return await self._user_id2user_info(user)
        elif user.portrait:
            user, _ = await self.get_homepage(user.portrait, with_threads=False)
            return user
        elif user.user_name:
            user = await self._user_name2basic_user_info(user)
            user, _ = await self.get_homepage(user.portrait, with_threads=False)
            return user
        else:
            LOG.warning("Null input")
            return user

    async def get_basic_user_info(self, _id: Union[str, int]) -> BasicUserInfo:
        """
        补全简略版用户信息

        Args:
            _id (str | int): 待补全用户的id user_id/user_name/portrait

        Returns:
            BasicUserInfo: 简略版用户信息 仅保证包含user_name/portrait/user_id
        """

        user = BasicUserInfo(_id)
        if user.user_id:
            return await self._user_id2basic_user_info(user)
        elif user.user_name:
            return await self._user_name2basic_user_info(user)
        elif user.portrait:
            user, _ = await self.get_homepage(user.portrait, with_threads=False)
            return user
        else:
            LOG.warning("Null input")
            return user

    async def _id2user_info(self, user: UserInfo) -> UserInfo:
        """
        通过用户名或旧版昵称或portrait补全完整版用户信息

        Args:
            user (UserInfo): 待补全的用户信息

        Returns:
            UserInfo: 完整版用户信息 但不含user_id

        Note:
            这是一个https接口 可能引入额外的性能开销
            2022.08.30 服务端不再返回user_id字段 请谨慎使用
        """

        try:
            async with self.session_web.get(
                yarl.URL.build(scheme="https", host="tieba.baidu.com", path="/home/get/panel"),
                allow_redirects=False,
                params={
                    'id': user.portrait,
                    'un': user.user_name or user.nick_name,
                },
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['no']):
                raise TiebaServerError(res_json['error'])

            user_dict: dict = res_json['data']

            _sex = user_dict['sex']
            if _sex == 'male':
                gender = 1
            elif _sex == 'female':
                gender = 2
            else:
                gender = 0

            # user.user_id = user_dict['id']
            user.user_name = user_dict['name']
            user.portrait = user_dict['portrait']
            user.nick_name = user_dict['show_nickname']

            user.gender = gender
            user.age = float(tb_age) if (tb_age := user_dict['tb_age']) != '-' else 0.0

            def tb_num2int(tb_num: str) -> int:
                """
                将贴吧数字字符串转为int
                可能会以xx万作为单位

                Args:
                    tb_num (str): 贴吧数字字符串

                Returns:
                    int: 对应数字
                """

                if isinstance(tb_num, str):
                    return int(float(tb_num.removesuffix('万')) * 1e4)
                else:
                    return tb_num

            user.post_num = tb_num2int(user_dict['post_num'])
            user.fan_num = tb_num2int(user_dict['followed_count'])

            user.is_vip = bool(int(vip_dict['v_status'])) if (vip_dict := user_dict['vipInfo']) else False

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
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

        try:
            async with self.session_web.get(
                yarl.URL.build(scheme="http", host="tieba.baidu.com", path="/i/sys/user_json"),
                allow_redirects=False,
                params={
                    'un': user.user_name,
                    'ie': 'utf-8',
                },
            ) as resp:
                text = await resp.text(encoding='utf-8', errors='ignore')

            if not text:
                raise TiebaServerError("empty response")
            res_json = json.loads(text)

            user_dict = res_json['creator']
            user.user_id = user_dict['id']
            user.portrait = user_dict['portrait']

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
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

        req_proto = GetUserInfoReqIdl_pb2.GetUserInfoReqIdl()
        req_proto.data.user_id = user.user_id

        try:
            async with self.session_app_proto.post(
                yarl.URL.build(path="/c/u/user/getuserinfo", query_string="cmd=303024"),
                data=self.pack_proto_bytes(req_proto.SerializeToString()),
            ) as resp:
                res_proto = GetUserInfoResIdl_pb2.GetUserInfoResIdl()
                res_proto.ParseFromString(await resp.content.read())

            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

            user_proto = res_proto.data.user
            user = UserInfo(_raw_data=user_proto)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
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
            async with self.session_web.get(
                yarl.URL.build(scheme="http", host="tieba.baidu.com", path="/im/pcmsg/query/getUserInfo"),
                allow_redirects=False,
                params={'chatUid': user.user_id},
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['errno']):
                raise TiebaServerError(res_json['errmsg'])

            user_dict = res_json['chatUser']
            user._user_name = user_dict['uname']
            user.portrait = user_dict['portrait']

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            user = BasicUserInfo()

        return user

    async def tieba_uid2user_info(self, tieba_uid: int) -> UserInfo:
        """
        通过tieba_uid补全用户信息

        Args:
            tieba_uid (int): 新版tieba_uid 请注意与旧版user_id的区别

        Returns:
            UserInfo: 完整版用户信息
        """

        req_proto = GetUserByTiebaUidReqIdl_pb2.GetUserByTiebaUidReqIdl()
        req_proto.data.tieba_uid = str(tieba_uid)

        try:
            async with self.session_app_proto.post(
                yarl.URL.build(path="/c/u/user/getUserByTiebaUid", query_string="cmd=309702"),
                data=self.pack_proto_bytes(req_proto.SerializeToString()),
            ) as resp:
                res_proto = GetUserByTiebaUidResIdl_pb2.GetUserByTiebaUidResIdl()
                res_proto.ParseFromString(await resp.content.read())

            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

            user_proto = res_proto.data.user
            user = UserInfo(_raw_data=user_proto)

        except Exception as err:
            LOG.warning(f"{err}. tieba_uid={tieba_uid}")
            user = UserInfo()

        return user

    async def get_threads(
        self,
        fname_or_fid: Union[str, int],
        /,
        pn: int = 1,
        *,
        rn: int = 30,
        sort: int = 5,
        is_good: bool = False,
    ) -> Threads:
        """
        获取首页帖子

        Args:
            fname_or_fid (str | int): 贴吧的贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30.
            sort (int, optional): 排序方式 对于有热门分区的贴吧0是热门排序1是按发布时间2报错34都是热门排序>=5是按回复时间
                对于无热门分区的贴吧0是按回复时间1是按发布时间2报错>=3是按回复时间. Defaults to 5.
            is_good (bool, optional): True为获取精品区帖子 False为获取普通区帖子. Defaults to False.

        Returns:
            Threads: 帖子列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        req_proto = FrsPageReqIdl_pb2.FrsPageReqIdl()
        req_proto.data.common._client_type = 2
        req_proto.data.common._client_version = self.latest_version
        req_proto.data.fname = fname
        req_proto.data.pn = pn
        req_proto.data.rn = rn if rn > 0 else 1
        req_proto.data.is_good = is_good
        req_proto.data.sort = sort

        try:
            async with self.session_app_proto.post(
                yarl.URL.build(path="/c/f/frs/page", query_string="cmd=301001"),
                data=self.pack_proto_bytes(req_proto.SerializeToString()),
            ) as resp:
                res_proto = FrsPageResIdl_pb2.FrsPageResIdl()
                res_proto.ParseFromString(await resp.content.read())

            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

            threads = Threads(res_proto.data)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname}")
            threads = Threads()

        return threads

    async def get_posts(
        self,
        tid: int,
        /,
        pn: int = 1,
        *,
        rn: int = 30,
        sort: int = 0,
        only_thread_author: bool = False,
        with_comments: bool = False,
        comment_sort_by_agree: bool = True,
        comment_rn: int = 10,
        is_fold: bool = False,
    ) -> Posts:
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
            is_fold (bool, optional): 是否请求被折叠的回复. Defaults to False.

        Returns:
            Posts: 回复列表
        """

        req_proto = PbPageReqIdl_pb2.PbPageReqIdl()
        req_proto.data.common._client_version = self.latest_version
        req_proto.data.tid = tid
        req_proto.data.pn = pn
        req_proto.data.rn = rn if rn > 1 else 2
        req_proto.data.sort = sort
        req_proto.data.only_thread_author = only_thread_author
        req_proto.data.is_fold = is_fold
        if with_comments:
            req_proto.data.with_comments = with_comments
            req_proto.data.comment_sort_by_agree = comment_sort_by_agree
            req_proto.data.comment_rn = comment_rn

        try:
            async with self.session_app_proto.post(
                yarl.URL.build(path="/c/f/pb/page", query_string="cmd=302001"),
                data=self.pack_proto_bytes(req_proto.SerializeToString()),
            ) as resp:
                res_proto = PbPageResIdl_pb2.PbPageResIdl()
                res_proto.ParseFromString(await resp.content.read())

            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

            posts = Posts(res_proto.data)

        except Exception as err:
            LOG.warning(f"{err}. tid={tid}")
            posts = Posts()

        return posts

    async def get_comments(
        self,
        tid: int,
        pid: int,
        /,
        pn: int = 1,
        *,
        is_floor: bool = False,
    ) -> Comments:
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

        req_proto = PbFloorReqIdl_pb2.PbFloorReqIdl()
        req_proto.data.common._client_version = self.latest_version
        req_proto.data.tid = tid
        if is_floor:
            req_proto.data.spid = pid
        else:
            req_proto.data.pid = pid
        req_proto.data.pn = pn

        try:
            async with self.session_app_proto.post(
                yarl.URL.build(path="/c/f/pb/floor", query_string="cmd=302002"),
                data=self.pack_proto_bytes(req_proto.SerializeToString()),
            ) as resp:
                res_proto = PbFloorResIdl_pb2.PbFloorResIdl()
                res_proto.ParseFromString(await resp.content.read())

            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

            comments = Comments(res_proto.data)

        except Exception as err:
            LOG.warning(f"{err}. tid={tid} pid={pid}")
            comments = Comments()

        return comments

    async def search_post(
        self,
        fname_or_fid: Union[str, int],
        query: str,
        /,
        pn: int = 1,
        *,
        rn: int = 30,
        query_type: int = 0,
        only_thread: bool = False,
    ) -> Searches:
        """
        贴吧搜索

        Args:
            fname_or_fid (str | int): 查询的贴吧名或fid 优先贴吧名
            query (str): 查询文本
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30.
            query_type (int, optional): 查询模式 0为全部搜索结果并且app似乎不提供这一模式 1为app时间倒序 2为app相关性排序. Defaults to 0.
            only_thread (bool, optional): 是否仅查询主题帖. Defaults to False.

        Returns:
            Searches: 搜索结果列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        payload = [
            ('_client_version', self.latest_version),
            ('kw', fname),
            ('only_thread', int(only_thread)),
            ('pn', pn),
            ('rn', rn),
            ('sm', query_type),
            ('word', query),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/s/searchpost"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', loads=JSON_DECODE_FUNC, content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            searches = Searches(res_json)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname}")
            searches = Searches()

        return searches

    async def get_forum_detail(self, fname_or_fid: Union[str, int]) -> Forum:
        """
        通过forum_id获取贴吧信息

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            Forum: 贴吧信息
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        payload = [
            ('_client_version', self.latest_version),
            ('forum_id', fid),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/f/forum/getforumdetail"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            forum_dict: Dict[str, str] = res_json['forum_info']
            forum_dict['thread_num'] = forum_dict.pop('thread_count')

            res = Forum(
                ParseDict(
                    forum_dict,
                    GetDislikeListResIdl_pb2.GetDislikeListResIdl.DataRes.ForumList(),
                    ignore_unknown_fields=True,
                )
            )

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid}")
            res = Forum()

        return res

    async def get_bawu_info(self, fname_or_fid: Union[str, int]) -> Dict[str, List[BasicUserInfo]]:
        """
        获取吧务信息

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            dict[str, list[BasicUserInfo]]: {吧务类型: list[吧务基本用户信息]}
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        req_proto = GetBawuInfoReqIdl_pb2.GetBawuInfoReqIdl()
        req_proto.data.common._client_version = self.latest_version
        req_proto.data.fid = fid

        try:
            async with self.session_app_proto.post(
                yarl.URL.build(path="/c/f/forum/getBawuInfo", query_string="cmd=301007"),
                data=self.pack_proto_bytes(req_proto.SerializeToString()),
            ) as resp:
                res_proto = GetBawuInfoResIdl_pb2.GetBawuInfoResIdl()
                res_proto.ParseFromString(await resp.content.read())

            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

            roledes_protos = res_proto.data.bawu_team_info.bawu_team_list
            bawu_dict = {
                roledes_proto.role_name: [
                    BasicUserInfo(_raw_data=roleinfo_proto) for roleinfo_proto in roledes_proto.role_info
                ]
                for roledes_proto in roledes_protos
            }

        except Exception as err:
            LOG.warning(err)
            bawu_dict = {}

        return bawu_dict

    async def get_tab_map(self, fname_or_fid: Union[str, int]) -> Dict[str, int]:
        """
        获取分区名到分区id的映射字典

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先贴吧名

        Returns:
            dict[str, int]: {分区名:分区id}
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        req_proto = SearchPostForumReqIdl_pb2.SearchPostForumReqIdl()
        req_proto.data.common.BDUSS = self.BDUSS
        req_proto.data.common._client_version = self.latest_version
        req_proto.data.fname = fname

        try:
            async with self.session_app_proto.post(
                yarl.URL.build(path="/c/f/forum/searchPostForum", query_string="cmd=309466"),
                data=self.pack_proto_bytes(req_proto.SerializeToString()),
            ) as resp:
                res_proto = SearchPostForumResIdl_pb2.SearchPostForumResIdl()
                res_proto.ParseFromString(await resp.content.read())

            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

            tab_map = {tab_proto.tab_name: tab_proto.tab_id for tab_proto in res_proto.data.exact_match.tab_info}

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid}")
            tab_map = {}

        return tab_map

    async def get_rank_users(self, fname_or_fid: Union[str, int], /, pn: int = 1) -> RankUsers:
        """
        获取pn页的等级排行榜用户列表

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            RankUsers: 等级排行榜用户列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        try:
            async with self.session_web.get(
                yarl.URL.build(scheme="https", host="tieba.baidu.com", path="/f/like/furank"),
                allow_redirects=False,
                params={
                    'kw': fname,
                    'pn': pn,
                    'ie': 'utf-8',
                },
            ) as resp:
                soup = bs4.BeautifulSoup(await resp.text(), 'lxml')

            rank_users = RankUsers(soup)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname}")
            rank_users = RankUsers()

        return rank_users

    async def get_member_users(self, fname_or_fid: Union[str, int], /, pn: int = 1) -> MemberUsers:
        """
        获取pn页的最新关注用户列表

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            MemberUsers: 最新关注用户列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        try:
            async with self.session_web.get(
                yarl.URL.build(scheme="https", host="tieba.baidu.com", path="/bawu2/platform/listMemberInfo"),
                allow_redirects=False,
                params={
                    'word': fname,
                    'pn': pn,
                    'ie': 'utf-8',
                },
            ) as resp:
                soup = bs4.BeautifulSoup(await resp.text(), 'lxml')

            member_users = MemberUsers(soup)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname}")
            member_users = MemberUsers()

        return member_users

    async def get_square_forums(self, class_name: str, /, pn: int = 1, *, rn: int = 20) -> SquareForums:
        """
        获取吧广场列表

        Args:
            class_name (str): 类别名
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 20.

        Returns:
            SquareForums: 吧广场列表
        """

        req_proto = GetForumSquareReqIdl_pb2.GetForumSquareReqIdl()
        req_proto.data.common.BDUSS = self.BDUSS
        req_proto.data.common._client_version = self.latest_version
        req_proto.data.class_name = class_name
        req_proto.data.pn = pn
        req_proto.data.rn = rn

        try:
            async with self.session_app_proto.post(
                yarl.URL.build(path="/c/f/forum/getForumSquare", query_string="cmd=309653"),
                data=self.pack_proto_bytes(req_proto.SerializeToString()),
            ) as resp:
                res_proto = GetForumSquareResIdl_pb2.GetForumSquareResIdl()
                res_proto.ParseFromString(await resp.content.read())

            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

            square_forums = SquareForums(res_proto.data)

        except Exception as err:
            LOG.warning(err)
            square_forums = SquareForums()

        return square_forums

    async def get_homepage(
        self, _id: Union[str, int], *, with_threads: bool = True
    ) -> Tuple[UserInfo, List[NewThread]]:
        """
        获取用户个人页信息

        Args:
            _id (str | int): 待获取用户的id user_id/user_name/portrait 优先user_id次优先portrait
            with_threads (bool, optional): True则同时请求主页帖子列表 False则返回的threads为空. Defaults to True.

        Returns:
            tuple[UserInfo, list[NewThread]]: 用户信息, list[帖子信息]
        """

        if not (BasicUserInfo.is_user_id(_id) or BasicUserInfo.is_portrait(_id)):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        req_proto = ProfileReqIdl_pb2.ProfileReqIdl()
        req_proto.data.common._client_version = self.latest_version
        if user.user_id:
            req_proto.data.friend_uid = user.user_id
        else:
            req_proto.data.friend_uid_portrait = user.portrait
        if with_threads:
            req_proto.data.need_post_count = 1
            req_proto.data.common._client_type = 2
        req_proto.data.pn = 1
        req_proto.data.rn = 20
        # req_proto.data.uid = (await self.get_self_info()).user_id  # 用该字段检查共同关注的吧

        try:
            async with self.session_app_proto.post(
                yarl.URL.build(path="/c/u/user/profile", query_string="cmd=303012"),
                data=self.pack_proto_bytes(req_proto.SerializeToString()),
            ) as resp:
                res_proto = ProfileResIdl_pb2.ProfileResIdl()
                res_proto.ParseFromString(await resp.content.read())

            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

            user = UserInfo(_raw_data=res_proto.data.user)
            threads = [NewThread(thread_proto) for thread_proto in res_proto.data.post_list]
            for thread in threads:
                thread._user = user

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            user = UserInfo()
            threads = []

        return user, threads

    async def get_statistics(self, fname_or_fid: Union[str, int]) -> Dict[str, List[int]]:
        """
        获取吧务后台中最近29天的统计数据

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            dict[str, list[int]]: {字段名:按时间顺序排列的统计数据}
            {'view': 浏览量,
             'thread': 主题帖数,
             'new_member': 新增关注数,
             'post': 回复数,
             'sign_ratio': 签到率,
             'average_time': 人均浏览时长,
             'average_times': 人均进吧次数,
             'recommend': 首页推荐数}
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('_client_version', self.latest_version),
            ('forum_id', fid),
        ]

        field_names = [
            'view',
            'thread',
            'new_member',
            'post',
            'sign_ratio',
            'average_time',
            'average_times',
            'recommend',
        ]
        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/f/forum/getforumdata"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            data = res_json['data']
            stat = {
                field_name: [int(item['value']) for item in reversed(data_i['group'][1]['values'])]
                for field_name, data_i in zip(field_names, data)
            }

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid}")
            stat = {field_name: [] for field_name in field_names}

        return stat

    async def get_follow_forums(self, _id: Union[str, int], /, pn: int = 1, *, rn: int = 50) -> FollowForums:
        """
        获取用户关注贴吧列表

        Args:
            _id (str | int): 待获取用户的id user_id/user_name/portrait 优先user_id
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 50.

        Returns:
            FollowForums: 用户关注贴吧列表
        """

        if not BasicUserInfo.is_user_id(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('_client_version', self.latest_version),
            ('friend_uid', user.user_id),
            ('page_no', pn),
            ('page_size', rn),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/f/forum/like"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            follow_forums = FollowForums(res_json)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            follow_forums = FollowForums()

        return follow_forums

    async def get_recom_status(self, fname_or_fid: Union[str, int]) -> Tuple[int, int]:
        """
        获取大吧主推荐功能的月度配额状态

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            tuple[int, int]: 本月总推荐配额, 本月已使用的推荐配额
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('_client_version', self.latest_version),
            ('forum_id', fid),
            ('pn', '1'),
            ('rn', '0'),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/f/bawu/getRecomThreadList"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            total_recom_num = int(res_json['total_recommend_num'])
            used_recom_num = int(res_json['used_recommend_num'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid}")
            total_recom_num = 0
            used_recom_num = 0

        return total_recom_num, used_recom_num

    async def get_recom_threads(self, fname_or_fid: Union[str, int], /, pn: int = 1, *, rn: int = 30) -> RecomThreads:
        """
        获取pn页的大吧主推荐帖列表

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30.

        Returns:
            RecomThreads: 大吧主推荐帖列表
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('_client_version', self.latest_version),
            ('forum_id', fid),
            ('pn', pn),
            ('rn', rn),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/f/bawu/getRecomThreadHistory"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', loads=JSON_DECODE_FUNC, content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            recom_threads = RecomThreads(res_json)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid}")
            recom_threads = RecomThreads()

        return recom_threads

    async def block(
        self,
        fname_or_fid: Union[str, int],
        /,
        _id: Union[str, int],
        *,
        day: Literal[1, 3, 10] = 1,
        reason: str = '',
    ) -> bool:
        """
        封禁用户

        Args:
            fname_or_fid (str | int): 所在贴吧的贴吧名或fid
            _id (str | int): 待封禁用户的id user_id/user_name/portrait 优先portrait
            day (Literal[1, 3, 10], optional): 封禁天数. Defaults to 1.
            reason (str, optional): 封禁理由. Defaults to ''.

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        if not BasicUserInfo.is_portrait(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('day', day),
            ('fid', fid),
            ('ntn', 'banid'),
            ('portrait', user.portrait),
            ('reason', reason),
            ('tbs', await self.get_tbs()),
            ('word', fname),
            ('z', '6'),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/c/bawu/commitprison"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} user={user} day={day}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} user={user} day={day}")
        return True

    async def unblock(self, fname_or_fid: Union[str, int], /, _id: Union[str, int]) -> bool:
        """
        解封用户

        Args:
            fname_or_fid (str | int): 所在贴吧的贴吧名或fid
            _id (str | int): 待解封用户的id user_id/user_name/portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        if not BasicUserInfo.is_user_id(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = [
            ('fn', fname),
            ('fid', fid),
            ('block_un', ' '),
            ('block_uid', user.user_id),
            ('tbs', await self.get_tbs()),
        ]

        try:
            async with self.session_web.post(
                yarl.URL.build(scheme="https", host="tieba.baidu.com", path="/mo/q/bawublockclear"),
                data=payload,
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['no']):
                raise TiebaServerError(res_json['error'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname} user={user}")
            return False

        LOG.info(f"Succeeded. forum={fname} user={user}")
        return True

    async def hide_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        屏蔽主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待屏蔽的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        try:
            await self._del_or_hide_thread(fname_or_fid, tid, is_hide=True)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def del_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        删除主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待删除的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        try:
            await self._del_or_hide_thread(fname_or_fid, tid, is_hide=False)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def _del_or_hide_thread(self, fname_or_fid: Union[str, int], /, tid: int, *, is_hide: bool = False) -> None:
        """
        主题帖删除/屏蔽相关操作

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待删除/屏蔽的主题帖tid
            is_hide (bool, optional): True则屏蔽帖 False则删除帖. Defaults to False.

        Raises:
            RuntimeError: 网络请求失败或服务端返回错误
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('fid', fid),
            ('is_frs_mask', int(is_hide)),
            ('tbs', await self.get_tbs()),
            ('z', tid),
        ]

        async with self.session_app.post(
            yarl.URL.build(path="/c/c/bawu/delthread"),
            data=self.pack_form(payload),
        ) as resp:
            res_json: dict = await resp.json(encoding='utf-8', content_type=None)

        if int(res_json['error_code']):
            raise TiebaServerError(res_json['error_msg'])

    async def del_threads(self, fname_or_fid: Union[str, int], /, tids: List[int], *, block: bool = False) -> bool:
        """
        批量删除主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tids (list[int]): 待删除的主题帖tid列表
            block (bool, optional): 是否同时封一天. Defaults to False.

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('forum_id', fid),
            ('tbs', await self.get_tbs()),
            ('thread_ids', ','.join(map(str, tids))),
            ('type', 2 if block else 1),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/c/bawu/multiDelThread"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])
            if res_json['info']['ret_type']:
                raise TiebaServerError(res_json['info']['text'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tids={tids}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tids={tids}")
        return True

    async def del_post(self, fname_or_fid: Union[str, int], /, pid: int) -> bool:
        """
        删除回复

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            pid (int): 待删除的回复pid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('fid', fid),
            ('pid', pid),
            ('tbs', await self.get_tbs()),
            ('z', 2),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/c/bawu/delpost"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} pid={pid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} pid={pid}")
        return True

    async def del_posts(self, fname_or_fid: Union[str, int], /, pids: List[int], *, block: bool = False) -> bool:
        """
        批量删除回复

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            pids (list[int]): 待删除的回复pid列表
            block (bool, optional): 是否同时封一天. Defaults to False.

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('forum_id', fid),
            ('post_ids', ','.join(map(str, pids))),
            ('tbs', await self.get_tbs()),
            ('thread_id', 2),
            ('type', 2 if block else 1),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/c/bawu/multiDelPost"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])
            if res_json['info']['ret_type']:
                raise TiebaServerError(res_json['info']['text'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} pids={pids}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} pids={pids}")
        return True

    async def unhide_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        解除主题帖屏蔽

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int, optional): 待解除屏蔽的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        try:
            await self.recover(fname_or_fid, tid=tid, is_hide=True)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def recover_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        恢复主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int, optional): 待恢复的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        try:
            await self.recover(fname_or_fid, tid=tid, is_hide=False)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def recover_post(self, fname_or_fid: Union[str, int], /, pid: int) -> bool:
        """
        恢复主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            pid (int, optional): 待恢复的回复pid

        Returns:
            bool: True成功 False失败
        """

        try:
            await self.recover(fname_or_fid, pid=pid, is_hide=False)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} pid={pid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} pid={pid}")
        return True

    async def recover(
        self,
        fname_or_fid: Union[str, int],
        /,
        tid: int = 0,
        pid: int = 0,
        *,
        is_hide: bool = False,
    ) -> None:
        """
        帖子恢复相关操作

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int, optional): 待恢复的主题帖tid. Defaults to 0.
            pid (int, optional): 待恢复的回复pid. Defaults to 0.
            is_hide (bool, optional): True则取消屏蔽主题帖 False则恢复删帖. Defaults to False.

        Raises:
            RuntimeError: 网络请求失败或服务端返回错误
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        payload = [
            ('fn', fname),
            ('fid', fid),
            ('tid_list[]', tid),
            ('pid_list[]', pid),
            ('type_list[]', '1' if pid else '0'),
            ('is_frs_mask_list[]', int(is_hide)),
        ]

        async with self.session_web.post(
            yarl.URL.build(scheme="https", host="tieba.baidu.com", path="/mo/q/bawurecoverthread"),
            data=payload,
        ) as resp:
            res_json: dict = await resp.json(encoding='utf-8', content_type=None)

        if int(res_json['no']):
            raise TiebaServerError(res_json['error'])

    async def move(self, fname_or_fid: Union[str, int], /, tid: int, *, to_tab_id: int, from_tab_id: int = 0) -> bool:
        """
        将主题帖移动至另一分区

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待移动的主题帖tid
            to_tab_id (int): 目标分区id
            from_tab_id (int, optional): 来源分区id 默认为0即无分区. Defaults to 0.

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('_client_version', self.latest_version),
            ('forum_id', fid),
            ('tbs', await self.get_tbs()),
            ('threads', json.dumps([{'thread_id', tid, 'from_tab_id', from_tab_id, 'to_tab_id', to_tab_id}])),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/c/bawu/moveTabThread"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def recommend(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        大吧主首页推荐

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待推荐的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('forum_id', fid),
            ('thread_id', tid),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/c/bawu/pushRecomToPersonalized"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])
            if int(res_json['data']['is_push_success']) != 1:
                raise TiebaServerError(res_json['data']['msg'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def good(self, fname_or_fid: Union[str, int], /, tid: int, *, cname: str = '') -> bool:
        """
        加精主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待加精的主题帖tid
            cname (str, optional): 待添加的精华分区名称 默认为''即不分区. Defaults to ''.

        Returns:
            bool: True成功 False失败
        """

        try:
            cid = await self._get_cid(fname_or_fid, cname)
            await self._good(fname_or_fid, tid, cid=cid, is_set=True)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} cname={cname}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def ungood(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        撤精主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待撤精的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        try:
            await self._good(fname_or_fid, tid, is_set=False)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def _get_cid(self, fname_or_fid: Union[str, int], /, cname: str) -> int:
        """
        通过加精分区名获取加精分区id

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            cname (str): 加精分区名

        Returns:
            int: 加精分区id
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('word', fname),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/c/bawu/goodlist"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            cid = 0
            for item in res_json['cates']:
                if cname == item['class_name']:
                    cid = int(item['class_id'])
                    break

        except Exception as err:
            LOG.warning(f"{err}. forum={fname} cname={cname}")
            cid = 0

        return cid

    async def _good(self, fname_or_fid: Union[str, int], /, tid: int, *, cid: int = 0, is_set: bool = True) -> None:
        """
        主题帖加精相关操作

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待撤精的主题帖tid
            cid (int, optional): 将主题帖加到cid对应的精华分区 cid默认为0即不分区. Defaults to 0.
            is_set (bool, optional): 加精或取消加精 默认为True即加精. Defaults to True.

        Raises:
            RuntimeError: 网络请求失败或服务端返回错误
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('cid', cid),
            ('fid', fid),
            ('ntn', 'set' if is_set else None),
            ('tbs', await self.get_tbs()),
            ('word', fname),
            ('z', tid),
        ]

        async with self.session_app.post(
            yarl.URL.build(path="/c/c/bawu/commitgood"),
            data=self.pack_form(payload),
        ) as resp:
            res_json: dict = await resp.json(encoding='utf-8', content_type=None)

        if int(res_json['error_code']):
            raise TiebaServerError(res_json['error_msg'])

    async def top(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        置顶主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待置顶的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        try:
            await self._top(fname_or_fid, tid, is_set=True)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def untop(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        撤销置顶主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待撤销置顶的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        try:
            await self._top(fname_or_fid, tid, is_set=False)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def _top(self, fname_or_fid: Union[str, int], /, tid: int, *, is_set: bool = True) -> None:
        """
        主题帖置顶相关操作

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待撤销置顶的主题帖tid
            is_set (bool, optional): 置顶或撤销置顶 默认为True即置顶. Defaults to True.

        Raises:
            RuntimeError: 网络请求失败或服务端返回错误
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        payload = [
            ('BDUSS', self.BDUSS),
            ('fid', fid),
            ('ntn', 'set' if is_set else None),
            ('tbs', await self.get_tbs()),
            ('word', fname),
            ('z', tid),
        ]

        async with self.session_app.post(
            yarl.URL.build(path="/c/c/bawu/committop"),
            data=self.pack_form(payload),
        ) as resp:
            res_json: dict = await resp.json(encoding='utf-8', content_type=None)

        if int(res_json['error_code']):
            raise TiebaServerError(res_json['error_msg'])

    async def get_recovers(self, fname_or_fid: Union[str, int], /, pn: int = 1, name: str = '') -> Recovers:
        """
        获取pn页的待恢复帖子列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid
            pn (int, optional): 页码. Defaults to 1.
            name (str, optional): 通过被删帖作者的用户名/昵称查询 默认为空即查询全部. Defaults to ''.

        Returns:
            Recovers: 待恢复帖子列表
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        try:
            async with self.session_web.get(
                yarl.URL.build(scheme="https", host="tieba.baidu.com", path="/mo/q/bawurecover"),
                allow_redirects=False,
                params={
                    'fn': fname,
                    'fid': fid,
                    'word': name,
                    'is_ajax': '1',
                    'pn': pn,
                },
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['no']):
                raise TiebaServerError(res_json['error'])

            recovers = Recovers(res_json)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname}")
            recovers = Recovers()

        return recovers

    async def get_blacklist_users(self, fname_or_fid: Union[str, int], /, pn: int = 1) -> BlacklistUsers:
        """
        获取pn页的黑名单用户列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            BlacklistUsers: 黑名单用户列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        try:
            async with self.session_web.get(
                yarl.URL.build(scheme="https", host="tieba.baidu.com", path="/bawu2/platform/listBlackUser"),
                allow_redirects=False,
                params={
                    'word': fname,
                    'pn': pn,
                },
            ) as resp:
                soup = bs4.BeautifulSoup(await resp.text(), 'lxml')

            blacklist_users = BlacklistUsers(soup)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname}")
            blacklist_users = BlacklistUsers()

        return blacklist_users

    async def blacklist_add(self, fname_or_fid: Union[str, int], /, _id: Union[str, int]) -> bool:
        """
        添加贴吧黑名单

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先贴吧名
            _id (str | int): 待加黑名单用户的id user_id/user_name/portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        if not BasicUserInfo.is_user_id(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = [
            ('tbs', await self.get_tbs()),
            ('user_id', user.user_id),
            ('word', fname),
            ('ie', 'utf-8'),
        ]

        try:
            async with self.session_web.post(
                yarl.URL.build(scheme="http", host="tieba.baidu.com", path="/bawu2/platform/addBlack"),
                data=payload,
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['errno']):
                raise TiebaServerError(res_json['errmsg'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname} user={user.user_id}")
            return False

        LOG.info(f"Succeeded. forum={fname} user={user.user_id}")
        return True

    async def blacklist_del(self, fname_or_fid: Union[str, int], /, _id: Union[str, int]) -> bool:
        """
        移出贴吧黑名单

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先贴吧名
            _id (str | int): 待解黑名单用户的id user_id/user_name/portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        if not BasicUserInfo.is_user_id(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = [
            ('word', fname),
            ('tbs', await self.get_tbs()),
            ('list[]', user.user_id),
            ('ie', 'utf-8'),
        ]

        try:
            async with self.session_web.post(
                yarl.URL.build(scheme="http", host="tieba.baidu.com", path="/bawu2/platform/cancelBlack"),
                data=payload,
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['errno']):
                raise TiebaServerError(res_json['errmsg'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname} user={user.user_id}")
            return False

        LOG.info(f"Succeeded. forum={fname} user={user.user_id}")
        return True

    async def get_unblock_appeals(self, fname_or_fid: Union[str, int], /, pn: int = 1, *, rn: int = 5) -> Appeals:
        """
        获取申诉请求列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 5.

        Returns:
            Appeals: 申诉请求列表
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        params = {
            'fn': fname,
            'fid': fid,
            'pn': pn,
            'rn': rn,
            'tbs': await self.get_tbs(),
        }

        try:
            async with self.session_web.get(
                yarl.URL.build(scheme="https", host="tieba.baidu.com", path="/mo/q/getBawuAppealList"),
                allow_redirects=False,
                params=params,
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['no']):
                raise TiebaServerError(res_json['error'])

            appeals = Appeals(res_json)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname}")
            appeals = Appeals()

        return appeals

    async def handle_unblock_appeals(
        self, fname_or_fid: Union[str, int], /, appeal_ids: List[int], *, refuse: bool = True
    ) -> bool:
        """
        拒绝或通过解封申诉

        Args:
            fname_or_fid (str | int): 申诉所在贴吧的贴吧名或fid
            appeal_ids (list[int]): 申诉请求的appeal_id列表
            refuse (bool, optional): True则拒绝申诉 False则接受申诉. Defaults to True.

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        payload = (
            [
                ('fn', fname),
                ('fid', fid),
            ]
            + [(f'appeal_list[{i}]', appeal_id) for i, appeal_id in enumerate(appeal_ids)]
            + [
                ('refuse_reason', '_'),
                ('status', '2' if refuse else '1'),
                ('tbs', await self.get_tbs()),
            ]
        )

        try:
            async with self.session_web.post(
                yarl.URL.build(scheme="https", host="tieba.baidu.com", path="/mo/q/multiAppealhandle"),
                data=payload,
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['no']):
                raise TiebaServerError(res_json['error'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname}")
            return False

        LOG.info(f"Succeeded. forum={fname}")
        return True

    async def get_image(self, img_url: str) -> "np.ndarray":
        """
        从链接获取静态图像

        Args:
            img_url (str): 图像链接

        Returns:
            np.ndarray: 图像
        """

        try:
            async with self.session_web.get(img_url, allow_redirects=False) as resp:
                if not resp.content_type.endswith(('jpeg', 'png', 'bmp'), 6):
                    raise ContentTypeError(f"Expect jpeg, png or bmp, got {resp.content_type}")
                content = await resp.content.read()

            image = cv.imdecode(np.frombuffer(content, np.uint8), cv.IMREAD_COLOR)
            if image is None:
                raise RuntimeError("Error with opencv.imdecode")

        except Exception as err:
            LOG.warning(f"{err}. url={img_url}")
            image = np.empty(0, dtype=np.uint8)

        return image

    async def get_portrait(self, _id: Union[str, int], /, size: Literal['s', 'm', 'l'] = 's') -> "np.ndarray":
        """
        获取用户头像

        Args:
            _id (str | int): 用户的id user_id/user_name/portrait 优先portrait
            size (Literal['s', 'm', 'l'], optional): 获取头像的大小 s为55x55 m为110x110 l为原图. Defaults to 's'.

        Returns:
            np.ndarray: 头像
        """

        if not BasicUserInfo.is_portrait(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        if size == 's':
            path = 'n'
        elif size == 'l':
            path = 'h'
        else:
            path = ''

        try:
            async with self.session_web.get(
                yarl.URL.build(
                    scheme="http", host="tb.himg.baidu.com", path=f"/sys/portrait{path}/item/{user.portrait}"
                ),
                allow_redirects=False,
            ) as resp:
                image = cv.imdecode(np.frombuffer(await resp.content.read(), np.uint8), cv.IMREAD_COLOR)

            if image is None:
                raise RuntimeError("error in opencv.imdecode")

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            image = np.empty(0, dtype=np.uint8)

        return image

    async def get_newmsg(self) -> Dict[str, bool]:
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

        payload = [
            ('BDUSS', self.BDUSS),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/s/msg"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            msg = {k: bool(int(v)) for k, v in res_json['message'].items()}

        except Exception as err:
            LOG.warning(err)
            msg = {
                'fans': False,
                'replyme': False,
                'atme': False,
                'agree': False,
                'pletter': False,
                'bookmark': False,
                'count': False,
            }

        return msg

    async def get_replys(self, pn: int = 1) -> Replys:
        """
        获取回复信息

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            Replys: 回复列表
        """

        req_proto = ReplyMeReqIdl_pb2.ReplyMeReqIdl()
        req_proto.data.common.BDUSS = self.BDUSS
        req_proto.data.common._client_version = self.latest_version
        req_proto.data.pn = str(pn)

        try:
            async with self.session_app_proto.post(
                yarl.URL.build(path="/c/u/feed/replyme", query_string="cmd=303007"),
                data=self.pack_proto_bytes(req_proto.SerializeToString()),
            ) as resp:
                res_proto = ReplyMeResIdl_pb2.ReplyMeResIdl()
                res_proto.ParseFromString(await resp.content.read())

            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

            replys = Replys(res_proto.data)

        except Exception as err:
            LOG.warning(err)
            replys = Replys()

        return replys

    async def get_ats(self, pn: int = 1) -> Ats:
        """
        获取@信息

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            Ats: at列表
        """

        payload = [
            ('BDUSS', self.BDUSS),
            ('_client_version', self.latest_version),
            ('pn', pn),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/u/feed/atme"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', loads=JSON_DECODE_FUNC, content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            ats = Ats(res_json)

        except Exception as err:
            LOG.warning(err)
            ats = Ats()

        return ats

    async def get_self_public_threads(self, pn: int = 1) -> List[NewThread]:
        """
        获取本人发布的公开状态的主题帖列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            list[NewThread]: 主题帖列表
        """

        user = await self.get_self_info()

        try:
            return await self._get_user_contents(user, pn, is_thread=True, public_only=True)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            return []

    async def get_self_threads(self, pn: int = 1) -> List[NewThread]:
        """
        获取本人发布的主题帖列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            list[NewThread]: 主题帖列表
        """

        user = await self.get_self_info()

        try:
            return await self._get_user_contents(user, pn, is_thread=True)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            return []

    async def get_self_posts(self, pn: int = 1) -> List[UserPosts]:
        """
        获取本人发布的回复列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            list[UserPosts]: 回复列表
        """

        user = await self.get_self_info()

        try:
            return await self._get_user_contents(user, pn, is_thread=False)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            return []

    async def get_user_threads(self, _id: Union[str, int], pn: int = 1) -> List[NewThread]:
        """
        获取用户发布的主题帖列表

        Args:
            _id (str | int): 待获取用户的id user_id/user_name/portrait 优先user_id
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            list[NewThread]: 主题帖列表
        """

        if not BasicUserInfo.is_user_id(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        try:
            return await self._get_user_contents(user, pn)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            return []

    async def _get_user_contents(
        self, user: BasicUserInfo, /, pn: int = 1, *, is_thread: bool = True, public_only: bool = False
    ) -> Union[List[NewThread], List[UserPosts]]:
        """
        获取用户发布的主题帖/回复列表

        Args:
            user (BasicUserInfo): 待获取用户的基本用户信息
            pn (int, optional): 页码. Defaults to 1.
            is_thread (bool, optional): 是否请求主题帖. Defaults to True.
            public_only (bool, optional): 是否仅获取公开帖. Defaults to False.

        Raises:
            RuntimeError: 网络请求失败或服务端返回错误

        Returns:
            list[NewThread] | list[UserPosts]: 主题帖/回复列表
        """

        req_proto = UserPostReqIdl_pb2.UserPostReqIdl()
        req_proto.data.common.BDUSS = self.BDUSS
        req_proto.data.common._client_version = self.latest_version
        req_proto.data.user_id = user.user_id
        req_proto.data.is_thread = is_thread
        req_proto.data.need_content = 1
        req_proto.data.pn = pn
        req_proto.data.is_view_card = 2 if public_only else 1

        async with self.session_app_proto.post(
            yarl.URL.build(path="/c/u/feed/userpost", query_string="cmd=303002"),
            data=self.pack_proto_bytes(req_proto.SerializeToString()),
        ) as resp:
            res_proto = UserPostResIdl_pb2.UserPostResIdl()
            res_proto.ParseFromString(await resp.content.read())

        if int(res_proto.error.errorno):
            raise TiebaServerError(res_proto.error.errmsg)

        res_data_proto = res_proto.data
        if is_thread:
            res_list = [NewThread(thread_proto) for thread_proto in res_data_proto.post_list]
            for thread in res_list:
                thread._user = user
        else:
            res_list = [UserPosts(posts_proto) for posts_proto in res_data_proto.post_list]
            for userposts in res_list:
                for userpost in userposts:
                    userpost._user = user

        return res_list

    async def get_fans(self, _id: Union[str, int, None] = None, /, pn: int = 1) -> Fans:
        """
        获取粉丝列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            _id (str | int | None): 待获取用户的id user_id/user_name/portrait 优先user_id
                默认为None即获取本账号信息. Defaults to None.

        Returns:
            Fans: 粉丝列表
        """

        if _id is None:
            user = await self.get_self_info()
        elif not BasicUserInfo.is_user_id(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('_client_version', self.latest_version),
            ('pn', pn),
            ('uid', user.user_id),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/u/fans/page"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', loads=JSON_DECODE_FUNC, content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            fans = Fans(res_json)

        except Exception as err:
            LOG.warning(err)
            fans = Fans()

        return fans

    async def get_follows(self, _id: Union[str, int, None] = None, /, pn: int = 1) -> Follows:
        """
        获取关注列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            _id (str | int | None): 待获取用户的id user_id/user_name/portrait 优先user_id
                默认为None即获取本账号信息. Defaults to None.

        Returns:
            Follows: 关注列表
        """

        if _id is None:
            user = await self.get_self_info()
        elif not BasicUserInfo.is_user_id(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('_client_version', self.latest_version),
            ('pn', pn),
            ('uid', user.user_id),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/u/follow/followList"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', loads=JSON_DECODE_FUNC, content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

            follows = Follows(res_json)

        except Exception as err:
            LOG.warning(err)
            follows = Follows()

        return follows

    async def get_self_follow_forums(self, pn: int = 1) -> SelfFollowForums:
        """
        获取本账号关注贴吧列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            SelfFollowForums: 本账号关注贴吧列表

        Note:
            本接口需要STOKEN
        """

        try:
            async with self.session_web.get(
                yarl.URL.build(scheme="https", host="tieba.baidu.com", path="/mg/o/getForumHome"),
                allow_redirects=False,
                params={
                    'pn': pn,
                    'rn': 200,
                },
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['errno']):
                raise TiebaServerError(res_json['errmsg'])

            self_follow_forums = SelfFollowForums(res_json)

        except Exception as err:
            LOG.warning(err)
            self_follow_forums = SelfFollowForums()

        return self_follow_forums

    async def get_dislike_forums(self, pn: int = 1, /, *, rn: int = 20) -> DislikeForums:
        """
        获取首页推荐屏蔽的贴吧列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 20.

        Returns:
            DislikeForums: 首页推荐屏蔽的贴吧列表
        """

        req_proto = GetDislikeListReqIdl_pb2.GetDislikeListReqIdl()
        req_proto.data.common.BDUSS = self.BDUSS
        req_proto.data.common._client_version = self.latest_version
        req_proto.data.pn = pn
        req_proto.data.rn = rn

        try:
            async with self.session_app_proto.post(
                yarl.URL.build(path="/c/u/user/getDislikeList", query_string="cmd=309692"),
                data=self.pack_proto_bytes(req_proto.SerializeToString()),
            ) as resp:
                res_proto = GetDislikeListResIdl_pb2.GetDislikeListResIdl()
                res_proto.ParseFromString(await resp.content.read())

            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)

            dislike_forums = DislikeForums(res_proto.data)

        except Exception as err:
            LOG.warning(err)
            dislike_forums = DislikeForums()

        return dislike_forums

    async def agree(self, tid: int, pid: int = 0) -> bool:
        """
        点赞主题帖或回复

        Args:
            tid (int): 待点赞的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待点赞的回复pid. Defaults to 0.

        Returns:
            bool: True成功 False失败

        Note:
            本接口仍处于测试阶段
            高频率调用会导致<发帖秒删>！请谨慎使用！恢复方法是刷回复永封后再申诉解封
        """

        try:
            await self._agree(tid, pid)

        except Exception as err:
            LOG.warning(f"{err}. tid={tid} pid={pid}")
            return False

        LOG.info(f"Succeeded. tid={tid} pid={pid}")
        return True

    async def unagree(self, tid: int, pid: int = 0) -> bool:
        """
        取消点赞主题帖或回复

        Args:
            tid (int): 待取消点赞的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待取消点赞的回复pid. Defaults to 0.

        Returns:
            bool: True成功 False失败
        """

        try:
            await self._agree(tid, pid, is_undo=True)

        except Exception as err:
            LOG.warning(f"{err}. tid={tid} pid={pid}")
            return False

        LOG.info(f"Succeeded. tid={tid} pid={pid}")
        return True

    async def disagree(self, tid: int, pid: int = 0) -> bool:
        """
        点踩主题帖或回复

        Args:
            tid (int): 待点踩的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待点踩的回复pid. Defaults to 0.

        Returns:
            bool: True成功 False失败
        """

        try:
            await self._agree(tid, pid, is_disagree=True)

        except Exception as err:
            LOG.warning(f"{err}. tid={tid} pid={pid}")
            return False

        LOG.info(f"Succeeded. tid={tid} pid={pid}")
        return True

    async def undisagree(self, tid: int, pid: int = 0) -> bool:
        """
        取消点踩主题帖或回复

        Args:
            tid (int): 待取消点踩的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待取消点踩的回复pid. Defaults to 0.

        Returns:
            bool: True成功 False失败
        """

        try:
            await self._agree(tid, pid, is_disagree=True, is_undo=True)

        except Exception as err:
            LOG.warning(f"{err}. tid={tid} pid={pid}")
            return False

        LOG.info(f"Succeeded. tid={tid} pid={pid}")
        return True

    async def _agree(self, tid: int, pid: int = 0, *, is_disagree: bool = False, is_undo: bool = False) -> None:
        """
        点赞点踩

        Args:
            tid (int): 待点赞点踩的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待点赞点踩的回复pid. Defaults to 0.
            is_disagree (bool, optional): 是否为点踩. Defaults to False.
            is_undo (bool, optional): 是否为取消. Defaults to False.

        Raises:
            RuntimeError: 网络请求失败或服务端返回错误
        """

        payload = [
            ('BDUSS', self.BDUSS),
            ('_client_version', self.latest_version),
            ('agree_type', 5 if is_disagree else 2),
            ('cuid', self.cuid_galaxy2),
            ('obj_type', 1 if pid else 3),
            ('op_type', int(is_undo)),
            ('post_id', pid),
            ('tbs', await self.get_tbs()),
            ('thread_id', tid),
        ]

        async with self.session_app.post(
            yarl.URL.build(path="/c/c/agree/opAgree"),
            data=self.pack_form(payload),
        ) as resp:
            res_json: dict = await resp.json(encoding='utf-8', content_type=None)

        if int(res_json['error_code']):
            raise TiebaServerError(res_json['error_msg'])

    async def remove_fan(self, _id: Union[str, int]):
        """
        移除粉丝

        Args:
            _id (str | int): 待移除粉丝的id user_id/user_name/portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        if not BasicUserInfo.is_user_id(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('fans_uid', user.user_id),
            ('tbs', await self.get_tbs()),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/c/user/removeFans"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            return False

        LOG.info(f"Succeeded. user={user}")
        return True

    async def follow_user(self, _id: Union[str, int]):
        """
        关注用户

        Args:
            _id (str | int): 待关注用户的id user_id/user_name/portrait 优先portrait

        Returns:
            bool: True成功 False失败
        """

        if not BasicUserInfo.is_portrait(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('portrait', user.portrait),
            ('tbs', await self.get_tbs()),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/c/user/follow"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            return False

        LOG.info(f"Succeeded. user={user}")
        return True

    async def unfollow_user(self, _id: Union[str, int]):
        """
        取关用户

        Args:
            _id (str | int): 待取关用户的id user_id/user_name/portrait 优先portrait

        Returns:
            bool: True成功 False失败
        """

        if not BasicUserInfo.is_portrait(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('portrait', user.portrait),
            ('tbs', await self.get_tbs()),
        ]

        try:
            async with self.session_app.post(
                yarl.URL.build(path="/c/c/user/unfollow"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            return False

        LOG.info(f"Succeeded. user={user}")
        return True

    async def follow_forum(self, fname_or_fid: Union[str, int]) -> bool:
        """
        关注贴吧

        Args:
            fname_or_fid (str | int): 要关注贴吧的贴吧名或fid 优先fid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        try:
            payload = [
                ('BDUSS', self.BDUSS),
                ('fid', fid),
                ('tbs', await self.get_tbs()),
            ]

            async with self.session_app.post(
                yarl.URL.build(path="/c/c/forum/like"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])
            if int(res_json['error']['errno']):
                raise TiebaServerError(res_json['error']['errmsg'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid}")
        return True

    async def unfollow_forum(self, fname_or_fid: Union[str, int]) -> bool:
        """
        取关贴吧

        Args:
            fname_or_fid (str | int): 要取关贴吧的贴吧名或fid 优先fid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        try:
            payload = [
                ('BDUSS', self.BDUSS),
                ('fid', fid),
                ('tbs', await self.get_tbs()),
            ]

            async with self.session_app.post(
                yarl.URL.build(path="/c/c/forum/unfavolike"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid}")
        return True

    async def dislike_forum(self, fname_or_fid: Union[str, int]) -> bool:
        """
        屏蔽贴吧 使其不再出现在首页推荐列表中

        Args:
            fname_or_fid (str | int): 待屏蔽贴吧的贴吧名或fid 优先fid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        try:
            payload = [
                ('BDUSS', self.BDUSS),
                ('_client_version', self.latest_version),
                (
                    'dislike',
                    json.dumps([{"tid": 1, "dislike_ids": 7, "fid": fid, "click_time": self.timestamp_ms}]),
                ),
                ('dislike_from', "homepage"),
            ]

            async with self.session_app.post(
                yarl.URL.build(path="/c/c/excellent/submitDislike"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid}")
        return True

    async def undislike_forum(self, fname_or_fid: Union[str, int]) -> bool:
        """
        解除贴吧的首页推荐屏蔽

        Args:
            fname_or_fid (str | int): 待屏蔽贴吧的贴吧名或fid 优先fid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        try:
            payload = [
                ('BDUSS', self.BDUSS),
                ('cuid', self.cuid),
                ('forum_id', fid),
            ]

            async with self.session_app.post(
                yarl.URL.build(path="/c/c/excellent/submitCancelDislike"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid}")
        return True

    async def set_privacy(self, fname_or_fid: Union[str, int], /, tid: int, pid: int, *, hide: bool = True) -> bool:
        """
        隐藏主题帖

        Args:
            fname_or_fid (str | int): 主题帖所在贴吧的贴吧名或fid 优先fid
            tid (int): 主题帖tid
            tid (int): 主题帖pid
            hide (bool, optional): True则设为隐藏 False则取消隐藏. Defaults to True.

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        try:
            payload = [
                ('BDUSS', self.BDUSS),
                ('forum_id', fid),
                ('is_hide', int(hide)),
                ('post_id', pid),
                ('thread_id', tid),
            ]

            async with self.session_app.post(
                yarl.URL.build(path="/c/c/thread/setPrivacy"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])

        except Exception as err:
            LOG.warning(f"{err}. tid={tid}")
            return False

        LOG.info(f"Succeeded. tid={tid}")
        return True

    async def sign_forum(self, fname_or_fid: Union[str, int]) -> bool:
        """
        单个贴吧签到

        Args:
            fname_or_fid (str | int): 要签到贴吧的贴吧名或fid 优先贴吧名

        Returns:
            bool: True表示不需要再尝试签到 False表示由于各种原因失败需要重签
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        error_code = 0
        try:
            payload = [
                ('BDUSS', self.BDUSS),
                ('_client_version', self.latest_version),
                ('kw', fname),
                ('tbs', await self.get_tbs()),
            ]

            async with self.session_app.post(
                yarl.URL.build(path="/c/c/forum/sign"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            error_code = int(res_json['error_code'])
            if error_code:
                raise TiebaServerError(res_json['error_msg'])
            if int(res_json['user_info']['sign_bonus_point']) == 0:
                raise TiebaServerError("sign_bonus_point is 0")

        except Exception as err:
            LOG.warning(f"{err}. forum={fname}")
            if error_code in [160002, 340006]:
                # 已经签过或吧被屏蔽
                return True
            return False

        LOG.info(f"Succeeded. forum={fname}")
        return True

    async def add_post(self, fname_or_fid: Union[str, int], /, tid: int, content: str) -> bool:
        """
        回复主题帖

        Args:
            fname_or_fid (str | int): 要回复的主题帖所在贴吧的贴吧名或fid
            tid (int): 要回复的主题帖的tid
            content (str): 回复内容

        Returns:
            bool: 回帖是否成功

        Note:
            本接口仍处于测试阶段
            高频率调用会导致<永久封禁屏蔽>！请谨慎使用！
            已通过的测试: cookie白板号(无头像无关注吧无发帖记录 2元/个) 通过异地阿里云ip出口以3分钟的发送间隔发15条回复不吞楼不封号
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        try:
            payload = [
                ('BDUSS', self.BDUSS),
                ('_client_id', self.client_id),
                ('_client_type', '2'),
                ('_client_version', self.post_version),
                ('_phone_imei', '000000000000000'),
                ('anonymous', '1'),
                ('apid', 'sw'),
                ('content', content),
                ('cuid', self.cuid),
                ('cuid_galaxy2', self.cuid_galaxy2),
                ('cuid_gid', ''),
                ('fid', fid),
                ('kw', fname),
                ('model', 'M2012K11AC'),
                ('net_type', '1'),
                ('new_vcode', '1'),
                ('post_from', '3'),
                ('reply_uid', 'null'),
                ('stoken', self.STOKEN),
                ('subapp_type', 'mini'),
                ('tbs', await self.get_tbs()),
                ('tid', tid),
                ('timestamp', self.timestamp_ms),
                ('v_fid', ''),
                ('v_fname', ''),
                ('vcode_tag', '12'),
            ]

            async with self.session_app.post(
                yarl.URL.build(path="/c/c/post/add"),
                data=self.pack_form(payload),
            ) as resp:
                res_json: dict = await resp.json(encoding='utf-8', content_type=None)

            if int(res_json['error_code']):
                raise TiebaServerError(res_json['error_msg'])
            if int(res_json['info']['need_vcode']):
                raise TiebaServerError("need verify code")

        except Exception as err:
            LOG.warning(f"{err}. forum={fname} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname} tid={tid}")
        return True

    async def send_msg(self, _id: Union[str, int], content: str) -> bool:
        """
        发送私信

        Args:
            _id (str | int): 待私信用户的id user_id/user_name/portrait 优先user_id
            content (str): 发送内容

        Returns:
            bool: True成功 False失败
        """

        if not BasicUserInfo.is_user_id(_id):
            user = await self.get_basic_user_info(_id)
        else:
            user = BasicUserInfo(_id)

        data_proto = CommitPersonalMsgReqIdl_pb2.CommitPersonalMsgReqIdl.DataReq()
        data_proto.toUid = user.user_id
        data_proto.content = content
        data_proto.msgType = 1
        req_proto = CommitPersonalMsgReqIdl_pb2.CommitPersonalMsgReqIdl()
        req_proto.data.CopyFrom(data_proto)

        try:
            await self._init_websocket()

            resp = await self.send_ws_bytes(req_proto.SerializeToString(), cmd=205001)

            res_proto = CommitPersonalMsgResIdl_pb2.CommitPersonalMsgResIdl()
            res_proto.ParseFromString(await resp.read(timeout=5))
            if int(res_proto.error.errorno):
                raise TiebaServerError(res_proto.error.errmsg)
            if int(res_proto.data.blockInfo.blockErrno):
                raise TiebaServerError(res_proto.data.blockInfo.blockErrmsg)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            return False

        LOG.info(f"Succeeded. user={user}")
        return True
