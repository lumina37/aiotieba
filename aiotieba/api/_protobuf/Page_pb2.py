"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\nPage.proto\"|\n\x04Page\x12\x11\n\tpage_size\x18\x01 \x01(\x05\x12\x14\n\x0c\x63urrent_page\x18\x03 \x01(\x05\x12\x13\n\x0btotal_count\x18\x04 \x01(\x05\x12\x12\n\ntotal_page\x18\x05 \x01(\x05\x12\x10\n\x08has_more\x18\x06 \x01(\x05\x12\x10\n\x08has_prev\x18\x07 \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Page_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_PAGE']._serialized_start = 14
    _globals['_PAGE']._serialized_end = 138
