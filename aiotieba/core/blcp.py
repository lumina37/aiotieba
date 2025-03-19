from __future__ import annotations

import asyncio
import base64
import dataclasses as dcs
import gzip
import json
import random
import socket
import ssl
import time
import urllib.parse
import weakref
from asyncio import IncompleteReadError, Queue, StreamReader, StreamWriter
from hashlib import md5
from sys import maxsize as LongMax
from typing import TYPE_CHECKING

import aiohttp
import yarl
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ..api._protobuf import Lcm_pb2, Rpc_pb2
from ..config import ProxyConfig, TimeoutConfig
from ..const import CHAT_APPID, CHAT_SDK_VERSION, CHAT_VERSION
from ..helper import timeout
from ..helper.crypto import enuid

if TYPE_CHECKING:
    from ..api._classdef import UserInfo
    from .account import Account
    from .net import NetCore


@dcs.dataclass
class BLCPCore:
    """
    网络请求相关容器

    Args:
        proxy (ProxyConfig, optional): 代理配置. Defaults to None.
        timeout (TimeoutConfig, optional): 超时配置. Defaults to None.
    """

    account: Account
    user: UserInfo
    reader: StreamReader
    writer: StreamWriter
    loop: asyncio.AbstractEventLoop
    proxy: ProxyConfig
    timeout: TimeoutConfig
    blcp_dispatcher: asyncio.Task
    blcp_responses: ClientBLCPResponses
    waiter: BLCPWaiter
    net_core: NetCore
    trigger_id: int
    message_queue: Queue  # 该消息队列只有群聊消息，没有各种握手
    heartbeater: asyncio.Task

    def __init__(
        self,
        proxy: ProxyConfig | None = None,
        timeout: TimeoutConfig | None = None,
        loop: asyncio.AbstractEventLoop = None,
        net_core: NetCore = None,
        account: Account = None,
        user: UserInfo = None,
        max_queue_length: int = 100,
    ) -> None:
        if not isinstance(proxy, ProxyConfig):
            proxy = ProxyConfig()
        self.proxy = proxy

        if not isinstance(timeout, TimeoutConfig):
            timeout = TimeoutConfig()
        self.timeout = timeout
        if not loop:
            self.loop = asyncio.get_running_loop()
        else:
            self.loop = loop
        self.blcp_dispatcher: asyncio.Task = None
        self.heartbeater = None
        self.net_core = net_core
        self.account = account
        self.trigger_id = -1
        self.user = user
        self.status = -1
        self.message_queue = Queue(maxsize=max_queue_length)

    def set_account(self, new_account: Account) -> None:
        self.account = new_account

    async def connect(self) -> None:
        self.waiter = BLCPWaiter(5)

        context = ssl.create_default_context()
        context.check_hostname = False

        # print("connecting")

        try:
            reader, writer = await asyncio.open_connection(
                "common.lcs.baidu.com", 443, ssl=context, family=socket.AF_INET
            )  # 实际上可以支持ipv6
        except BaseException:
            raise
        else:
            self.reader = reader
            self.writer = writer

        if self.blcp_dispatcher is not None and not self.blcp_dispatcher.done():
            self.blcp_dispatcher.cancel()

        self.blcp_responses = ClientBLCPResponses(reader=reader, writer=writer)
        self.blcp_dispatcher = self.loop.create_task(self.__blcp_dispatch(), name="blcp_dispatcher")

        self.status = 0

    async def login(self) -> None:
        cuid_galaxy2 = self.account.cuid_galaxy2
        blcp_token = await self.generate_lcm_token(cuid_galaxy2)

        # 握手
        loginBLCPRequest = BLCPData(serviceId=1, methodId=1)
        loginBLCPRequest.RpcBody = self.buildRpcBody(
            serviceId=1, methodId=1, correlationId=loginBLCPRequest.correlationId, need_common=1
        )
        LcmBody = Lcm_pb2.RpcData()
        LcmBody.lcm_request.log_id = loginBLCPRequest.correlationId
        LcmBody.lcm_request.token = blcp_token
        LcmBody.lcm_request.common.cuid = cuid_galaxy2
        LcmBody.lcm_request.common.device = "android"
        LcmBody.lcm_request.common.app_id = str(CHAT_APPID)
        LcmBody.lcm_request.common.app_version = CHAT_VERSION
        LcmBody.lcm_request.common.sdk_version = "3460016"
        LcmBody.lcm_request.common.network = "wifi"
        LcmBody.lcm_request.timestamp = int(time.time() * 1000)
        LcmBody.lcm_request.start_type = -1
        LcmBody.lcm_request.conn_type = 1
        loginBLCPRequest.LcmBody = LcmBody.SerializeToString()

        response = self.waiter.new(loginBLCPRequest.correlationId)
        self.writer.write(loginBLCPRequest.toBytes())
        reps = await response.read()
        try:
            rpc, lcm = ClientBLCPResponses.parseBLCPResponse(reps.toBytes())
        except:
            raise Exception("BLCP Handshake error.")  # todo: 特殊的握手错误

        if rpc.response.error_text != "success" or lcm.lcm_response.error_msg != "success":
            raise Exception("BLCP Handshake error.")  # todo: 特殊的握手错误

        # 第二部分登陆
        # 构造部分位于 com.baidu.searchbox.cloudcontrolblcp.CloudControlBlCPManager

        # 参数来源在com.baidu.common.param.CommonUrlParamManager中找到
        sid = self.account.sample_id
        ua = "900_1600_android_12.68.1.0_240"  # 分辨率
        uid = enuid(cuid_galaxy2)  # Enuid，由cuid_galaxy2经过libbase64encoder_v2_0.so得到
        login_from = "1008550l"  # baidu_imsdk_common_data.xml
        cfrom = login_from
        c3_aid = self.account.c3_aid
        reqdict = {
            "params": {
                "appname": "tieba",
                "sid": sid,
                "ua": ua,
                "uid": uid,
                "cfrom": cfrom,
                "from": login_from,
                "network": "1_-1",
                "p_sv": "32",
                "mps": "",
                "mpv": "1",
                "c3_aid": c3_aid,
                "type_id": "0",
            },
            "filter": {"aps": {"cpu_abi": "armeabi-v7a"}, "command": {"step": "0"}},
        }

        loginBLCPRequest = BLCPData(serviceId=4, methodId=1)
        loginBLCPRequest.RpcBody = self.buildRpcBody(
            serviceId=4, methodId=1, correlationId=loginBLCPRequest.correlationId
        )
        loginBLCPRequest.LcmBody = json.dumps(reqdict).encode()
        response = self.waiter.new(loginBLCPRequest.correlationId)
        self.writer.write(loginBLCPRequest.toBytes())
        reps = await response.read()

        try:
            rpc, lcm = ClientBLCPResponses.parseBLCPResponse(reps.toBytes())
        except:
            raise Exception("BLCP Handshake error.")  # todo: 特殊的握手错误

        if rpc.response.error_text != "success" or lcm.get("errno") != "0":
            raise Exception("BLCP Handshake error.")  # todo: 特殊的握手错误

        loginBLCPRequest = BLCPData(serviceId=2, methodId=50)
        loginBLCPRequest.correlationId = 2000003149381050
        loginBLCPRequest.RpcBody = self.buildRpcBody(
            serviceId=2, methodId=50, correlationId=loginBLCPRequest.correlationId
        )

        client_identifier = {"zid": "", "version_code": ""}  # 待完善，目前可以不携带zid
        cookie = ""  # 待完善，目前可以不携带cookie
        token = self.account.BDUSS

        reqdict = {
            "method": 50,
            "appid": CHAT_APPID,
            "device_id": "android_" + cuid_galaxy2,
            "account_type": 1,
            "token": token,
            "version": 4,
            "sdk_version": CHAT_SDK_VERSION,
            "app_version": CHAT_VERSION,
            "app_open_type": 0,
            "client_identifier": json.dumps(client_identifier),
            "tail": 0,
            "timeout": 10,
            "cookie": cookie,
            "device_info": {
                "app_version": CHAT_VERSION,
                "os_version": "32",
                "platform": "android",
                "appid": str(CHAT_APPID),
                "from": login_from,
                "cfrom": cfrom,
            },
            "rpc": json.dumps({"rpc_retry_time": 0}),
            "user_type": 0,
            "client_logid": int(time.time() * 1000 * 1000),
        }

        loginBLCPRequest.LcmBody = json.dumps(reqdict).encode()
        response = self.waiter.new(loginBLCPRequest.correlationId)
        self.writer.write(loginBLCPRequest.toBytes())
        reps = await response.read()

        try:
            rpc, lcm = ClientBLCPResponses.parseBLCPResponse(reps.toBytes())
        except:
            raise Exception("BLCP Handshake error.")  # todo: 特殊的握手错误

        if rpc.response.error_text != "success" or lcm.get("err_code") != 0:
            raise Exception("BLCP Handshake error.")  # todo: 特殊的握手错误

        rep = json.loads(reps.LcmBody)

        self.user.trigger_id = rep["trigger_id"][0]
        self.user.uk = rep["uk"]
        self.user.bduk = rep["bd_uid"]
        self.login_id = rep["login_id"]

        self.status = 1

    async def generate_lcm_token(self, cuid_galaxy2):
        headers = {
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.11.0",
            "Host": "pim.baidu.com",
        }
        request_id = str(int(time.time() * 1000))
        ts = int(time.time() * 1000)
        data = {
            "app_id": str(CHAT_APPID),
            "app_version": CHAT_VERSION,
            "cuid": cuid_galaxy2,
            "device_type": "android",
            "manufacture": "",
            "model_type": "",
            "request_id": request_id,
            "sdk_version": "3460016",
            "sign": md5((str(CHAT_APPID) + cuid_galaxy2 + "android" + str(ts)).encode()).hexdigest(),  # appid
            "ts": ts,
            "user_key": "",
        }
        request = aiohttp.ClientRequest(
            "POST",
            yarl.URL.build(scheme="https", host="pim.baidu.com", path="/rest/5.0/generate_lcm_token", port=443),
            headers=headers,
            # proxy=self.net_core.proxy.url,
            # proxy_auth=self.net_core.proxy.auth,
            # ssl=False,
            data=json.dumps(data),
        )  # todo: 支持代理

        try:
            response = await self.net_core.req2res(request, False, 2 * 1024)
            rjson = await response.json()
            return rjson["token"]
        except Exception:
            return ""

    async def groupchat(self):  # 模拟正常请求，暂不清楚作用
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.11.0",
            "Host": "pim.baidu.com",
            "Cookie": "BDUSS=" + self.account.BDUSS,
        }
        ts = int(time.time())
        data = {
            "method": "get_joined_groups",
            "appid": CHAT_APPID,
            "timestamp": ts,
            "sign": md5((str(ts) + self.account.BDUSS + str(CHAT_APPID)).encode()).hexdigest(),
        }
        request = aiohttp.ClientRequest(
            "POST",
            yarl.URL.build(scheme="https", host="pim.baidu.com", path="/rest/2.0/im/groupchat", port=443),
            headers=headers,
            # proxy=self.net_core.proxy.url,
            # proxy_auth=self.net_core.proxy.auth,
            # ssl=False,
            data=urllib.parse.urlencode(data),
        )  # todo: 支持代理

        try:
            response = await self.net_core.req2res(request, False, 2 * 1024)
            await response.json()
        except Exception:
            return ""

    async def groupchatv1(self):  # 模拟正常请求，暂不清楚作用
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.11.0",
            "Host": "pim.baidu.com",
            "Cookie": "BDUSS=" + self.account.BDUSS,
        }
        ts = int(time.time())
        data = {
            "method": "get_joined_groups",
            "group_type": 3,
            "appid": CHAT_APPID,
            "source": 0,
            "cuid": self.account.cuid_galaxy2,
            "app_version": CHAT_VERSION,
            "sdk_version": str(CHAT_SDK_VERSION),
            "timestamp": ts,
            "device_type": 2,
            "sign": md5((str(ts) + self.account.BDUSS + str(CHAT_APPID)).encode()).hexdigest(),
        }
        request = aiohttp.ClientRequest(
            "POST",
            yarl.URL.build(scheme="https", host="pim.baidu.com", path="/rest/2.0/im/groupchatv1", port=443),
            headers=headers,
            # proxy=self.net_core.proxy.url,
            # proxy_auth=self.net_core.proxy.auth,
            # ssl=False,
            data=urllib.parse.urlencode(data),
        )  # todo: 支持代理

        try:
            response = await self.net_core.req2res(request, False, 2 * 1024)
            await response.json()
        except Exception:
            return ""

    @staticmethod
    def getBDUKfromUserId(user_id: str):
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_req_body = padder.update(user_id.encode()) + padder.finalize()

        aes_encryptor = Cipher(algorithms.AES(b"AFD311832EDEEAEF"), modes.CBC(b"2011121211143000")).encryptor()
        req_body_aes = aes_encryptor.update(padded_req_body) + aes_encryptor.finalize()

        return base64.urlsafe_b64encode(req_body_aes).strip(b"=").decode()

    @staticmethod
    def getmsgkey(bduk: str):
        return bduk + str(int(time.time() * 1000) * 1000) + f"{random.randint(-LongMax, LongMax)}"

    @staticmethod
    def buildRpcBody(serviceId, methodId, correlationId, compress_type=0, need_common=1):
        event_timestamp = Rpc_pb2.EventTimestamp()
        event_timestamp.event = "CLCPReqBegin"
        event_timestamp.timestamp_ms = int(time.time() * 1000)

        RpcRequestMeta = Rpc_pb2.RpcRequestMeta()
        RpcRequestMeta.log_id = correlationId
        RpcRequestMeta.service_id = serviceId
        RpcRequestMeta.method_id = methodId
        RpcRequestMeta.need_common = need_common
        RpcRequestMeta.event_list.append(event_timestamp)

        RpcMeta = Rpc_pb2.RpcMeta()
        RpcMeta.request.CopyFrom(RpcRequestMeta)
        RpcMeta.correlation_id = correlationId
        RpcMeta.compress_type = compress_type  # i
        RpcMeta.accept_compress_type = 1

        return RpcMeta.SerializeToString()

    async def __blcp_dispatch(self) -> None:
        async for msg in self.blcp_responses:
            if not msg:
                continue
            self.waiter.set_done(msg.correlationId, msg)
            # todo: 加上callbacks以处理服务端主动发送的消息，如群聊消息等。获取群聊消息推送需要先发包绑定群聊。
            if msg.isNotify:
                rpc, lcm = ClientBLCPResponses.parseBLCPResponse(
                    msg.toBytes()
                )  # todo:优化。这里在解码后又编码再解码了一次
                if self.message_queue.full():
                    await self.message_queue.get()  # 队满自动丢弃
                await self.message_queue.put(lcm)

        self.status = -1
        raise Exception("IM服务端断开连接")

    async def joinChatRoom(self, chatroom_id: int) -> bool:
        if self.status != 1:
            raise Exception("IM未登陆")
        request = BLCPData(serviceId=3, methodId=201)  # 加入Chatroom的请求
        request.RpcBody = self.buildRpcBody(serviceId=3, methodId=201, correlationId=request.correlationId)
        reqdict = {
            "method": 201,
            "mcast_id": chatroom_id,
            "appid": CHAT_APPID,
            "uk": self.user.uk,
            "origin_id": self.user.trigger_id,
            "msg_key": "k" + str(int(time.time() * 100000)),
            "sdk_version": CHAT_SDK_VERSION,
            "is_reliable": False,
            "client_logid": int(time.time() * 1000 * 1000),
            "rpc": json.dumps({"rpc_retry_time": 0}),
        }
        request.LcmBody = json.dumps(reqdict).encode()
        response = self.waiter.new(request.correlationId)
        self.writer.write(request.toBytes())
        reps = await response.read()

        try:
            rpc, lcm = ClientBLCPResponses.parseBLCPResponse(reps.toBytes())
        except:
            raise Exception("BLCP Handshake error.")  # todo: 特殊的握手错误
        if rpc.response.error_text != "success" or lcm.get("err_code") != 0:
            raise Exception("BLCP Handshake error.")  # todo: 特殊的握手错误

        await self.fetch_mcast_msg_client_request(self.account.cuid_galaxy2, chatroom_id)  # todo:获取历史消息

        if self.heartbeater is not None and not self.heartbeater.done():
            self.heartbeater.cancel()

        self.heartbeater = self.loop.create_task(self.__heartbeater(), name="heartbeater")

        return True

    async def __heartbeater(self, freq: int = 5):
        while True:
            await asyncio.sleep(freq)
            await self.heartbeat()

    async def exitChatRoom(self, chatroom_id: int, room_type: int) -> bool:
        # 待实现
        pass

    async def heartbeat(self):
        request = BLCPData(serviceId=1, methodId=3)
        request.RpcBody = self.buildRpcBody(serviceId=1, methodId=3, correlationId=request.correlationId)
        LcmBody = Lcm_pb2.RpcData()
        LcmBody.lcm_request.log_id = request.correlationId
        LcmBody.lcm_request.timestamp = request.timestamp
        request.LcmBody = LcmBody.SerializeToString()
        self.writer.write(request.toBytes())

    async def enter_chatroom_client_request(
        self, cuid_galaxy2: str, room_id: int, account_type: int = 1
    ):  # 模拟正常请求，暂不清楚作用
        headers = {
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.11.0",
            "Host": "pim.baidu.com",
            "Cookie": "BDUSS=" + self.account.BDUSS,
        }
        data = {
            "appid": CHAT_APPID,
            "room_id": room_id,
            "app_version": CHAT_VERSION,
            "cuid": cuid_galaxy2,
            "device_id": cuid_galaxy2,
            "sdk_version": CHAT_SDK_VERSION,
            "timestamp": int(time.time()),
            "account_type": account_type,
        }
        data["sign"] = generate_sign(data)

        request = aiohttp.ClientRequest(
            "POST",
            yarl.URL.build(
                scheme="https", host="pim.baidu.com", path="/rest/3.0/im/chatroom/enter_chatroom_client", port=443
            ),
            headers=headers,
            # proxy=self.net_core.proxy.url,
            # proxy_auth=self.net_core.proxy.auth,
            # ssl=False,
            data=json.dumps(data),
        )  # todo: 支持代理

        try:
            response = await self.net_core.req2res(request, False, 2 * 1024)
            await response.read()
            rjson = await response.json()
        except:
            raise Exception("进入群聊失败.")
        return rjson

    async def fetch_mcast_msg_client_request(
        self, cuid_galaxy2: str, room_id: int, account_type: int = 1
    ):  # 该方法可以获取历史消息，暂未继续开发
        headers = {
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.11.0",
            "Host": "pim.baidu.com",
            "Cookie": "BDUSS=" + self.account.BDUSS,
        }
        data = {
            "appid": CHAT_APPID,
            "mcast_id": room_id,
            "msgid_begin": 0,
            "msgid_end": 9223372036854775807,
            "count": -60,
            "category": 4,
            "app_version": CHAT_VERSION,
            "sdk_version": CHAT_SDK_VERSION,
            "device_id": cuid_galaxy2,
            "device_type": 2,
            "from_action": 1,
            "ext_info": urllib.parse.quote(
                json.dumps({"last_callback_msg_id": 0, "cast_id": 0, "local_ts": 0, "latest_msg_id": 0})
            ),
            "timestamp": int(time.time()),
            "account_type": account_type,
        }
        data["sign"] = generate_sign(data)

        request = aiohttp.ClientRequest(
            "POST",
            yarl.URL.build(scheme="https", host="pim.baidu.com", path="/rest/3.0/im/fetch_mcast_msg_client", port=443),
            headers=headers,
            # proxy=self.net_core.proxy.url,
            # proxy_auth=self.net_core.proxy.auth,
            # ssl=False,
            data=json.dumps(data),
        )  # todo: 支持代理

        try:
            response = await self.net_core.req2res(request, False, 2 * 1024)
            await response.read()
            rjson = await response.json()
        except:
            raise Exception("进入群聊失败.")
        return rjson


