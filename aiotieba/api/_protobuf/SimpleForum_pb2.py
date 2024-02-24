"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x11SimpleForum.proto\"x\n\x0bSimpleForum\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0b\x66irst_class\x18\x07 \x01(\t\x12\x14\n\x0csecond_class\x18\x08 \x01(\t\x12\x12\n\nmember_num\x18\x0c \x01(\x05\x12\x10\n\x08post_num\x18\r \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'SimpleForum_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_SIMPLEFORUM']._serialized_start = 21
    _globals['_SIMPLEFORUM']._serialized_end = 141
