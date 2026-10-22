from __future__ import annotations

import abc
import dataclasses as dcs
import gzip
import json
import random
import time
from sys import maxsize as LONG_MAX
from typing import TYPE_CHECKING, Any, Self

from ...api._protobuf import Lcm_pb2, Rpc_pb2
from ...helper import parse_json
from .enums import BLCPServiceID, CompressType
from .exception import BLCPProtocolError

if TYPE_CHECKING:
    from asyncio import StreamReader

FRAME_PREFIX = b"lcp\x01"
"""帧前缀 最后一位为协议版本号"""


@dcs.dataclass
class EventTimestamp:
    """
    链路埋点事件

    Attributes:
        event (str): 事件名 如 CLCPReqBegin
        timestamp_ms (int): 毫秒时间戳
    """

    event: str
    timestamp_ms: int

    @classmethod
    def now(cls, event: str) -> Self:
        """
        以当前时间创建一个事件

        Args:
            event (str): 事件名

        Returns:
            EventTimestamp: 事件
        """

        return cls(event, int(time.time() * 1000))


@dcs.dataclass
class RpcRequestMeta:
    """
    RPC请求元信息
    """

    service_id: int
    method_id: int
    log_id: int = 0
    need_common: int = 1
    events: list[EventTimestamp] = dcs.field(default_factory=list)

    def to_proto(self) -> Rpc_pb2.RpcRequestMeta:
        proto = Rpc_pb2.RpcRequestMeta()
        proto.service_id = self.service_id
        proto.method_id = self.method_id
        proto.log_id = self.log_id
        proto.need_common = self.need_common
        for event in self.events:
            item = proto.event_list.add()
            item.event = event.event
            item.timestamp_ms = event.timestamp_ms
        return proto

    @classmethod
    def from_proto(cls, proto: Rpc_pb2.RpcRequestMeta) -> Self:
        events = [EventTimestamp(item.event, item.timestamp_ms) for item in proto.event_list]
        return cls(proto.service_id, proto.method_id, proto.log_id, proto.need_common, events)


@dcs.dataclass
class RpcResponseMeta:
    """
    RPC响应元信息
    """

    service_id: int = 0
    method_id: int = 0
    log_id: int = 0
    error_code: int = 0
    error_text: str = ""
    events: list[EventTimestamp] = dcs.field(default_factory=list)

    def to_proto(self) -> Rpc_pb2.RpcResponseMeta:
        proto = Rpc_pb2.RpcResponseMeta()
        proto.service_id = self.service_id
        proto.method_id = self.method_id
        proto.log_id = self.log_id
        proto.error_code = self.error_code
        proto.error_text = self.error_text
        for event in self.events:
            item = proto.event_list.add()
            item.event = event.event
            item.timestamp_ms = event.timestamp_ms
        return proto

    @classmethod
    def from_proto(cls, proto: Rpc_pb2.RpcResponseMeta) -> Self:
        events = [EventTimestamp(item.event, item.timestamp_ms) for item in proto.event_list]
        return cls(proto.service_id, proto.method_id, proto.log_id, proto.error_code, proto.error_text, events)


@dcs.dataclass
class RpcNotifyMeta:
    """
    RPC推送元信息
    """

    service_id: int = 0
    method_id: int = 0
    log_id: int = 0
    events: list[EventTimestamp] = dcs.field(default_factory=list)

    def to_proto(self) -> Rpc_pb2.RpcNotifyMeta:
        proto = Rpc_pb2.RpcNotifyMeta()
        proto.service_id = self.service_id
        proto.method_id = self.method_id
        proto.log_id = self.log_id
        for event in self.events:
            item = proto.event_list.add()
            item.event = event.event
            item.timestamp_ms = event.timestamp_ms
        return proto

    @classmethod
    def from_proto(cls, proto: Rpc_pb2.RpcNotifyMeta) -> Self:
        events = [EventTimestamp(item.event, item.timestamp_ms) for item in proto.event_list]
        return cls(proto.service_id, proto.method_id, proto.log_id, events)