def generate_sign(json_obj):
    if json_obj is None:
        return ""

    # 按照字典序排序键值对
    sorted_items = sorted(json_obj.items())

    # 构造签名字符串
    sign_str = "".join(f"{key}={value}" for key, value in sorted_items)

    # 计算MD5签名
    return md5(sign_str.encode("utf-8")).hexdigest()


@dcs.dataclass
class BLCPData:
    serviceId: int
    methodId: int
    RpcBody: bytes
    LcmBody: bytes
    timestamp: int
    ifRequest: bool
    correlationId: int
    isNotify: bool

    def __init__(
        self,
        serviceId: int,
        methodId: int,
        RpcBody: bytes = None,
        LcmBody: bytes = None,
        timestamp: int = None,
        ifRequest: bool = True,
        isNotify: bool = False,
    ):
        self.serviceId = serviceId
        self.methodId = methodId
        self.RpcBody = RpcBody
        self.ifRequest = ifRequest
        self.LcmBody = LcmBody
        self.isNotify = isNotify

        if timestamp is None:
            self.timestamp = int(time.time() * 1000)
        else:
            self.timestamp = timestamp

        self.correlationId = random.randint(0, LongMax)

    def toBytes(self):
        buffer = bytearray()
        buffer.extend(b"lcp\x01")
        buffer.extend(int.to_bytes(len(self.RpcBody) + len(self.LcmBody), 4, "big"))
        buffer.extend(int.to_bytes(len(self.RpcBody), 4, "big"))
        buffer.extend(self.RpcBody)
        buffer.extend(self.LcmBody)

        return bytes(buffer)


