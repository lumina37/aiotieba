"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0ePollInfo.proto\"\xa2\x01\n\x08PollInfo\x12\x10\n\x08is_multi\x18\x02 \x01(\x05\x12\x11\n\ttotal_num\x18\x03 \x01(\x03\x12%\n\x07options\x18\t \x03(\x0b\x32\x14.PollInfo.PollOption\x12\x12\n\ntotal_poll\x18\x0b \x01(\x03\x12\r\n\x05title\x18\x0c \x01(\t\x1a\'\n\nPollOption\x12\x0b\n\x03num\x18\x02 \x01(\x03\x12\x0c\n\x04text\x18\x03 \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'PollInfo_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_POLLINFO']._serialized_start = 19
    _globals['_POLLINFO']._serialized_end = 181
    _globals['_POLLINFO_POLLOPTION']._serialized_start = 142
    _globals['_POLLINFO_POLLOPTION']._serialized_end = 181