@dcs.dataclass
class RpcMeta:
    """
    帧头 描述一次RPC的元信息

    Attributes:
        correlation_id (int): 请求id 响应会原样回传
        request (RpcRequestMeta | None): 请求元信息
        response (RpcResponseMeta | None): 响应元信息
        notify (RpcNotifyMeta | None): 推送元信息
        compress_type (CompressType): 报文体压缩类型
        accept_compress_type (CompressType): 期望的响应压缩类型
    """

    correlation_id: int = 0
    request: RpcRequestMeta | None = None
    response: RpcResponseMeta | None = None
    notify: RpcNotifyMeta | None = None
    compress_type: CompressType = CompressType.NONE
    accept_compress_type: CompressType = CompressType.GZIP

    @property
    def is_request(self) -> bool:
        return self.request is not None

    @property
    def is_response(self) -> bool:
        return self.response is not None

    @property
    def is_notify(self) -> bool:
        return self.notify is not None

    @property
    def __inner(self) -> RpcRequestMeta | RpcResponseMeta | RpcNotifyMeta | None:
        if self.response is not None:
            return self.response
        if self.notify is not None:
            return self.notify
        return self.request

    @property
    def service_id(self) -> int:
        return self.__inner.service_id

    @property
    def method_id(self) -> int:
        return self.__inner.method_id

    @property
    def log_id(self) -> int:
        return self.__inner.log_id

    def to_proto(self) -> Rpc_pb2.RpcMeta:
        proto = Rpc_pb2.RpcMeta()
        if self.request is not None:
            proto.request.CopyFrom(self.request.to_proto())
        if self.response is not None:
            proto.response.CopyFrom(self.response.to_proto())
        if self.notify is not None:
            proto.notify.CopyFrom(self.notify.to_proto())
        proto.compress_type = self.compress_type
        proto.correlation_id = self.correlation_id
        proto.accept_compress_type = self.accept_compress_type
        return proto

    @classmethod
    def from_proto(cls, proto: Rpc_pb2.RpcMeta) -> Self:
        return cls(
            correlation_id=proto.correlation_id,
            request=RpcRequestMeta.from_proto(proto.request) if proto.HasField("request") else None,
            response=RpcResponseMeta.from_proto(proto.response) if proto.HasField("response") else None,
            notify=RpcNotifyMeta.from_proto(proto.notify) if proto.HasField("notify") else None,
            compress_type=CompressType(proto.compress_type),
            accept_compress_type=CompressType(proto.accept_compress_type),
        )

    def encode(self) -> bytes:
        return self.to_proto().SerializeToString()

    @classmethod
    def decode(cls, data: bytes) -> Self:
        proto = Rpc_pb2.RpcMeta()
        proto.ParseFromString(data)
        return cls.from_proto(proto)


class BLCPBody(abc.ABC):
    """
    报文体的抽象基类 负责自身的序列化与反序列化
    """

    @abc.abstractmethod
    def encode(self) -> bytes:
        """
        将报文体序列化为字节

        Returns:
            bytes: 报文体
        """

    @classmethod
    @abc.abstractmethod
    def decode(cls, data: bytes) -> Self:
        """
        从字节反序列化为报文体

        Args:
            data (bytes): 报文体

        Returns:
            Self: 报文体对象
        """

    @classmethod
    def decode_for(cls, meta: RpcMeta, data: bytes) -> BLCPBody:
        """
        依据帧头选择报文体类型并反序列化

        Args:
            meta (RpcMeta): 帧头
            data (bytes): 原始报文体

        Returns:
            BLCPBody: 报文体对象
        """

        if meta.compress_type == CompressType.GZIP:
            data = gzip.decompress(data)

        # 控制面使用protobuf 业务面使用json
        body_type: type[BLCPBody] = LcmBody if meta.service_id == BLCPServiceID.LCM else JsonBody
        return body_type.decode(data)


