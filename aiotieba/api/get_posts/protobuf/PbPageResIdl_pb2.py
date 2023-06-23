"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2
from ..._protobuf import Page_pb2 as Page__pb2
from ..._protobuf import Post_pb2 as Post__pb2
from ..._protobuf import ThreadInfo_pb2 as ThreadInfo__pb2
from ..._protobuf import User_pb2 as User__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x12PbPageResIdl.proto\x1a\x0b\x45rror.proto\x1a\nPage.proto\x1a\nPost.proto\x1a\x10ThreadInfo.proto\x1a\nUser.proto\"\xd6\x02\n\x0cPbPageResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12#\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x15.PbPageResIdl.DataRes\x1a\x89\x02\n\x07\x44\x61taRes\x12\x30\n\x05\x66orum\x18\x02 \x01(\x0b\x32!.PbPageResIdl.DataRes.SimpleForum\x12\x13\n\x04page\x18\x03 \x01(\x0b\x32\x05.Page\x12\x18\n\tpost_list\x18\x06 \x03(\x0b\x32\x05.Post\x12\x1b\n\x06thread\x18\x08 \x01(\x0b\x32\x0b.ThreadInfo\x12\x18\n\tuser_list\x18\r \x03(\x0b\x32\x05.User\x12\x17\n\x0fthread_freq_num\x18% \x01(\x03\x1aM\n\x0bSimpleForum\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\nmember_num\x18\x0c \x01(\x05\x12\x10\n\x08post_num\x18\r \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'PbPageResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_PBPAGERESIDL']._serialized_start = 90
    _globals['_PBPAGERESIDL']._serialized_end = 432
    _globals['_PBPAGERESIDL_DATARES']._serialized_start = 167
    _globals['_PBPAGERESIDL_DATARES']._serialized_end = 432
    _globals['_PBPAGERESIDL_DATARES_SIMPLEFORUM']._serialized_start = 355
    _globals['_PBPAGERESIDL_DATARES_SIMPLEFORUM']._serialized_end = 432
