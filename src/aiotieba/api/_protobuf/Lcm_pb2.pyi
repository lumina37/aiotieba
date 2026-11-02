from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Common(_message.Message):
    __slots__ = ("cuid", "device", "os_version", "manufacture", "model_type", "app_id", "app_version", "sdk_version", "network", "rom_version", "user_key")
    CUID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    OS_VERSION_FIELD_NUMBER: _ClassVar[int]
    MANUFACTURE_FIELD_NUMBER: _ClassVar[int]
    MODEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    APP_ID_FIELD_NUMBER: _ClassVar[int]
    APP_VERSION_FIELD_NUMBER: _ClassVar[int]
    SDK_VERSION_FIELD_NUMBER: _ClassVar[int]
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    ROM_VERSION_FIELD_NUMBER: _ClassVar[int]
    USER_KEY_FIELD_NUMBER: _ClassVar[int]
    cuid: str
    device: str
    os_version: str
    manufacture: str
    model_type: str
    app_id: str
    app_version: str
    sdk_version: str
    network: str
    rom_version: str
    user_key: str
    def __init__(self, cuid: _Optional[str] = ..., device: _Optional[str] = ..., os_version: _Optional[str] = ..., manufacture: _Optional[str] = ..., model_type: _Optional[str] = ..., app_id: _Optional[str] = ..., app_version: _Optional[str] = ..., sdk_version: _Optional[str] = ..., network: _Optional[str] = ..., rom_version: _Optional[str] = ..., user_key: _Optional[str] = ...) -> None: ...

class LcmNotify(_message.Message):
    __slots__ = ("log_id", "action")
    LOG_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    log_id: int
    action: int
    def __init__(self, log_id: _Optional[int] = ..., action: _Optional[int] = ...) -> None: ...

class LcmRequest(_message.Message):
    __slots__ = ("log_id", "token", "common", "timestamp", "action", "start_type", "conn_type")
    LOG_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    COMMON_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    START_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONN_TYPE_FIELD_NUMBER: _ClassVar[int]
    log_id: int
    token: str
    common: Common
    timestamp: int
    action: int
    start_type: int
    conn_type: int
    def __init__(self, log_id: _Optional[int] = ..., token: _Optional[str] = ..., common: _Optional[_Union[Common, _Mapping]] = ..., timestamp: _Optional[int] = ..., action: _Optional[int] = ..., start_type: _Optional[int] = ..., conn_type: _Optional[int] = ...) -> None: ...

class LcmResponse(_message.Message):
    __slots__ = ("log_id", "error_code", "error_msg", "next_interval_ms", "server_info")
    LOG_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MSG_FIELD_NUMBER: _ClassVar[int]
    NEXT_INTERVAL_MS_FIELD_NUMBER: _ClassVar[int]
    SERVER_INFO_FIELD_NUMBER: _ClassVar[int]
    log_id: int
    error_code: int
    error_msg: str
    next_interval_ms: int
    server_info: str
    def __init__(self, log_id: _Optional[int] = ..., error_code: _Optional[int] = ..., error_msg: _Optional[str] = ..., next_interval_ms: _Optional[int] = ..., server_info: _Optional[str] = ...) -> None: ...

class RpcData(_message.Message):
    __slots__ = ("lcm_request", "lcm_response", "lcm_notify")
    LCM_REQUEST_FIELD_NUMBER: _ClassVar[int]
    LCM_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    LCM_NOTIFY_FIELD_NUMBER: _ClassVar[int]
    lcm_request: LcmRequest
    lcm_response: LcmResponse
    lcm_notify: LcmNotify
    def __init__(self, lcm_request: _Optional[_Union[LcmRequest, _Mapping]] = ..., lcm_response: _Optional[_Union[LcmResponse, _Mapping]] = ..., lcm_notify: _Optional[_Union[LcmNotify, _Mapping]] = ...) -> None: ...
