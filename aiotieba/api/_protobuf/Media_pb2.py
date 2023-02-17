"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0bMedia.proto\"\x94\x01\n\x05Media\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\x11\n\tsmall_pic\x18\x02 \x01(\t\x12\x0f\n\x07\x62ig_pic\x18\x03 \x01(\t\x12\x11\n\twater_pic\x18\x04 \x01(\t\x12\r\n\x05width\x18\n \x01(\r\x12\x0e\n\x06height\x18\x0b \x01(\r\x12\x12\n\norigin_pic\x18\x0f \x01(\t\x12\x13\n\x0borigin_size\x18\x10 \x01(\rb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Media_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_MEDIA']._serialized_start = 16
    _globals['_MEDIA']._serialized_end = 164
