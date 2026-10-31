from __future__ import annotations

import dataclasses as dcs
import gzip
import json
import random
import time
from sys import maxsize as LONG_MAX
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Self, cast

from ...api._protobuf import Lcm_pb2, Rpc_pb2
from ...helper import parse_json
from .enums import BlcpMetaType, BlcpServiceID, CompressType
from .exception import BlcpProtocolError

if TYPE_CHECKING:
    from asyncio import StreamReader

BLCP_FRAME_PREFIX = b"lcp\x01"
"""BLCP帧前缀 最后一位为协议版本号 线上magic仍为lcp"""


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
class BlcpRequestMeta:
    """
    BLCP请求元信息
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
class BlcpResponseMeta:
    """
    BLCP响应元信息
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
class BlcpNotifyMeta:
    """
    BLCP推送元信息
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


class TypeBlcpBody(Protocol):
    """
    报文体类型 负责自身的序列化
    """

    def encode(self) -> bytes:
        """
        将报文体序列化为字节

        Returns:
            bytes: 报文体
        """

        ...


@dcs.dataclass
class BlcpHeader:
    """
    帧头 描述一次BLCP调用的元信息

    Note:
        底层protobuf沿用app反编译结果的RpcMeta命名

    Attributes:
        meta_type (BlcpMetaType): meta类型
        meta (BlcpRequestMeta | BlcpResponseMeta | BlcpNotifyMeta): 请求/响应/推送元信息
        correlation_id (int): 请求id 响应会原样回传
        compress_type (CompressType): 报文体压缩类型
        accept_compress_type (CompressType): 期望的响应压缩类型
    """

    meta_type: BlcpMetaType
    meta: BlcpRequestMeta | BlcpResponseMeta | BlcpNotifyMeta
    correlation_id: int = 0
    compress_type: CompressType = CompressType.NONE
    accept_compress_type: CompressType = CompressType.GZIP

    def __post_init__(self) -> None:
        self.meta_type = BlcpMetaType(self.meta_type)
        expected_type = {
            BlcpMetaType.REQUEST: BlcpRequestMeta,
            BlcpMetaType.RESPONSE: BlcpResponseMeta,
            BlcpMetaType.NOTIFY: BlcpNotifyMeta,
        }[self.meta_type]
        if not isinstance(self.meta, expected_type):
            raise BlcpProtocolError(f"meta类型不匹配: {self.meta_type!r} {type(self.meta).__name__}")

    @property
    def service_id(self) -> int:
        return self.meta.service_id

    @property
    def method_id(self) -> int:
        return self.meta.method_id

    @property
    def log_id(self) -> int:
        return self.meta.log_id

    def to_proto(self) -> Rpc_pb2.RpcMeta:
        proto = Rpc_pb2.RpcMeta()
        if self.meta_type is BlcpMetaType.REQUEST:
            proto.request.CopyFrom(self.meta.to_proto())
        elif self.meta_type is BlcpMetaType.RESPONSE:
            proto.response.CopyFrom(self.meta.to_proto())
        elif self.meta_type is BlcpMetaType.NOTIFY:
            proto.notify.CopyFrom(self.meta.to_proto())
        proto.compress_type = self.compress_type
        proto.correlation_id = self.correlation_id
        proto.accept_compress_type = self.accept_compress_type
        return proto

    @classmethod
    def from_proto(cls, proto: Rpc_pb2.RpcMeta) -> Self:
        """
        从protobuf解析帧头

        Args:
            proto (Rpc_pb2.RpcMeta): 帧头

        Returns:
            BlcpHeader: 帧头
        """

        correlation_id = proto.correlation_id
        compress_type = CompressType(proto.compress_type)

        if proto.HasField("notify"):
            meta_type = BlcpMetaType.NOTIFY
            meta = BlcpNotifyMeta.from_proto(proto.notify)
        elif proto.HasField("response"):
            meta_type = BlcpMetaType.RESPONSE
            meta = BlcpResponseMeta.from_proto(proto.response)
        elif proto.HasField("request"):
            meta_type = BlcpMetaType.REQUEST
            meta = BlcpRequestMeta.from_proto(proto.request)
        else:
            meta_type = BlcpMetaType.RESPONSE
            meta = BlcpResponseMeta()

        return cls(meta_type, meta, correlation_id, compress_type)

    def encode(self) -> bytes:
        return self.to_proto().SerializeToString()

    @classmethod
    def decode(cls, data: bytes) -> Self:
        proto = Rpc_pb2.RpcMeta()
        proto.ParseFromString(data)
        return cls.from_proto(proto)


class TypeBlcpMsg(Protocol):
    """
    BLCP报文类型 帧头与报文体的组合
    """

    header: BlcpHeader
    body: TypeBlcpBody


@dcs.dataclass
class ProtoLcmBody:
    """
    LCM控制面报文体 protobuf编码 底层为app的RpcData
    """

    data: Lcm_pb2.RpcData

    def encode(self) -> bytes:
        return self.data.SerializeToString()

    @classmethod
    def from_proto(cls, proto: Lcm_pb2.RpcData) -> Self:
        """
        从protobuf构造报文体

        Args:
            proto (Lcm_pb2.RpcData): LCM报文体

        Returns:
            ProtoLcmBody: 报文体
        """

        return cls(proto)

    @classmethod
    def decode(cls, data: bytes) -> Self:
        rpc_data = Lcm_pb2.RpcData()
        rpc_data.ParseFromString(data)
        return cls.from_proto(rpc_data)

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
class JsonBody:
    """
    BLCP业务面报文体 json编码
    """

    data: dict[str, Any]

    def encode(self) -> bytes:
        return json.dumps(self.data, ensure_ascii=False).encode()

    @classmethod
    def decode(cls, data: bytes) -> Self:
        return cls(parse_json(data))


@dcs.dataclass
class BytesBody:
    """
    原始字节报文体 用于无内容的请求
    """

    data: bytes = b""

    def encode(self) -> bytes:
        return self.data

    @classmethod
    def decode(cls, data: bytes) -> Self:
        return cls(data)


def _decode_body(header: BlcpHeader, data: bytes) -> TypeBlcpBody:
    if header.compress_type == CompressType.GZIP:
        data = gzip.decompress(data)

    # 控制面使用protobuf 业务面使用json
    body_type = ProtoLcmBody if header.service_id == BlcpServiceID.LCM else JsonBody
    return body_type.decode(data)


@dcs.dataclass
class BlcpFrame:
    """
    BLCP帧 负责帧头与报文体的拼装和拆解

    Attributes:
        header (bytes): 帧头 BlcpHeader的序列化结果
        body (bytes): 报文体
    """

    header: bytes
    body: bytes

    @classmethod
    def from_msg(cls, msg: TypeBlcpMsg) -> Self:
        """
        从报文创建帧

        Args:
            msg (TypeBlcpMsg): 报文

        Returns:
            BlcpFrame: 帧
        """

        return cls(msg.header.encode(), msg.body.encode())

    def encode(self) -> bytes:
        """
        将帧序列化为字节

        Returns:
            bytes: 帧
        """

        header_len = len(self.header)
        total_len = header_len + len(self.body)
        return b"".join((
            BLCP_FRAME_PREFIX,
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
            BlcpFrame: 帧

        Raises:
            asyncio.IncompleteReadError: 连接被关闭
        """

        await reader.readuntil(BLCP_FRAME_PREFIX)
        lengths = await reader.readexactly(8)

        total_len = int.from_bytes(lengths[0:4], "big")
        header_len = int.from_bytes(lengths[4:8], "big")

        header = await reader.readexactly(header_len)
        body = await reader.readexactly(total_len - header_len)

        return cls(header, body)


