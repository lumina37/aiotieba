from ..._protobuf import Error_pb2 as _Error_pb2
from ..._protobuf import User_pb2 as _User_pb2
from ..._protobuf import PostInfoList_pb2 as _PostInfoList_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProfileResIdl(_message.Message):
    __slots__ = ("error", "data")
    class DataRes(_message.Message):
        __slots__ = ("user", "anti_stat", "post_list", "user_agree_info")
        class Anti(_message.Message):
            __slots__ = ("block_stat", "hide_stat", "days_tofree")
            BLOCK_STAT_FIELD_NUMBER: _ClassVar[int]
            HIDE_STAT_FIELD_NUMBER: _ClassVar[int]
            DAYS_TOFREE_FIELD_NUMBER: _ClassVar[int]
            block_stat: int
            hide_stat: int
            days_tofree: int
            def __init__(self, block_stat: _Optional[int] = ..., hide_stat: _Optional[int] = ..., days_tofree: _Optional[int] = ...) -> None: ...
        class UserAgreeInfo(_message.Message):
            __slots__ = ("total_agree_num",)
            TOTAL_AGREE_NUM_FIELD_NUMBER: _ClassVar[int]
            total_agree_num: int
            def __init__(self, total_agree_num: _Optional[int] = ...) -> None: ...
        USER_FIELD_NUMBER: _ClassVar[int]
        ANTI_STAT_FIELD_NUMBER: _ClassVar[int]
        POST_LIST_FIELD_NUMBER: _ClassVar[int]
        USER_AGREE_INFO_FIELD_NUMBER: _ClassVar[int]
        user: _User_pb2.User
        anti_stat: ProfileResIdl.DataRes.Anti
        post_list: _containers.RepeatedCompositeFieldContainer[_PostInfoList_pb2.PostInfoList]
        user_agree_info: ProfileResIdl.DataRes.UserAgreeInfo
        def __init__(self, user: _Optional[_Union[_User_pb2.User, _Mapping]] = ..., anti_stat: _Optional[_Union[ProfileResIdl.DataRes.Anti, _Mapping]] = ..., post_list: _Optional[_Iterable[_Union[_PostInfoList_pb2.PostInfoList, _Mapping]]] = ..., user_agree_info: _Optional[_Union[ProfileResIdl.DataRes.UserAgreeInfo, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    error: _Error_pb2.Error
    data: ProfileResIdl.DataRes
    def __init__(self, error: _Optional[_Union[_Error_pb2.Error, _Mapping]] = ..., data: _Optional[_Union[ProfileResIdl.DataRes, _Mapping]] = ...) -> None: ...
