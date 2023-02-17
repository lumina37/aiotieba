"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2
from ..._protobuf import User_pb2 as User__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1dGetUserByTiebaUidResIdl.proto\x1a\x0b\x45rror.proto\x1a\nUser.proto\"\x80\x01\n\x17GetUserByTiebaUidResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12.\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32 .GetUserByTiebaUidResIdl.DataRes\x1a\x1e\n\x07\x44\x61taRes\x12\x13\n\x04user\x18\x01 \x01(\x0b\x32\x05.Userb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'GetUserByTiebaUidResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_GETUSERBYTIEBAUIDRESIDL']._serialized_start = 59
    _globals['_GETUSERBYTIEBAUIDRESIDL']._serialized_end = 187
    _globals['_GETUSERBYTIEBAUIDRESIDL_DATARES']._serialized_start = 157
    _globals['_GETUSERBYTIEBAUIDRESIDL_DATARES']._serialized_end = 187
