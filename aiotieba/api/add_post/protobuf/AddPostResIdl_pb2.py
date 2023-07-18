"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13\x41\x64\x64PostResIdl.proto\x1a\x0b\x45rror.proto\"\xf2\x01\n\rAddPostResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12$\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x16.AddPostResIdl.DataRes\x1a\xa3\x01\n\x07\x44\x61taRes\x12\x10\n\x08video_id\x18\x04 \x01(\t\x12\x0b\n\x03msg\x18\x05 \x01(\t\x12\x0f\n\x07pre_msg\x18\x06 \x01(\t\x12\x11\n\tcolor_msg\x18\x07 \x01(\t\x12\x31\n\x04info\x18\x0e \x01(\x0b\x32#.AddPostResIdl.DataRes.PostAntiInfo\x1a\"\n\x0cPostAntiInfo\x12\x12\n\nneed_vcode\x18\x03 \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'AddPostResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_ADDPOSTRESIDL']._serialized_start = 37
    _globals['_ADDPOSTRESIDL']._serialized_end = 279
    _globals['_ADDPOSTRESIDL_DATARES']._serialized_start = 116
    _globals['_ADDPOSTRESIDL_DATARES']._serialized_end = 279
    _globals['_ADDPOSTRESIDL_DATARES_POSTANTIINFO']._serialized_start = 245
    _globals['_ADDPOSTRESIDL_DATARES_POSTANTIINFO']._serialized_end = 279
