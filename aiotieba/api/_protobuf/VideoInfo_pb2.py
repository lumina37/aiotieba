"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0fVideoInfo.proto\"\x8c\x01\n\tVideoInfo\x12\x11\n\tvideo_url\x18\x02 \x01(\t\x12\x16\n\x0evideo_duration\x18\x03 \x01(\r\x12\x13\n\x0bvideo_width\x18\x04 \x01(\r\x12\x14\n\x0cvideo_height\x18\x05 \x01(\r\x12\x15\n\rthumbnail_url\x18\x06 \x01(\t\x12\x12\n\nplay_count\x18\n \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'VideoInfo_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_VIDEOINFO']._serialized_start = 20
    _globals['_VIDEOINFO']._serialized_end = 160
