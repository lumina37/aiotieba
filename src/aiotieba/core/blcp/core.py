from __future__ import annotations

import asyncio
import base64
import dataclasses as dcs
import hashlib
import json
import random
import time
import urllib.parse
from sys import maxsize as LONG_MAX
from typing import TYPE_CHECKING, Any

import aiohttp
import yarl
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ...const import CHAT_VERSION
from ...enums import BLCPStatus
from ...helper.crypto import enuid, sign
from .conn import BLCPConn
from .const import CHAT_APPID, CHAT_SDK_VERSION
from .enums import BLCPMethodID, BLCPServiceID
from .exception import BLCPError, BLCPLoginError
from .packet import BLCPBody, BLCPRequest, BLCPResponse, JsonBody, LcmBody

if TYPE_CHECKING:
    from ...api._classdef import UserInfo
    from ...config import TimeoutConfig
    from ..account import Account
    from ..net import NetCore

LCP_SDK_VERSION = "3460016"
"""LCP SDK版本号 用于LCM登录报文中的sdk_version字段"""


@dcs.dataclass
class BLCPCore:
    """
    BLCP业务层 负责登录、吧群等业务与pim HTTP请求 内部持有BLCPConn

    Args:
        account (Account): 用户参数容器
        net_core (NetCore): 网络连接容器
        user (UserInfo): 用户信息容器
        timeout (TimeoutConfig, optional): 超时配置. Defaults to None.
        max_notify_queue (int, optional): 推送队列长度上限. Defaults to 100.
    """

    account: Account
    user: UserInfo
    net_core: NetCore
    conn: BLCPConn
    login_id: int
    _logged_in: bool
    _login_lock: asyncio.Lock

    def __init__(
        self,
        account: Account,
        net_core: NetCore,
        user: UserInfo,
        timeout: TimeoutConfig | None = None,
        max_notify_queue: int = 100,
    ) -> None:
        self.account = account
        self.user = user
        self.net_core = net_core
        self.conn = BLCPConn(timeout=timeout, max_notify_queue=max_notify_queue)
        self.login_id = 0
        self._logged_in = False
        self._login_lock = asyncio.Lock()

    def set_account(self, new_account: Account) -> None:
        """
        更新用户参数

        Args:
            new_account (Account): 用户参数容器
        """

        self.account = new_account

    @property
    def status(self) -> BLCPStatus:
        """
        BLCP整体状态 业务登录后为LOGGED_IN
        """

        if self._logged_in:
            return BLCPStatus.LOGGED_IN

        return self.conn.status

    @property
    def is_logged_in(self) -> bool:
        """
        业务是否已登录
        """

        return self._logged_in

    @property
    def message_queue(self) -> asyncio.Queue:
        """
        服务端推送队列
        """

        return self.conn.notifies

    async def login(self) -> None:
        """
        完成LCP握手 云控登录 与 IM登录

        Raises:
            BLCPLoginError: 任一环节失败
        """

        if self._logged_in:
            return

        async with self._login_lock:
            if self._logged_in:
                return

            if not self.conn.is_open:
                await self.conn.connect()

            await self._lcm_login()
            await self._cloud_control_login()
            await self._im_login()

            self._logged_in = True

    async def close(self) -> None:
        """
        关闭连接
        """

        self._logged_in = False
        await self.conn.close()

    async def request(
        self,
        service_id: int,
        method_id: int,
        body: BLCPBody | dict[str, Any] | None = None,
        *,
        read_timeout: float | None = None,
    ) -> BLCPResponse:
        """
        发送一次业务请求并等待响应

        Args:
            service_id (int): 服务号
            method_id (int): 方法号
            body (BLCPBody | dict | None, optional): 报文体 传入dict时自动包装为JsonBody. Defaults to None.
            read_timeout (float | None, optional): 读超时时间. Defaults to None.

        Returns:
            BLCPResponse: 响应报文
        """

        if isinstance(body, dict):
            body = JsonBody(body)

        request = BLCPRequest.create(service_id, method_id, body)

        return await self.conn.request(request, read_timeout)

    def pack_pim_request(self, path: str, data: dict[str, Any], *, with_cookie: bool = False) -> aiohttp.ClientRequest:
        """
        打包发往pim.baidu.com的JSON请求

        Args:
            path (str): 请求路径
            data (dict[str, Any]): 请求数据
            with_cookie (bool, optional): 是否携带BDUSS. Defaults to False.

        Returns:
            aiohttp.ClientRequest: 请求对象
        """

        headers = {
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.11.0",
            "Host": "pim.baidu.com",
        }
        if with_cookie:
            headers["Cookie"] = "BDUSS=" + self.account.BDUSS

        return aiohttp.ClientRequest(
            "POST",
            yarl.URL.build(scheme="https", host="pim.baidu.com", path=path, port=443),
            headers=headers,
            data=json.dumps(data),
        )

    async def join_chatroom(self, chatroom_id: int) -> bool:
        """
        加入吧群聊天室

        Args:
            chatroom_id (int): 聊天室id

        Returns:
            bool: 是否成功

        Raises:
            BLCPError: 未登录或服务端返回错误
        """

        if not self._logged_in:
            raise BLCPError("BLCP未登录")

        method = BLCPMethodID.JOIN_CAST

        request_data = {
            "method": int(method),
            "mcast_id": chatroom_id,
            "appid": CHAT_APPID,
            "uk": self.user.uk,
            "origin_id": self.user.trigger_id,
            "msg_key": "k" + str(int(time.time() * 100000)),
            "sdk_version": CHAT_SDK_VERSION,
            "is_reliable": False,
            "client_logid": int(time.time() * 1_000_000),
            "rpc": json.dumps({"rpc_retry_time": 0}),
        }

        response = await self.request(BLCPServiceID.MCAST, method, request_data)
        if response.error_code != 0:
            raise BLCPError(f"加入聊天室失败 code={response.error_code} text={response.error_text!r}")

        err_code = response.payload.get("err_code", -1)
        if err_code != 0:
            raise BLCPError(f"加入聊天室失败 err_code={err_code}")

        await self._fetch_room_history(chatroom_id)

        return True

    async def _lcm_login(self) -> None:
        token = await self._generate_lcm_token()
        if not token:
            raise BLCPLoginError("获取LCP token失败")

        correlation_id = random.randint(0, LONG_MAX)
        body = LcmBody.login(
            log_id=correlation_id,
            token=token,
            timestamp=int(time.time() * 1000),
            cuid=self.account.cuid_galaxy2,
            app_id=CHAT_APPID,
            app_version=CHAT_VERSION,
            sdk_version=LCP_SDK_VERSION,
        )
        request = BLCPRequest.create(BLCPServiceID.LCM, BLCPMethodID.LOGIN, body, correlation_id=correlation_id)

        response = await self.conn.request(request)
        if not response.ok:
            raise BLCPLoginError(f"LCP握手失败 code={response.error_code} text={response.error_text!r}")

        lcm = response.lcm
        self.conn.start_heartbeat(lcm.next_interval_ms if lcm is not None else 0)

    async def _generate_lcm_token(self) -> str:
        cuid = self.account.cuid_galaxy2
        ts = int(time.time() * 1000)
        data = {
            "app_id": str(CHAT_APPID),
            "app_version": CHAT_VERSION,
            "cuid": cuid,
            "device_type": "android",
            "manufacture": "",
            "model_type": "",
            "request_id": str(ts),
            "sdk_version": LCP_SDK_VERSION,
            "sign": hashlib.md5(f"{CHAT_APPID}{cuid}android{ts}".encode()).hexdigest(),
            "ts": ts,
            "user_key": "",
        }
        request = self.pack_pim_request("/rest/5.0/generate_lcm_token", data)

        try:
            response = await self.net_core.req2res(request, False)
            payload = await response.json()
        except Exception as err:
            raise BLCPLoginError("获取LCP token失败") from err

        return payload.get("token", "")

    async def _cloud_control_login(self) -> None:
        request_data = {
            "params": {
                "appname": "tieba",
                "sid": self.account.sample_id,
                "ua": "900_1600_android_12.68.1.0_240",
                "uid": enuid(self.account.cuid_galaxy2),
                "cfrom": "1008550l",
                "from": "1008550l",
                "network": "1_-1",
                "p_sv": "32",
                "mps": "",
                "mpv": "1",
                "c3_aid": self.account.c3_aid,
                "type_id": "0",
            },
            "filter": {"aps": {"cpu_abi": "armeabi-v7a"}, "command": {"step": "0"}},
        }

        response = await self.request(BLCPServiceID.CLOUD_CONTROL, BLCPMethodID.LOGIN, request_data)
        if response.error_code != 0:
            raise BLCPLoginError(f"云控登录失败 code={response.error_code} text={response.error_text!r}")

        errno = str(response.payload.get("errno", ""))
        if errno != "0":
            raise BLCPLoginError(f"云控登录失败 errno={errno}")

    async def _im_login(self) -> None:
        method = BLCPMethodID.LOGIN_BY_TOKEN

        request_data = {
            "method": int(method),
            "appid": CHAT_APPID,
            "device_id": "android_" + self.account.cuid_galaxy2,
            "account_type": 1,
            "token": self.account.BDUSS,
            "version": 4,
            "sdk_version": CHAT_SDK_VERSION,
            "app_version": CHAT_VERSION,
            "app_open_type": 0,
            "client_identifier": json.dumps({"zid": "", "version_code": ""}),
            "tail": 0,
            "timeout": 10,
            "cookie": "",
            "device_info": {
                "app_version": CHAT_VERSION,
                "os_version": "32",
                "platform": "android",
                "appid": str(CHAT_APPID),
                "from": "1008550l",
                "cfrom": "1008550l",
            },
            "rpc": json.dumps({"rpc_retry_time": 0}),
            "user_type": 0,
            "client_logid": int(time.time() * 1_000_000),
        }

        response = await self.request(BLCPServiceID.IM, method, request_data)
        if response.error_code != 0:
            raise BLCPLoginError(f"IM登录失败 code={response.error_code} text={response.error_text!r}")

        payload = response.payload
        err_code = payload.get("err_code", -1)
        if err_code != 0:
            raise BLCPLoginError(f"IM登录失败 err_code={err_code}")

        self.user.trigger_id = payload["trigger_id"][0]
        self.user.uk = payload["uk"]
        self.user.bduk = payload.get("bd_uid", "")
        self.login_id = payload.get("login_id", 0)

    async def _fetch_room_history(self, chatroom_id: int) -> dict[str, Any]:
        data = {
            "appid": CHAT_APPID,
            "mcast_id": chatroom_id,
            "msgid_begin": 0,
            "msgid_end": LONG_MAX,
            "count": -60,
            "category": 4,
            "app_version": CHAT_VERSION,
            "sdk_version": CHAT_SDK_VERSION,
            "device_id": self.account.cuid_galaxy2,
            "device_type": 2,
            "from_action": 1,
            "ext_info": urllib.parse.quote(
                json.dumps({"last_callback_msg_id": 0, "cast_id": 0, "local_ts": 0, "latest_msg_id": 0})
            ),
            "timestamp": int(time.time()),
            "account_type": 1,
        }
        data = sign(data, salt=b"")

        request = self.pack_pim_request("/rest/3.0/im/fetch_mcast_msg_client", data, with_cookie=True)

        try:
            response = await self.net_core.req2res(request, False)
            await response.read()
            return await response.json()
        except Exception as err:
            raise BLCPError("获取群聊历史消息失败") from err

    @staticmethod
    def get_bduk(user_id: int) -> str:
        """
        将user_id加密为群聊报文中的baidu_uk

        Args:
            user_id (int): 用户的user_id

        Returns:
            str: baidu_uk
        """

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded = padder.update(str(user_id).encode()) + padder.finalize()

        encryptor = Cipher(algorithms.AES(b"AFD311832EDEEAEF"), modes.CBC(b"2011121211143000")).encryptor()
        encrypted = encryptor.update(padded) + encryptor.finalize()

        return base64.urlsafe_b64encode(encrypted).strip(b"=").decode()

    @staticmethod
    def make_msg_key(bduk: str) -> str:
        """
        构造群聊消息的去重键

        Args:
            bduk (str): baidu_uk

        Returns:
            str: msg_key
        """

        return bduk + str(int(time.time() * 1000) * 1000) + f"{random.randint(-LONG_MAX, LONG_MAX)}"
