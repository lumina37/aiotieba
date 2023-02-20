"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1cUpdateClientInfoResIdl.proto\x1a\x0b\x45rror.proto\"\xec\x01\n\x16UpdateClientInfoResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12-\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x1f.UpdateClientInfoResIdl.DataRes\x1a\x8b\x01\n\x07\x44\x61taRes\x12<\n\tgroupInfo\x18\x01 \x03(\x0b\x32).UpdateClientInfoResIdl.DataRes.GroupInfo\x1a\x42\n\tGroupInfo\x12\x0f\n\x07groupId\x18\x01 \x01(\x03\x12\x11\n\tgroupType\x18\x14 \x01(\x05\x12\x11\n\tlastMsgId\x18\x15 \x01(\x03\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'UpdateClientInfoResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_UPDATECLIENTINFORESIDL']._serialized_start = 46
    _globals['_UPDATECLIENTINFORESIDL']._serialized_end = 282
    _globals['_UPDATECLIENTINFORESIDL_DATARES']._serialized_start = 143
    _globals['_UPDATECLIENTINFORESIDL_DATARES']._serialized_end = 282
    _globals['_UPDATECLIENTINFORESIDL_DATARES_GROUPINFO']._serialized_start = 216
    _globals['_UPDATECLIENTINFORESIDL_DATARES_GROUPINFO']._serialized_end = 282
