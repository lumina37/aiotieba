__all__ = ['Client']
import asyncio
import base64
import gzip
import hashlib
import json
import random
import time
import uuid
from typing import ClassVar, Dict, List, Literal, Optional, Tuple, Union

import httpcore
import httpx
import httpx_ws
import numpy as np
import wsproto
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

from .._config import CONFIG
from .._exception import TiebaServerError
from .._helper import JSON_DECODE_FUNC
from .._logger import LOG
from ..protobuf import (
    CommitPersonalMsgReqIdl_pb2,
    CommitPersonalMsgResIdl_pb2,
    GetDislikeListReqIdl_pb2,
    GetDislikeListResIdl_pb2,
    UpdateClientInfoReqIdl_pb2,
    UpdateClientInfoResIdl_pb2,
)
from .common.helper import pack_form_request, pack_proto_request, send_request
from .common.typedef import (
    Appeals,
    Ats,
    BlacklistUsers,
    Comments,
    DislikeForums,
    Fans,
    FollowForums,
    Follows,
    Forum,
    ForumInfoCache,
    Header,
    MemberUsers,
    NewThread,
    Posts,
    RankUsers,
    RecomThreads,
    Recovers,
    Replys,
    ReqUInfo,
    Searches,
    SelfFollowForums,
    SquareForums,
    Threads,
    UserInfo,
    UserPosts,
    WebsocketResponse,
)


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
        '_client_app',
        '_client_app_proto',
        '_client_web',
        '_client_ws',
        'websocket',
        '_ws_aes_chiper',
        '_ws_dispatcher',
    ]

    _use_env_proxy = True
    _timeout: ClassVar[httpx.Timeout] = httpx.Timeout(connect=3.0, read=12.0, write=8.0, pool=3.0)
    _limits: ClassVar[httpx.Limits] = httpx.Limits(
        max_connections=None, max_keepalive_connections=None, keepalive_expiry=10.0
    )

    latest_version: ClassVar[str] = "12.34.3.0"  # 这是目前的最新版本
    # no_fold_version: ClassVar[str] = "12.12.1.0"  # 这是最后一个回复列表不发生折叠的版本
    post_version: ClassVar[str] = "9.1.0.0"  # 发帖使用极速版

    def __init__(self, BDUSS_key: Optional[str] = None) -> None:
        self._BDUSS_key = BDUSS_key

        user_cfg: Dict[str, str] = CONFIG['User'].get(BDUSS_key, {})
        self.BDUSS = user_cfg.get('BDUSS', '')
        self.STOKEN = user_cfg.get('STOKEN', '')

        self._user = UserInfo()
        self._tbs: str = None
        self._client_id: str = None
        self._cuid: str = None
        self._cuid_galaxy2: str = None
        self._ws_password: bytes = None

        self._client_app: httpx.AsyncClient = None
        self._client_app_proto: httpx.AsyncClient = None
        self._client_web: httpx.AsyncClient = None
        self._client_ws: httpx.AsyncClient = None
        self.websocket: httpx_ws.AsyncWebSocketSession = None
        self._ws_aes_chiper = None
        self._ws_dispatcher: asyncio.Task = None

    async def __aenter__(self) -> "Client":
        await self.client_web.__aenter__()
        return self

    async def close(self) -> None:
        if self._ws_dispatcher is not None:
            self._ws_dispatcher.cancel()

        if self.is_ws_aviliable:
            await self.websocket.close()

        if self._client_app is not None:
            await self._client_app.aclose()
        if self._client_app_proto is not None:
            await self._client_app_proto.aclose()
        if self._client_web is not None:
            await self._client_web.aclose()
        if self._client_ws is not None:
            await self._client_ws.aclose()

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
            self._cuid = f"baidutiebaapp{uuid.uuid4()}"
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
            rand_str = random.randbytes(16).hex().upper()
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
    def client_app(self) -> httpx.AsyncClient:
        """
        用于APP请求

        Returns:
            httpx.AsyncClient
        """

        if self._client_app is None:
            headers = {
                Header.USER_AGENT: f"tieba/{self.latest_version}",
                Header.CONNECTION: "keep-alive",
                Header.ACCEPT_ENCODING: "gzip",
                Header.HOST: "tiebac.baidu.com",
            }

            self._client_app = httpx.AsyncClient(headers=headers, timeout=self._timeout, trust_env=self._use_env_proxy)

        return self._client_app

    @property
    def client_app_proto(self) -> httpx.AsyncClient:
        """
        用于APP protobuf请求

        Returns:
            httpx.AsyncClient
        """

        if self._client_app_proto is None:
            headers = {
                Header.USER_AGENT: f"tieba/{self.latest_version}",
                Header.BAIDU_DATA_TYPE: "protobuf",
                Header.CONNECTION: "keep-alive",
                Header.ACCEPT_ENCODING: "gzip",
                Header.HOST: "tiebac.baidu.com",
            }

            self._client_app_proto = httpx.AsyncClient(
                headers=headers, timeout=self._timeout, trust_env=self._use_env_proxy
            )

        return self._client_app_proto

    @property
    def client_web(self) -> httpx.AsyncClient:
        """
        用于网页端请求

        Returns:
            httpx.AsyncClient
        """

        if self._client_web is None:
            headers = {
                Header.USER_AGENT: f"tieba/{self.latest_version}",
                Header.ACCEPT_ENCODING: "gzip, deflate",
                Header.CACHE_CONTROL: "no-cache",
                Header.CONNECTION: "keep-alive",
                Header.HOST: "tieba.baidu.com",
            }
            cookies = {
                'BDUSS': self.BDUSS,
                'STOKEN': self.STOKEN,
            }

            self._client_web = httpx.AsyncClient(
                headers=headers, cookies=cookies, timeout=self._timeout, trust_env=self._use_env_proxy
            )

        return self._client_web

    @property
    def client_ws(self) -> httpx.AsyncClient:
        """
        用于websocket请求

        Returns:
            httpx.AsyncClient
        """

        if self._client_ws is None:
            headers = {
                Header.HOST: "im.tieba.baidu.com:8000",
                Header.SEC_WEBSOCKET_EXTENSIONS: "im_version=2.3",
            }

            self._client_ws = httpx.AsyncClient(headers=headers, timeout=self._timeout, trust_env=self._use_env_proxy)

        return self._client_ws

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

        ws_view = memoryview(ws_bytes)
        flag = ws_view[0]
        cmd = int.from_bytes(ws_view[1:5], 'big')
        req_id = int.from_bytes(ws_view[5:9], 'big')

        ws_bytes = ws_view[9:].tobytes()
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
            httpx_ws.WebSocketUpgradeError: websocket握手失败
        """

        if self._ws_dispatcher is not None and not self._ws_dispatcher.cancelled():
            self._ws_dispatcher.cancel()

        request = self.client_ws.build_request("GET", httpcore.URL(scheme=b"ws", host=b"im.tieba.baidu.com", port=8000))
        response = await self.client_ws.send(request=request, stream=True)
        if response.status_code != 101:
            raise httpx_ws.WebSocketUpgradeError(response)

        self.websocket = httpx_ws.AsyncWebSocketSession(
            response.extensions["network_stream"], keepalive_ping_interval_seconds=heartbeat
        )

        self._ws_dispatcher = asyncio.create_task(self._ws_dispatch(), name="ws_dispatcher")

    @property
    def is_ws_aviliable(self) -> bool:
        """
        self.websocket是否可用

        Returns:
            bool: True则self.websocket可用 反之不可用
        """

        return self.websocket is not None and self.websocket.connection.state == wsproto.connection.ConnectionState.OPEN

    async def send_ws_bytes(
        self, ws_bytes: bytes, /, cmd: int, *, need_gzip: bool = True, need_encrypt: bool = True
    ) -> WebsocketResponse:
        """
        将ws_bytes通过贴吧websocket发送

        Args:
            ws_bytes (bytes): 待发送的websocket数据
            cmd (int): 请求的cmd类型
            need_gzip (bool, optional): 是否需要gzip压缩. Defaults to False.
            need_encrypt (bool, optional): 是否需要aes加密. Defaults to False.

        Returns:
            WebsocketResponse: 用于等待返回数据的WebsocketResponse实例
        """

        ws_res = WebsocketResponse()
        ws_bytes = self._pack_ws_bytes(ws_bytes, cmd, ws_res.req_id, need_gzip=need_gzip, need_encrypt=need_encrypt)

        WebsocketResponse.ws_res_wait_dict[ws_res.req_id] = ws_res
        await self.websocket.send_bytes(ws_bytes)

        return ws_res

    async def _ws_dispatch(self) -> None:
        """
        分发从贴吧websocket接收到的数据
        """

        try:
            while 1:
                res_bytes = await self.websocket.receive_bytes()
                res_bytes, _, req_id = self._unpack_ws_bytes(res_bytes)

                ws_res = WebsocketResponse.ws_res_wait_dict.get(req_id, None)
                if ws_res:
                    ws_res._data_future.set_result(res_bytes)

        except (httpx_ws.WebSocketDisconnect, asyncio.CancelledError):
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

            req_proto = UpdateClientInfoReqIdl_pb2.UpdateClientInfoReqIdl()
            req_proto.data.bduss = self.BDUSS
            req_proto.data.device = f"""{{"subapp_type":"mini","_client_version":"{self.post_version}","pversion":"1.0.3","_msg_status":"1","_phone_imei":"000000000000000","from":"1021099l","cuid_galaxy2":"{self.cuid_galaxy2}","model":"LIO-AN00","_client_type":"2"}}"""
            req_proto.data.secretKey = rsa_chiper.encrypt(self.ws_password)
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
            str: tbs
        """

        if not self._tbs:
            await self.login()

        return self._tbs

    async def get_self_info(self, require: ReqUInfo = ReqUInfo.ALL) -> UserInfo:
        """
        获取本账号信息

        Args:
            require (ReqUInfo): 指示需要获取的字段

        Returns:
            UserInfo: 用户信息
        """

        if not self._user.user_id:
            if require & ReqUInfo.BASIC:
                await self.login()
        if not self._user.tieba_uid:
            if require & (ReqUInfo.TIEBA_UID | ReqUInfo.NICK_NAME):
                await self._get_selfinfo_initNickname()

        return self._user

    async def login(self) -> bool:
        """
        登录并获取tbs和当前账号的用户信息

        Returns:
            bool: True成功 False失败
        """

        from . import login

        try:
            request = login.pack_request(self.client_app, self.BDUSS, self.latest_version)
            response = await send_request(self.client_app, request)
            user, tbs = login.parse_response(response)

            self._user = self._user | user
            self._tbs = tbs

        except Exception as err:
            LOG.warning(err)
            self._user = UserInfo()
            self._tbs = ""
            return False

        return True

    async def get_fid(self, fname: str) -> int:
        """
        通过贴吧名获取forum_id

        Args:
            fname (str): 贴吧名

        Returns:
            int: forum_id
        """

        if fid := ForumInfoCache.get_fid(fname):
            return fid

        from . import get_fid

        try:
            request = get_fid.pack_request(self.client_web, fname)
            response = await send_request(self.client_web, request)
            fid = get_fid.parse_response(response)

            ForumInfoCache.add_forum(fname, fid)

        except Exception as err:
            LOG.warning(f"{err}. fname={fname}")
            fid = 0

        return fid

    async def get_fname(self, fid: int) -> str:
        """
        通过forum_id获取贴吧名

        Args:
            fid (int): forum_id

        Returns:
            str: 贴吧名
        """

        if fname := ForumInfoCache.get_fname(fid):
            return fname

        fname = (await self.get_forum_detail(fid)).fname

        if fname:
            ForumInfoCache.add_forum(fname, fid)

        return fname

    async def get_user_info(self, _id: Union[str, int], /, require: ReqUInfo = ReqUInfo.ALL) -> UserInfo:
        """
        获取用户信息

        Args:
            _id (str | int): 用户id user_id / portrait / user_name
            require (ReqUInfo): 指示需要获取的字段

        Returns:
            UserInfo: 用户信息
        """

        if not _id:
            LOG.warning("Null input")
            return UserInfo(_id)

        if UserInfo.is_user_id(_id):
            if (require | ReqUInfo.BASIC) == ReqUInfo.BASIC:
                # 仅有BASIC需求
                return await self._get_uinfo_getUserInfo(_id)
            elif require & ReqUInfo.TIEBA_UID:
                # 有TIEBA_UID需求
                user = await self._get_uinfo_getUserInfo(_id)
                user, _ = await self.get_homepage(user.portrait, with_threads=False)
                return user
            else:
                # 有除TIEBA_UID外的其他非BASIC需求
                return await self._get_uinfo_getuserinfo(_id)
        elif UserInfo.is_portrait(_id):
            if (require | ReqUInfo.BASIC) == ReqUInfo.BASIC:
                if not require & ReqUInfo.USER_ID:
                    # 无USER_ID需求
                    return await self._get_uinfo_panel(_id)
                else:
                    user, _ = await self.get_homepage(_id, with_threads=False)
                    return user
            else:
                user, _ = await self.get_homepage(_id, with_threads=False)
                return user
        else:
            if (require | ReqUInfo.BASIC) == ReqUInfo.BASIC:
                return await self._get_uinfo_user_json(_id)
            elif require & ReqUInfo.NICK_NAME and not require & ReqUInfo.USER_ID:
                # 有NICK_NAME需求但无USER_ID需求
                return await self._get_uinfo_panel(_id)
            else:
                user = await self._get_uinfo_user_json(_id)
                user, _ = await self.get_homepage(user.portrait, with_threads=False)
                return user

    async def _get_uinfo_panel(self, name_or_portrait: str) -> UserInfo:
        """
        接口 https://tieba.baidu.com/home/get/panel

        Args:
            name_or_portrait (str): 用户id user_name / portrait

        Returns:
            UserInfo: 包含 portrait, user_name, nick_name

        Note:
            从2022.08.30开始服务端不再返回user_id字段 请谨慎使用
            该接口可判断用户是否被屏蔽
            该接口rps阈值较低 建议每隔一段时间更换一个可用的Cookie字段BAIDUID
        """

        from . import get_uinfo_panel

        try:
            request = get_uinfo_panel.pack_request(self.client_web, name_or_portrait)
            response = await send_request(self.client_web, request)
            user = get_uinfo_panel.parse_response(response)

        except Exception as err:
            LOG.warning(f"{err}. user={name_or_portrait}")
            user = UserInfo()

        return user

    async def _get_uinfo_user_json(self, user_name: str) -> UserInfo:
        """
        接口 http://tieba.baidu.com/i/sys/user_json

        Args:
            user_name (str): 用户id user_name

        Returns:
            UserInfo: 包含 user_id / portrait / user_name
        """

        from . import get_uinfo_user_json

        try:
            request = get_uinfo_user_json.pack_request(self.client_web, user_name)
            response = await send_request(self.client_web, request)
            user = get_uinfo_user_json.parse_response(response)
            user.user_name = user_name

        except Exception as err:
            LOG.warning(f"{err}. user={user_name}")
            user = UserInfo()

        return user

    async def _get_uinfo_getuserinfo(self, user_id: int) -> UserInfo:
        """
        接口 http://tiebac.baidu.com/c/u/user/getuserinfo

        Args:
            user_id (int): 用户id user_id

        Returns:
            UserInfo: 包含 all
        """

        from . import get_uinfo_getuserinfo

        try:
            request = get_uinfo_getuserinfo.pack_request(self.client_app_proto, user_id)
            response = await send_request(self.client_app_proto, request)
            user = get_uinfo_getuserinfo.parse_response(response)

        except Exception as err:
            LOG.warning(f"{err}. user={user_id}")
            user = UserInfo()

        return user

    async def _get_uinfo_getUserInfo(self, user_id: int) -> UserInfo:
        """
        接口 http://tieba.baidu.com/im/pcmsg/query/getUserInfo

        Args:
            user_id (int): 用户id user_id

        Returns:
            UserInfo: 包含 user_id / portrait / user_name

        Note:
            该接口需要BDUSS
        """

        from . import get_uinfo_getUserInfo

        try:
            request = get_uinfo_getUserInfo.pack_request(self.client_web, user_id)
            response = await send_request(self.client_web, request)
            user = get_uinfo_getUserInfo.parse_response(response)
            user._user_id = user_id

        except Exception as err:
            LOG.warning(f"{err}. user={user_id}")
            user = UserInfo()

        return user

    async def tieba_uid2user_info(self, tieba_uid: int) -> UserInfo:
        """
        接口 http://tiebac.baidu.com/c/u/user/getUserByTiebaUid

        Args:
            tieba_uid (int): 用户id tieba_uid

        Returns:
            UserInfo: 包含 all

        Note:
            请注意tieba_uid与旧版user_id的区别
        """

        from . import tieba_uid2user_info

        try:
            request = tieba_uid2user_info.pack_request(self.client_app_proto, tieba_uid)
            response = await send_request(self.client_app_proto, request)
            user = tieba_uid2user_info.parse_response(response)

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
            fname_or_fid (str | int): 贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30.
            sort (int, optional): 排序方式 对于有热门分区的贴吧 0是热门排序 1是按发布时间 2报错 34都是热门排序 >=5是按回复时间
                对于无热门分区的贴吧 0是按回复时间 1是按发布时间 2报错 >=3是按回复时间. Defaults to 5.
            is_good (bool, optional): True则获取精品区帖子 False则获取普通区帖子. Defaults to False.

        Returns:
            Threads: 帖子列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        from . import get_threads

        try:
            request = get_threads.pack_request(self.client_app_proto, self.latest_version, fname, pn, rn, sort, is_good)
            response = await send_request(self.client_app_proto, request)
            threads = get_threads.parse_response(response)

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

        from . import get_posts

        try:
            request = get_posts.pack_request(
                self.client_app_proto,
                self.latest_version,
                tid,
                pn,
                rn,
                sort,
                only_thread_author,
                with_comments,
                comment_sort_by_agree,
                comment_rn,
                is_fold,
            )
            response = await send_request(self.client_app_proto, request)
            posts = get_posts.parse_response(response)

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

        from . import get_comments

        try:
            request = get_comments.pack_request(self.client_app_proto, self.latest_version, tid, pid, pn, is_floor)
            response = await send_request(self.client_app_proto, request)
            comments = get_comments.parse_response(response)

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

        from . import search_post

        try:
            request = search_post.pack_request(
                self.client_app, self.latest_version, fname, query, pn, rn, query_type, only_thread
            )
            response = await send_request(self.client_app, request)
            searches = search_post.parse_response(response)

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

        from . import get_forum_detail

        try:
            request = get_forum_detail.pack_request(self.client_app, self.latest_version, fid)
            response = await send_request(self.client_app, request)
            forum = get_forum_detail.parse_response(response)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid}")
            forum = Forum()

        return forum

    async def get_bawu_info(self, fname_or_fid: Union[str, int]) -> Dict[str, List[UserInfo]]:
        """
        获取吧务信息

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            dict[str, list[UserInfo]]: {吧务类型: list[吧务用户信息]}
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        from . import get_bawu_info

        try:
            request = get_bawu_info.pack_request(self.client_app_proto, self.latest_version, fid)
            response = await send_request(self.client_app_proto, request)
            bawu_dict = get_bawu_info.parse_response(response)

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

        from . import get_tab_map

        try:
            request = get_tab_map.pack_request(self.client_app_proto, self.BDUSS, self.latest_version, fname)
            response = await send_request(self.client_app_proto, request)
            tab_map = get_tab_map.parse_response(response)

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

        from . import get_rank_users

        try:
            request = get_rank_users.pack_request(self.client_web, fname, pn)
            response = await send_request(self.client_web, request)
            rank_users = get_rank_users.parse_response(response)

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

        from . import get_member_users

        try:
            request = get_member_users.pack_request(self.client_web, fname, pn)
            response = await send_request(self.client_web, request)
            member_users = get_member_users.parse_response(response)

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

        from . import get_square_forums

        try:
            request = get_square_forums.pack_request(
                self.client_app_proto, self.BDUSS, self.latest_version, class_name, pn, rn
            )
            response = await send_request(self.client_app_proto, request)
            square_forums = get_square_forums.parse_response(response)

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
            _id (str | int): 用户id user_id / user_name / portrait 优先portrait
            with_threads (bool, optional): True则同时请求主页帖子列表 False则返回的threads为空. Defaults to True.

        Returns:
            tuple[UserInfo, list[NewThread]]: 用户信息, list[帖子信息]
        """

        if not UserInfo.is_portrait(_id):
            user = await self.get_user_info(_id, ReqUInfo.PORTRAIT)
        else:
            user = UserInfo(_id)

        from . import get_homepage

        try:
            request = get_homepage.pack_request(self.client_app_proto, self.latest_version, user.portrait, with_threads)
            response = await send_request(self.client_app_proto, request)
            user, threads = get_homepage.parse_response(response)

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

        from . import get_statistics

        try:
            request = get_statistics.pack_request(self.client_app, self.BDUSS, self.latest_version, fid)
            response = await send_request(self.client_app, request)
            stat = get_statistics.parse_response(response)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid}")
            stat = {field_name: [] for field_name in get_statistics.field_names}

        return stat

    async def get_follow_forums(self, _id: Union[str, int], /, pn: int = 1, *, rn: int = 50) -> FollowForums:
        """
        获取用户关注贴吧列表

        Args:
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 50.

        Returns:
            FollowForums: 用户关注贴吧列表
        """

        if not UserInfo.is_user_id(_id):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
        else:
            user = UserInfo(_id)

        from . import get_follow_forums

        try:
            request = get_follow_forums.pack_request(
                self.client_app, self.BDUSS, self.latest_version, user.user_id, pn, rn
            )
            response = await send_request(self.client_app, request)
            follow_forums = get_follow_forums.parse_response(response)

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

        from . import get_recom_status

        try:
            request = get_recom_status.pack_request(self.client_app, self.BDUSS, self.latest_version, fid)
            response = await send_request(self.client_app, request)
            total_recom_num, used_recom_num = get_recom_status.parse_response(response)

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

        from . import get_recom_threads

        try:
            request = get_recom_threads.pack_request(self.client_app, self.BDUSS, self.latest_version, fid, pn, rn)
            response = await send_request(self.client_app, request)
            recom_threads = get_recom_threads.parse_response(response)

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
            _id (str | int): 用户id user_id / user_name / portrait 优先portrait
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

        if not UserInfo.is_portrait(_id):
            user = await self.get_user_info(_id, ReqUInfo.PORTRAIT)
        else:
            user = UserInfo(_id)

        tbs = await self.get_tbs()

        from . import block

        try:
            request = block.pack_request(self.client_app, self.BDUSS, tbs, fname, fid, user.portrait, day, reason)
            response = await send_request(self.client_app, request)
            block.parse_response(response)

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
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        if not UserInfo.is_user_id(_id):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
        else:
            user = UserInfo(_id)

        tbs = await self.get_tbs()

        from . import unblock

        try:
            request = unblock.pack_request(self.client_web, tbs, fname, fid, user.user_id)
            response = await send_request(self.client_web, request)
            unblock.parse_response(response)

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

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        tbs = await self.get_tbs()

        from . import del_thread

        try:
            request = del_thread.pack_request(self.client_app, self.BDUSS, tbs, fid, tid, is_hide=True)
            response = await send_request(self.client_app, request)
            del_thread.parse_response(response)

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

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        tbs = await self.get_tbs()

        from . import del_thread

        try:
            request = del_thread.pack_request(self.client_app, self.BDUSS, tbs, fid, tid, is_hide=False)
            response = await send_request(self.client_app, request)
            del_thread.parse_response(response)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def del_threads(self, fname_or_fid: Union[str, int], /, tids: List[int], *, block: bool = False) -> bool:
        """
        批量删除主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tids (list[int]): 待删除的主题帖tid列表
            block (bool, optional): 是否同时封一天. Defaults to False.

        Returns:
            bool: True成功 False失败 部分成功返回True
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        tbs = await self.get_tbs()

        from . import del_threads

        try:
            request = del_threads.pack_request(self.client_app, self.BDUSS, tbs, fid, tids, block)
            response = await send_request(self.client_app, request)
            del_threads.parse_response(response)

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
        tbs = await self.get_tbs()

        from . import del_post

        try:
            request = del_post.pack_request(self.client_app, self.BDUSS, tbs, fid, pid)
            response = await send_request(self.client_app, request)
            del_post.parse_response(response)

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
            bool: True成功 False失败 部分成功返回True
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        tbs = await self.get_tbs()

        from . import del_posts

        try:
            request = del_posts.pack_request(self.client_app, self.BDUSS, tbs, fid, pids, block)
            response = await send_request(self.client_app, request)
            del_posts.parse_response(response)

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

        tbs = await self.get_tbs()

        from . import recover

        request = recover.pack_request(self.client_web, tbs, fname, fid, tid, pid, is_hide)
        response = await send_request(self.client_web, request)
        recover.parse_response(response)

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
        tbs = await self.get_tbs()

        from . import move

        try:
            request = move.pack_request(
                self.client_app, self.BDUSS, tbs, self.latest_version, fid, tid, to_tab_id, from_tab_id
            )
            response = await send_request(self.client_app, request)
            move.parse_response(response)

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

        from . import recommend

        try:
            request = recommend.pack_request(self.client_app, self.BDUSS, fid, tid)
            response = await send_request(self.client_app, request)
            recommend.parse_response(response)

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

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        tbs = await self.get_tbs()

        from . import good

        try:
            cid = await self._get_cid(fname_or_fid, cname)
            request = good.pack_request(self.client_app, self.BDUSS, tbs, fname, fid, tid, cid, is_set=True)
            response = await send_request(self.client_app, request)
            good.parse_response(response)

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

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        tbs = await self.get_tbs()

        from . import good

        try:
            request = good.pack_request(self.client_app, self.BDUSS, tbs, fname, fid, tid, 0, is_set=False)
            response = await send_request(self.client_app, request)
            good.parse_response(response)

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

        from . import get_cid

        try:
            request = get_cid.pack_request(self.client_app, self.BDUSS, fname)
            response = await send_request(self.client_app, request)
            cid = get_cid.parse_response(response, cname)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname} cname={cname}")
            cid = 0

        return cid

    async def top(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        置顶主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待置顶的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        tbs = await self.get_tbs()

        from . import top

        try:
            request = top.pack_request(self.client_app, self.BDUSS, tbs, fname, fid, tid, is_set=True)
            response = await send_request(self.client_app, request)
            top.parse_response(response)

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

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        tbs = await self.get_tbs()

        from . import top

        try:
            request = top.pack_request(self.client_app, self.BDUSS, tbs, fname, fid, tid, is_set=False)
            response = await send_request(self.client_app, request)
            top.parse_response(response)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname_or_fid} tid={tid}")
            return False

        LOG.info(f"Succeeded. forum={fname_or_fid} tid={tid}")
        return True

    async def get_recovers(self, fname_or_fid: Union[str, int], /, name: str = '', pn: int = 1) -> Recovers:
        """
        获取pn页的待恢复帖子列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid
            name (str, optional): 通过被删帖作者的用户名/昵称查询 默认为空即查询全部. Defaults to ''.
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            Recovers: 待恢复帖子列表
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        from . import get_recovers

        try:
            request = get_recovers.pack_request(self.client_web, fname, fid, name, pn)
            response = await send_request(self.client_web, request)
            recovers = get_recovers.parse_response(response)

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

        from . import get_blacklist_users

        try:
            request = get_blacklist_users.pack_request(self.client_web, fname, pn)
            response = await send_request(self.client_web, request)
            blacklist_users = get_blacklist_users.parse_response(response)

        except Exception as err:
            LOG.warning(f"{err}. forum={fname}")
            blacklist_users = BlacklistUsers()

        return blacklist_users

    async def blacklist_add(self, fname_or_fid: Union[str, int], /, _id: Union[str, int]) -> bool:
        """
        添加贴吧黑名单

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先贴吧名
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        if not UserInfo.is_user_id(_id):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
        else:
            user = UserInfo(_id)

        tbs = await self.get_tbs()

        from . import blacklist_add

        try:
            request = blacklist_add.pack_request(self.client_web, tbs, fname, user.user_id)
            response = await send_request(self.client_web, request)
            blacklist_add.parse_response(response)

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
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        if not UserInfo.is_user_id(_id):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
        else:
            user = UserInfo(_id)

        tbs = await self.get_tbs()

        from . import blacklist_del

        try:
            request = blacklist_del.pack_request(self.client_web, tbs, fname, user.user_id)
            response = await send_request(self.client_web, request)
            blacklist_del.parse_response(response)

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

        tbs = await self.get_tbs()

        from . import get_unblock_appeals

        try:
            request = get_unblock_appeals.pack_request(self.client_web, tbs, fname, fid, pn, rn)
            response = await send_request(self.client_web, request)
            appeals = get_unblock_appeals.parse_response(response)

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

        tbs = await self.get_tbs()

        from . import handle_unblock_appeals

        try:
            request = handle_unblock_appeals.pack_request(self.client_web, tbs, fname, fid, appeal_ids, refuse)
            response = await send_request(self.client_web, request)
            handle_unblock_appeals.parse_response(response)

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

        from . import get_image

        try:
            request = get_image.pack_request(self.client_web, img_url)
            response = await send_request(self.client_web, request)
            image = get_image.parse_response(response)

        except Exception as err:
            LOG.warning(f"{err}. url={img_url}")
            image = np.empty(0, dtype=np.uint8)

        return image

    async def hash2image(self, raw_hash: str, /, size: Literal['s', 'm', 'l'] = 's') -> "np.ndarray":
        """
        通过百度图库hash获取静态图像

        Args:
            raw_hash (str): 百度图库hash
            size (Literal['s', 'm', 'l'], optional): 获取图像的大小 s为宽720 m为宽960 l为原图. Defaults to 's'.

        Returns:
            np.ndarray: 图像
        """

        from . import get_image

        try:
            request = get_image.hash_pack_request(self.client_web, raw_hash, size)
            response = await send_request(self.client_web, request)
            image = get_image.parse_response(response)

        except Exception as err:
            LOG.warning(f"{err}. raw_hash={raw_hash} size={size}")
            image = np.empty(0, dtype=np.uint8)

        return image

    async def get_portrait(self, _id: Union[str, int], /, size: Literal['s', 'm', 'l'] = 's') -> "np.ndarray":
        """
        获取用户头像

        Args:
            _id (str | int): 用户id user_id / user_name / portrait 优先portrait
            size (Literal['s', 'm', 'l'], optional): 获取头像的大小 s为55x55 m为110x110 l为原图. Defaults to 's'.

        Returns:
            np.ndarray: 头像
        """

        if not UserInfo.is_portrait(_id):
            user = await self.get_user_info(_id, ReqUInfo.PORTRAIT)
        else:
            user = UserInfo(_id)

        from . import get_image

        try:
            request = get_image.portrait_pack_request(self.client_web, user.portrait, size)
            response = await send_request(self.client_web, request)
            image = get_image.parse_response(response)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            image = np.empty(0, dtype=np.uint8)

        return image

    async def _get_selfinfo_initNickname(self) -> bool:
        """
        获取本账号信息

        Returns:
            bool: True成功 False失败
        """

        from . import get_selfinfo_initNickname

        try:
            request = get_selfinfo_initNickname.pack_request(self.client_app, self.BDUSS, self.latest_version)
            response = await send_request(self.client_app, request)
            user = get_selfinfo_initNickname.parse_response(response)

            self._user = self._user | user

        except Exception as err:
            LOG.warning(err)
            return False

        return True

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

        from . import get_newmsg

        try:
            request = get_newmsg.pack_request(self.client_app, self.BDUSS)
            response = await send_request(self.client_app, request)
            msg = get_newmsg.parse_response(response)

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

        from . import get_replys

        try:
            request = get_replys.pack_request(self.client_app_proto, self.BDUSS, self.latest_version, pn)
            response = await send_request(self.client_app_proto, request)
            replys = get_replys.parse_response(response)

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

        from . import get_ats

        try:
            request = get_ats.pack_request(self.client_app, self.BDUSS, self.latest_version, pn)
            response = await send_request(self.client_app, request)
            ats = get_ats.parse_response(response)

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

        user = await self.get_self_info(ReqUInfo.USER_ID)

        from . import get_user_contents

        try:
            request = get_user_contents.pack_request(
                self.client_app_proto,
                self.BDUSS,
                self.latest_version,
                user.user_id,
                pn,
                is_thread=True,
                public_only=True,
            )
            response = await send_request(self.client_app_proto, request)
            threads = get_user_contents.thread_parse_response(response, user)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            threads = []

        return threads

    async def get_self_threads(self, pn: int = 1) -> List[NewThread]:
        """
        获取本人发布的主题帖列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            list[NewThread]: 主题帖列表
        """

        user = await self.get_self_info(ReqUInfo.USER_ID)

        from . import get_user_contents

        try:
            request = get_user_contents.pack_request(
                self.client_app_proto,
                self.BDUSS,
                self.latest_version,
                user.user_id,
                pn,
                is_thread=True,
                public_only=False,
            )
            response = await send_request(self.client_app_proto, request)
            threads = get_user_contents.thread_parse_response(response, user)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            threads = []

        return threads

    async def get_self_posts(self, pn: int = 1) -> List[UserPosts]:
        """
        获取本人发布的回复列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            list[UserPosts]: 回复列表
        """

        user = await self.get_self_info(ReqUInfo.USER_ID)

        from . import get_user_contents

        try:
            request = get_user_contents.pack_request(
                self.client_app_proto,
                self.BDUSS,
                self.latest_version,
                user.user_id,
                pn,
                is_thread=False,
                public_only=False,
            )
            response = await send_request(self.client_app_proto, request)
            res_list = get_user_contents.thread_parse_response(response, user)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            res_list = []

        return res_list

    async def get_user_threads(self, _id: Union[str, int], pn: int = 1) -> List[NewThread]:
        """
        获取用户发布的主题帖列表

        Args:
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            list[NewThread]: 主题帖列表
        """

        if not UserInfo.is_user_id(_id):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
        else:
            user = UserInfo(_id)

        from . import get_user_contents

        try:
            request = get_user_contents.pack_request(
                self.client_app_proto,
                self.BDUSS,
                self.latest_version,
                user.user_id,
                pn,
                is_thread=True,
                public_only=False,
            )
            response = await send_request(self.client_app_proto, request)
            threads = get_user_contents.thread_parse_response(response, user)

        except Exception as err:
            LOG.warning(f"{err}. user={user}")
            threads = []

        return threads

    async def get_fans(self, _id: Union[str, int, None] = None, /, pn: int = 1) -> Fans:
        """
        获取粉丝列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            _id (str | int | None): 用户id user_id / user_name / portrait 优先user_id
                默认为None即获取本账号信息. Defaults to None.

        Returns:
            Fans: 粉丝列表
        """

        if _id is None:
            user = await self.get_self_info(ReqUInfo.USER_ID)
        elif not UserInfo.is_user_id(_id):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
        else:
            user = UserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('_client_version', self.latest_version),
            ('pn', pn),
            ('uid', user.user_id),
        ]

        try:
            async with self.client_app.post(
                httpcore.URL(path="/c/u/fans/page"),
                data=pack_form_request(payload),
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
            _id (str | int | None): 用户id user_id / user_name / portrait 优先user_id
                默认为None即获取本账号信息. Defaults to None.

        Returns:
            Follows: 关注列表
        """

        if _id is None:
            user = await self.get_self_info(ReqUInfo.USER_ID)
        elif not UserInfo.is_user_id(_id):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
        else:
            user = UserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('_client_version', self.latest_version),
            ('pn', pn),
            ('uid', user.user_id),
        ]

        try:
            async with self.client_app.post(
                httpcore.URL(path="/c/u/follow/followList"),
                data=pack_form_request(payload),
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
            async with self.client_web.get(
                httpcore.URL(scheme="https", host="tieba.baidu.com", path="/mg/o/getForumHome"),
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
            async with self.client_app_proto.post(
                httpcore.URL(path="/c/u/user/getDislikeList", query_string="cmd=309692"),
                data=pack_proto_request(req_proto.SerializeToString()),
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

        async with self.client_app.post(
            httpcore.URL(path="/c/c/agree/opAgree"),
            data=pack_form_request(payload),
        ) as resp:
            res_json: dict = await resp.json(encoding='utf-8', content_type=None)

        if int(res_json['error_code']):
            raise TiebaServerError(res_json['error_msg'])

    async def remove_fan(self, _id: Union[str, int]):
        """
        移除粉丝

        Args:
            _id (str | int): 待移除粉丝的id user_id / user_name / portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        if not UserInfo.is_user_id(_id):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
        else:
            user = UserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('fans_uid', user.user_id),
            ('tbs', await self.get_tbs()),
        ]

        try:
            async with self.client_app.post(
                httpcore.URL(path="/c/c/user/removeFans"),
                data=pack_form_request(payload),
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
            _id (str | int): 用户id user_id / user_name / portrait 优先portrait

        Returns:
            bool: True成功 False失败
        """

        if not UserInfo.is_portrait(_id):
            user = await self.get_user_info(_id, ReqUInfo.PORTRAIT)
        else:
            user = UserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('portrait', user.portrait),
            ('tbs', await self.get_tbs()),
        ]

        try:
            async with self.client_app.post(
                httpcore.URL(path="/c/c/user/follow"),
                data=pack_form_request(payload),
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
            _id (str | int): 用户id user_id / user_name / portrait 优先portrait

        Returns:
            bool: True成功 False失败
        """

        if not UserInfo.is_portrait(_id):
            user = await self.get_user_info(_id, ReqUInfo.PORTRAIT)
        else:
            user = UserInfo(_id)

        payload = [
            ('BDUSS', self.BDUSS),
            ('portrait', user.portrait),
            ('tbs', await self.get_tbs()),
        ]

        try:
            async with self.client_app.post(
                httpcore.URL(path="/c/c/user/unfollow"),
                data=pack_form_request(payload),
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

            async with self.client_app.post(
                httpcore.URL(path="/c/c/forum/like"),
                data=pack_form_request(payload),
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

            async with self.client_app.post(
                httpcore.URL(path="/c/c/forum/unfavolike"),
                data=pack_form_request(payload),
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

            async with self.client_app.post(
                httpcore.URL(path="/c/c/excellent/submitDislike"),
                data=pack_form_request(payload),
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

            async with self.client_app.post(
                httpcore.URL(path="/c/c/excellent/submitCancelDislike"),
                data=pack_form_request(payload),
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

            async with self.client_app.post(
                httpcore.URL(path="/c/c/thread/setPrivacy"),
                data=pack_form_request(payload),
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

            async with self.client_app.post(
                httpcore.URL(path="/c/c/forum/sign"),
                data=pack_form_request(payload),
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

            async with self.client_app.post(
                httpcore.URL(path="/c/c/post/add"),
                data=pack_form_request(payload),
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
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id
            content (str): 发送内容

        Returns:
            bool: True成功 False失败
        """

        if not UserInfo.is_user_id(_id):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
        else:
            user = UserInfo(_id)

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
