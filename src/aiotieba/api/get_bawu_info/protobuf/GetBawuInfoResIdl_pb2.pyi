from ..._protobuf import Error_pb2 as _Error_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetBawuInfoResIdl(_message.Message):
    __slots__ = ("data", "error")
    class DataRes(_message.Message):
        __slots__ = ("bawu_team_info",)
        class BawuTeam(_message.Message):
            __slots__ = ("total_num", "bawu_team_list")
            class BawuRoleDes(_message.Message):
                __slots__ = ("role_name", "role_info")
                class BawuRoleInfoPub(_message.Message):
                    __slots__ = ("user_id", "role_name", "portrait", "user_level", "user_name", "name_show")
                    USER_ID_FIELD_NUMBER: _ClassVar[int]
                    ROLE_NAME_FIELD_NUMBER: _ClassVar[int]
                    PORTRAIT_FIELD_NUMBER: _ClassVar[int]
                    USER_LEVEL_FIELD_NUMBER: _ClassVar[int]
                    USER_NAME_FIELD_NUMBER: _ClassVar[int]
                    NAME_SHOW_FIELD_NUMBER: _ClassVar[int]
                    user_id: int
                    role_name: str
                    portrait: str
                    user_level: int
                    user_name: str
                    name_show: str
                    def __init__(self, user_id: _Optional[int] = ..., role_name: _Optional[str] = ..., portrait: _Optional[str] = ..., user_level: _Optional[int] = ..., user_name: _Optional[str] = ..., name_show: _Optional[str] = ...) -> None: ...
                ROLE_NAME_FIELD_NUMBER: _ClassVar[int]
                ROLE_INFO_FIELD_NUMBER: _ClassVar[int]
                role_name: str
                role_info: _containers.RepeatedCompositeFieldContainer[GetBawuInfoResIdl.DataRes.BawuTeam.BawuRoleDes.BawuRoleInfoPub]
                def __init__(self, role_name: _Optional[str] = ..., role_info: _Optional[_Iterable[_Union[GetBawuInfoResIdl.DataRes.BawuTeam.BawuRoleDes.BawuRoleInfoPub, _Mapping]]] = ...) -> None: ...
            TOTAL_NUM_FIELD_NUMBER: _ClassVar[int]
            BAWU_TEAM_LIST_FIELD_NUMBER: _ClassVar[int]
            total_num: int
            bawu_team_list: _containers.RepeatedCompositeFieldContainer[GetBawuInfoResIdl.DataRes.BawuTeam.BawuRoleDes]
            def __init__(self, total_num: _Optional[int] = ..., bawu_team_list: _Optional[_Iterable[_Union[GetBawuInfoResIdl.DataRes.BawuTeam.BawuRoleDes, _Mapping]]] = ...) -> None: ...
        BAWU_TEAM_INFO_FIELD_NUMBER: _ClassVar[int]
        bawu_team_info: GetBawuInfoResIdl.DataRes.BawuTeam
        def __init__(self, bawu_team_info: _Optional[_Union[GetBawuInfoResIdl.DataRes.BawuTeam, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    data: GetBawuInfoResIdl.DataRes
    error: _Error_pb2.Error
    def __init__(self, data: _Optional[_Union[GetBawuInfoResIdl.DataRes, _Mapping]] = ..., error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ...) -> None: ...
