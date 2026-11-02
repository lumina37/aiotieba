from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChunkInfo(_message.Message):
    __slots__ = ("stream_id", "chunk_id")
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_ID_FIELD_NUMBER: _ClassVar[int]
    stream_id: int
    chunk_id: int
    def __init__(self, stream_id: _Optional[int] = ..., chunk_id: _Optional[int] = ...) -> None: ...

class EventTimestamp(_message.Message):
    __slots__ = ("event", "timestamp_ms")
    EVENT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    event: str
    timestamp_ms: int
    def __init__(self, event: _Optional[str] = ..., timestamp_ms: _Optional[int] = ...) -> None: ...

class RpcNotifyMeta(_message.Message):
    __slots__ = ("service_id", "method_id", "log_id", "event_list")
    SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    METHOD_ID_FIELD_NUMBER: _ClassVar[int]
    LOG_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_LIST_FIELD_NUMBER: _ClassVar[int]
    service_id: int
    method_id: int
    log_id: int
    event_list: _containers.RepeatedCompositeFieldContainer[EventTimestamp]
    def __init__(self, service_id: _Optional[int] = ..., method_id: _Optional[int] = ..., log_id: _Optional[int] = ..., event_list: _Optional[_Iterable[_Union[EventTimestamp, _Mapping]]] = ...) -> None: ...

class RpcRequestMeta(_message.Message):
    __slots__ = ("service_id", "method_id", "log_id", "need_common", "event_list")
    SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    METHOD_ID_FIELD_NUMBER: _ClassVar[int]
    LOG_ID_FIELD_NUMBER: _ClassVar[int]
    NEED_COMMON_FIELD_NUMBER: _ClassVar[int]
    EVENT_LIST_FIELD_NUMBER: _ClassVar[int]
    service_id: int
    method_id: int
    log_id: int
    need_common: int
    event_list: _containers.RepeatedCompositeFieldContainer[EventTimestamp]
    def __init__(self, service_id: _Optional[int] = ..., method_id: _Optional[int] = ..., log_id: _Optional[int] = ..., need_common: _Optional[int] = ..., event_list: _Optional[_Iterable[_Union[EventTimestamp, _Mapping]]] = ...) -> None: ...

class RpcResponseMeta(_message.Message):
    __slots__ = ("service_id", "method_id", "log_id", "error_code", "error_text", "event_list")
    SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    METHOD_ID_FIELD_NUMBER: _ClassVar[int]
    LOG_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_TEXT_FIELD_NUMBER: _ClassVar[int]
    EVENT_LIST_FIELD_NUMBER: _ClassVar[int]
    service_id: int
    method_id: int
    log_id: int
    error_code: int
    error_text: str
    event_list: _containers.RepeatedCompositeFieldContainer[EventTimestamp]
    def __init__(self, service_id: _Optional[int] = ..., method_id: _Optional[int] = ..., log_id: _Optional[int] = ..., error_code: _Optional[int] = ..., error_text: _Optional[str] = ..., event_list: _Optional[_Iterable[_Union[EventTimestamp, _Mapping]]] = ...) -> None: ...

class RpcMeta(_message.Message):
    __slots__ = ("request", "response", "compress_type", "correlation_id", "attachment_size", "chunk_info", "authentication_data", "notify", "accept_compress_type")
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    COMPRESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENT_SIZE_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INFO_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_DATA_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_COMPRESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    request: RpcRequestMeta
    response: RpcResponseMeta
    compress_type: int
    correlation_id: int
    attachment_size: int
    chunk_info: ChunkInfo
    authentication_data: bytes
    notify: RpcNotifyMeta
    accept_compress_type: int
    def __init__(self, request: _Optional[_Union[RpcRequestMeta, _Mapping]] = ..., response: _Optional[_Union[RpcResponseMeta, _Mapping]] = ..., compress_type: _Optional[int] = ..., correlation_id: _Optional[int] = ..., attachment_size: _Optional[int] = ..., chunk_info: _Optional[_Union[ChunkInfo, _Mapping]] = ..., authentication_data: _Optional[bytes] = ..., notify: _Optional[_Union[RpcNotifyMeta, _Mapping]] = ..., accept_compress_type: _Optional[int] = ...) -> None: ...