class ClientBLCPResponses:
    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.reader = reader
        self.writer = writer

    def __aiter__(self) -> ClientBLCPResponses:
        return self

    async def __anext__(self):
        rBytes = bytearray()
        try:
            rBytes += await self.reader.readuntil(b"lcp\x01")
        except IncompleteReadError:
            raise StopAsyncIteration("BLCP连接被关闭")  # 连接被关闭，reader会得到EOF返回空字节而不是阻塞。
        else:
            length_bytes = await self.reader.read(8)
            rBytes += length_bytes
            all_length = int.from_bytes(length_bytes[0:4], byteorder="big")
            rBytes += await self.reader.read(all_length)

        try:
            RpcMeta, Lcm = self.parseBLCPResponse(rBytes)
        except:
            return None
        RpcMeta: Rpc_pb2.RpcMeta
        if not RpcMeta or not Lcm:
            return None
        service_id = RpcMeta.response.service_id
        method_id = RpcMeta.response.method_id
        correlation_id = RpcMeta.correlation_id

        responseBLCP = BLCPData(serviceId=service_id, methodId=method_id)
        responseBLCP.correlationId = correlation_id
        responseBLCP.RpcBody = RpcMeta.SerializeToString()
        if RpcMeta.notify and (method_id != 3 and service_id != 1):  # 屏蔽心跳包
            responseBLCP.isNotify = True

        if isinstance(Lcm, Lcm_pb2.RpcData):
            responseBLCP.LcmBody = Lcm.SerializeToString()
        else:
            responseBLCP.LcmBody = json.dumps(Lcm).encode()  # todo:这里又编码回字节了，性能浪费
        responseBLCP.ifRequest = False

        return responseBLCP

    async def __aenter__(self) -> ClientBLCPResponses:
        return self

    async def __aexit__(self) -> None:
        await self.close()

    async def close(self):
        pass

    @staticmethod
    def parseBLCPResponse(receivedBytes: bytes) -> (Rpc_pb2.RpcMeta, Lcm_pb2.RpcData):
        if len(receivedBytes) < 4:
            return None, None
        if receivedBytes[0:4] != b"lcp\x01":
            return None, None

        # 跳过lcp和1
        receivedBytes = receivedBytes[4:]
        b1 = int.from_bytes(receivedBytes[0:4], byteorder="big")
        b2 = int.from_bytes(receivedBytes[4:8], byteorder="big")
        receivedBytes = receivedBytes[8:]

        barr1 = receivedBytes[0:b2]
        barr2 = receivedBytes[b2:b1]

        Rpc: Rpc_pb2.RpcMeta = Rpc_pb2.RpcMeta()
        Rpc.ParseFromString(barr1)

        # todo: 优化Lcm消息类型判别，目前try处理比较暴力
        try:
            Lcm = Lcm_pb2.RpcData()
            Lcm.ParseFromString(barr2)
        except:
            try:
                Lcm = Lcm_pb2.RpcData()
                Lcm.ParseFromString(gzip.decompress(barr2))
            except:
                try:
                    Lcm = json.loads(barr2)
                except:
                    try:
                        Lcm = json.loads(gzip.decompress(barr2))
                    except:
                        raise ValueError("无法解析数据")

        return Rpc, Lcm