@dcs.dataclass
class LcmBody(BLCPBody):
    """
    LCP控制面报文体 protobuf编码
    """

    data: Lcm_pb2.RpcData

    def encode(self) -> bytes:
        return self.data.SerializeToString()

    @classmethod
    def decode(cls, data: bytes) -> Self:
        rpc_data = Lcm_pb2.RpcData()
        rpc_data.ParseFromString(data)
        return cls(rpc_data)

    @classmethod
    def login(
        cls,
        *,
        log_id: int,
        token: str,
        timestamp: int,
        cuid: str,
        app_id: int,
        app_version: str,
        sdk_version: str,
        network: str = "wifi",
        device_type: str = "android",
        start_type: int = -1,
        conn_type: int = 1,
    ) -> Self:
        """
        构造LCM登录请求

        Args:
            log_id (int): 请求id
            token (str): LCP token
            timestamp (int): 毫秒时间戳
            cuid (str): 设备标识
            app_id (int): appid
            app_version (str): 客户端版本
            sdk_version (str): LCP SDK版本
            network (str, optional): 网络类型. Defaults to "wifi".
            device_type (str, optional): 设备类型. Defaults to "android".
            start_type (int, optional): 启动类型. Defaults to -1.
            conn_type (int, optional): 连接类型. Defaults to 1.

        Returns:
            LcmBody: 报文体
        """

        rpc_data = Lcm_pb2.RpcData()
        request = rpc_data.lcm_request
        request.log_id = log_id
        request.token = token
        request.timestamp = timestamp
        request.start_type = start_type
        request.conn_type = conn_type
        common = request.common
        common.cuid = cuid
        common.device = device_type
        common.app_id = str(app_id)
        common.app_version = app_version
        common.sdk_version = sdk_version
        common.network = network
        return cls(rpc_data)

    @classmethod
    def heartbeat(cls, *, log_id: int, timestamp: int) -> Self:
        """
        构造LCM心跳请求

        Args:
            log_id (int): 请求id
            timestamp (int): 毫秒时间戳

        Returns:
            LcmBody: 报文体
        """

        rpc_data = Lcm_pb2.RpcData()
        rpc_data.lcm_request.log_id = log_id
        rpc_data.lcm_request.timestamp = timestamp
        return cls(rpc_data)

    @classmethod
    def logout(cls, *, log_id: int, timestamp: int) -> Self:
        """
        构造LCM登出请求

        Args:
            log_id (int): 请求id
            timestamp (int): 毫秒时间戳

        Returns:
            LcmBody: 报文体
        """

        rpc_data = Lcm_pb2.RpcData()
        rpc_data.lcm_request.log_id = log_id
        rpc_data.lcm_request.timestamp = timestamp
        return cls(rpc_data)

    @property
    def response(self) -> Lcm_pb2.LcmResponse:
        """
        LCM响应
        """

        return self.data.lcm_response

    @property
    def next_interval_ms(self) -> int:
        """
        服务端期望的下一次心跳间隔 单位毫秒
        """

        return self.data.lcm_response.next_interval_ms


@dcs.dataclass
class JsonBody(BLCPBody):
    """
    LCP业务面报文体 json编码
    """

    data: dict[str, Any]

    def encode(self) -> bytes:
        return json.dumps(self.data, ensure_ascii=False).encode()

    @classmethod
    def decode(cls, data: bytes) -> Self:
        return cls(parse_json(data))


@dcs.dataclass
class BytesBody(BLCPBody):
    """
    原始字节报文体 用于无内容的请求
    """

    data: bytes = b""

    def encode(self) -> bytes:
        return self.data

    @classmethod
    def decode(cls, data: bytes) -> Self:
        return cls(data)


@dcs.dataclass
class LCPFrame:
    """
    LCP帧 负责帧头与报文体的拼装和拆解

    Attributes:
        header (bytes): 帧头 RpcMeta的序列化结果
        body (bytes): 报文体
    """

    header: bytes
    body: bytes

    def encode(self) -> bytes:
        """
        将帧序列化为字节

        Returns:
            bytes: 帧
        """

        header_len = len(self.header)
        total_len = header_len + len(self.body)
        return b"".join((
            FRAME_PREFIX,
            total_len.to_bytes(4, "big"),
            header_len.to_bytes(4, "big"),
            self.header,
            self.body,
        ))

    @classmethod
    async def read_from(cls, reader: StreamReader) -> Self:
        """
        从数据流读取一个完整的帧

        Args:
            reader (StreamReader): 数据流

        Returns:
            LCPFrame: 帧

        Raises:
            asyncio.IncompleteReadError: 连接被关闭
        """

        await reader.readuntil(FRAME_PREFIX)
        lengths = await reader.readexactly(8)

        total_len = int.from_bytes(lengths[0:4], "big")
        header_len = int.from_bytes(lengths[4:8], "big")

        header = await reader.readexactly(header_len)
        body = await reader.readexactly(total_len - header_len)

        return cls(header, body)


