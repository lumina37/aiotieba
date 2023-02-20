"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2
from ..._protobuf import PostInfoList_pb2 as PostInfoList__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x14UserPostResIdl.proto\x1a\x0b\x45rror.proto\x1a\x12PostInfoList.proto\"{\n\x0eUserPostResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12%\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x17.UserPostResIdl.DataRes\x1a+\n\x07\x44\x61taRes\x12 \n\tpost_list\x18\x01 \x03(\x0b\x32\r.PostInfoListb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'UserPostResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_USERPOSTRESIDL']._serialized_start = 57
    _globals['_USERPOSTRESIDL']._serialized_end = 180
    _globals['_USERPOSTRESIDL_DATARES']._serialized_start = 137
    _globals['_USERPOSTRESIDL_DATARES']._serialized_end = 180
