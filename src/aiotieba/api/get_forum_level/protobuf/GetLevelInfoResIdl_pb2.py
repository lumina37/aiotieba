"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x18GetLevelInfoResIdl.proto\x1a\x0b\x45rror.proto"\x9a\x01\n\x12GetLevelInfoResIdl\x12\x15\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x06.Error\x12)\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x1b.GetLevelInfoResIdl.DataRes\x1a\x42\n\x07\x44\x61taRes\x12\x0f\n\x07is_like\x18\x02 \x01(\x05\x12\x12\n\nlevel_name\x18\x04 \x01(\t\x12\x12\n\nuser_level\x18\x03 \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "GetLevelInfoResIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_GETLEVELINFORESIDL"]._serialized_start = 42
    _globals["_GETLEVELINFORESIDL"]._serialized_end = 196
    _globals["_GETLEVELINFORESIDL_DATARES"]._serialized_start = 130
    _globals["_GETLEVELINFORESIDL_DATARES"]._serialized_end = 196