@dcs.dataclass
class BLCPPacket:
    """
    LCP报文 帧头与报文体的组合

    Attributes:
        meta (RpcMeta): 帧头
        body (BLCPBody): 报文体
    """

    meta: RpcMeta
    body: BLCPBody

    def to_frame(self) -> LCPFrame:
        """
        转换为帧

        Returns:
            LCPFrame: 帧
        """

        return LCPFrame(self.meta.encode(), self.body.encode())

    def to_bytes(self) -> bytes:
        """
        序列化为可直接发送的字节

        Returns:
            bytes: 帧
        """

        return self.to_frame().encode()

    @classmethod
    def from_frame(cls, frame: LCPFrame) -> Self:
        """
        从帧反序列化为报文

        Args:
            frame (LCPFrame): 帧

        Returns:
            BLCPPacket: 报文 具体类型由帧头决定
        """

        meta = RpcMeta.decode(frame.header)
        body = BLCPBody.decode_for(meta, frame.body)

        if meta.is_request:
            return BLCPRequest(meta, body)
        if meta.is_response:
            return BLCPResponse(meta, body)
        return BLCPNotify(meta, body)


@dcs.dataclass
class BLCPRequest(BLCPPacket):
    """
    请求报文
    """

    @classmethod
    def create(
        cls,
        service_id: int,
        method_id: int,
        body: BLCPBody | None = None,
        *,
        correlation_id: int | None = None,
        need_common: int = 1,
        event: str | None = "CLCPReqBegin",
    ) -> Self:
        """
        创建一个请求报文

        Args:
            service_id (int): 服务号
            method_id (int): 方法号
            body (BLCPBody | None, optional): 报文体. Defaults to None.
            correlation_id (int | None, optional): 请求id 为空时随机生成. Defaults to None.
            need_common (int, optional): 是否需要公共参数. Defaults to 1.
            event (str | None, optional): 埋点事件名 为空则不添加. Defaults to "CLCPReqBegin".

        Returns:
            BLCPRequest: 请求报文
        """

        if correlation_id is None:
            correlation_id = random.randint(0, LONG_MAX)

        events = [EventTimestamp.now(event)] if event else []
        request_meta = RpcRequestMeta(service_id, method_id, correlation_id, need_common, events)
        meta = RpcMeta(correlation_id, request_meta)

        if body is None:
            body = BytesBody()

        return cls(meta, body)

    @property
    def correlation_id(self) -> int:
        return self.meta.correlation_id

    @property
    def service_id(self) -> int:
        return self.meta.request.service_id

    @property
    def method_id(self) -> int:
        return self.meta.request.method_id


@dcs.dataclass
class BLCPResponse(BLCPPacket):
    """
    响应报文
    """

    @property
    def correlation_id(self) -> int:
        return self.meta.correlation_id

    @property
    def service_id(self) -> int:
        return self.meta.response.service_id

    @property
    def method_id(self) -> int:
        return self.meta.response.method_id

    @property
    def error_code(self) -> int:
        return self.meta.response.error_code

    @property
    def error_text(self) -> str:
        return self.meta.response.error_text

    @property
    def ok(self) -> bool:
        """
        是否成功 同时校验RPC层与控制面错误码
        """

        if self.error_code != 0:
            return False

        lcm = self.lcm
        return lcm is None or lcm.error_code == 0

    @property
    def lcm(self) -> Lcm_pb2.LcmResponse | None:
        """
        控制面响应 非控制面报文返回None
        """

        if isinstance(self.body, LcmBody):
            return self.body.data.lcm_response
        return None

    @property
    def payload(self) -> dict[str, Any]:
        """
        业务面响应内容

        Raises:
            BLCPProtocolError: 报文体不是JSON
        """

        if isinstance(self.body, JsonBody):
            return self.body.data
        raise BLCPProtocolError(f"期望JSON报文体 实际为{type(self.body).__name__}")


@dcs.dataclass
class BLCPNotify(BLCPPacket):
    """
    服务端推送报文
    """

    @property
    def service_id(self) -> int:
        return self.meta.notify.service_id

    @property
    def method_id(self) -> int:
        return self.meta.notify.method_id

    @property
    def log_id(self) -> int:
        return self.meta.notify.log_id

    @property
    def payload(self) -> dict[str, Any]:
        """
        推送内容

        Raises:
            BLCPProtocolError: 报文体不是JSON
        """

        if isinstance(self.body, JsonBody):
            return self.body.data
        raise BLCPProtocolError(f"期望JSON报文体 实际为{type(self.body).__name__}")