@dcs.dataclass
class BlcpRequest:
    """
    请求报文

    Attributes:
        header (BlcpHeader): 帧头
        body (TypeBlcpBody): 报文体
    """

    header: BlcpHeader
    body: TypeBlcpBody

    @classmethod
    def from_frame(cls, frame: BlcpFrame) -> Self:
        """
        从帧反序列化为请求报文

        Args:
            frame (BlcpFrame): 帧

        Returns:
            BlcpRequest: 请求报文
        """

        header = BlcpHeader.decode(frame.header)
        body = _decode_body(header, frame.body)
        return cls(header, body)

    @classmethod
    def create(
        cls,
        service_id: int,
        method_id: int,
        body: TypeBlcpBody | None = None,
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
            body (TypeBlcpBody | None, optional): 报文体. Defaults to None.
            correlation_id (int | None, optional): 请求id 为空时随机生成. Defaults to None.
            need_common (int, optional): 是否需要公共参数. Defaults to 1.
            event (str | None, optional): 埋点事件名 为空则不添加. Defaults to "CLCPReqBegin".

        Returns:
            BlcpRequest: 请求报文
        """

        if correlation_id is None:
            correlation_id = random.randint(0, LONG_MAX)

        events = [EventTimestamp.now(event)] if event else []
        request_meta = BlcpRequestMeta(service_id, method_id, correlation_id, need_common, events)
        header = BlcpHeader(BlcpMetaType.REQUEST, request_meta, correlation_id)

        if body is None:
            body = BytesBody()

        return cls(header, body)

    @property
    def correlation_id(self) -> int:
        return self.header.correlation_id

    @property
    def service_id(self) -> int:
        return self.header.service_id

    @property
    def method_id(self) -> int:
        return self.header.method_id


@dcs.dataclass
class BlcpResponse:
    """
    响应报文

    Attributes:
        header (BlcpHeader): 帧头
        body (TypeBlcpBody): 报文体
    """

    header: BlcpHeader
    body: TypeBlcpBody

    @classmethod
    def from_frame(cls, frame: BlcpFrame) -> Self:
        """
        从帧反序列化为响应报文

        Args:
            frame (BlcpFrame): 帧

        Returns:
            BlcpResponse: 响应报文
        """

        header = BlcpHeader.decode(frame.header)
        body = _decode_body(header, frame.body)
        return cls(header, body)

    @property
    def correlation_id(self) -> int:
        return self.header.correlation_id

    @property
    def service_id(self) -> int:
        return self.header.service_id

    @property
    def method_id(self) -> int:
        return self.header.method_id

    @property
    def error_code(self) -> int:
        return self.header.meta.error_code

    @property
    def error_text(self) -> str:
        return self.header.meta.error_text

    @property
    def ok(self) -> bool:
        """
        是否成功 同时校验BLCP层与控制面错误码
        """

        if self.error_code != 0:
            return False

        lcm = self.lcm
        ok = lcm is None or lcm.error_code == 0
        return ok

    @property
    def lcm(self) -> Lcm_pb2.LcmResponse | None:
        """
        控制面响应 非控制面报文返回None
        """

        if isinstance(self.body, ProtoLcmBody):
            return self.body.data.lcm_response
        return None

    @property
    def payload(self) -> dict[str, Any]:
        """
        业务面响应内容
        """

        return cast("JsonBody", self.body).data


@dcs.dataclass
class BlcpNotify:
    """
    服务端推送报文

    Attributes:
        header (BlcpHeader): 帧头
        body (TypeBlcpBody): 报文体
    """

    header: BlcpHeader
    body: TypeBlcpBody

    @classmethod
    def from_frame(cls, frame: BlcpFrame) -> Self:
        """
        从帧反序列化为推送报文

        Args:
            frame (BlcpFrame): 帧

        Returns:
            BlcpNotify: 推送报文
        """

        header = BlcpHeader.decode(frame.header)
        body = _decode_body(header, frame.body)
        return cls(header, body)

    @property
    def service_id(self) -> int:
        return self.header.service_id

    @property
    def method_id(self) -> int:
        return self.header.method_id

    @property
    def log_id(self) -> int:
        return self.header.log_id

    @property
    def payload(self) -> dict[str, Any]:
        """
        推送内容
        """

        return cast("JsonBody", self.body).data


class BlcpMsgFactory:
    """
    BLCP报文工厂 依据帧头类型动态生成对应类型的报文
    """

    _MSG_TYPES: ClassVar[dict[BlcpMetaType, type[BlcpRequest] | type[BlcpResponse] | type[BlcpNotify]]] = {
        BlcpMetaType.REQUEST: BlcpRequest,
        BlcpMetaType.RESPONSE: BlcpResponse,
        BlcpMetaType.NOTIFY: BlcpNotify,
    }

    @classmethod
    def from_frame(cls, frame: BlcpFrame) -> TypeBlcpMsg:
        """
        从帧动态生成报文

        Args:
            frame (BlcpFrame): 帧

        Returns:
            TypeBlcpMsg: 报文
        """

        header = BlcpHeader.decode(frame.header)
        msg_type = cls._MSG_TYPES[header.meta_type]
        return msg_type.from_frame(frame)