@dcs.dataclass
class BLCPResponse:
    """
    BLCP响应

    Args:
        future (asyncio.Future): 用于等待读事件到来的Future
        req_id (int): 请求id
        read_timeout (float): 读超时时间
    """

    loop: asyncio.AbstractEventLoop
    future: asyncio.Future
    req_id: int
    read_timeout: float

    def __init__(self, req_id: int, read_timeout: float) -> None:
        self.loop = asyncio.get_running_loop()
        self.future = self.loop.create_future()
        self.req_id = req_id
        self.read_timeout = read_timeout

    async def read(self) -> BLCPData:
        """
        读取BLCP响应

        Returns:
            BLCPData

        Raises:
            asyncio.TimeoutError: 读取超时
        """

        try:
            async with timeout(self.read_timeout, self.loop):
                return await self.future
        except asyncio.TimeoutError as err:
            self.future.cancel()
            raise asyncio.TimeoutError("Timeout to read") from err
        except BaseException:
            self.future.cancel()
            raise


@dcs.dataclass
class BLCPWaiter:
    """
    BLCP等待映射
    """

    loop: asyncio.AbstractEventLoop
    waiter: weakref.WeakValueDictionary
    req_id: int
    read_timeout: float

    def __init__(self, read_timeout: float) -> None:
        self.loop = asyncio.get_running_loop()
        self.waiter = weakref.WeakValueDictionary()
        self.req_id = int(time.time())
        self.read_timeout = read_timeout
        weakref.finalize(self, self.__cancel_all)

    def __cancel_all(self) -> None:
        for ws_resp in self.waiter.values():
            ws_resp.future.cancel()

    def new(self, req_id: int = None) -> BLCPResponse:
        """
        创建一个可用于等待数据的响应对象

        Args:
            req_id (int): 请求id

        Returns:
            WsResponse: websocket响应
        """
        if not req_id:
            self.req_id += 1
        else:
            self.req_id = req_id

        blcp_resp = BLCPResponse(self.req_id, self.read_timeout)
        self.waiter[self.req_id] = blcp_resp
        return blcp_resp

    def set_done(self, req_id: int, data: BLCPData) -> None:
        """
        将req_id对应的响应Future设置为已完成

        Args:
            req_id (int): 请求id
            data (bytes): 填入的数据
        """

        blcp_resp: BLCPResponse = self.waiter.get(req_id, None)
        if blcp_resp is None:
            return
        blcp_resp.future.set_result(data)
