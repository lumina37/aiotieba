"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0f\x43ommonReq.proto\"I\n\tCommonReq\x12\x14\n\x0c_client_type\x18\x01 \x01(\x05\x12\x17\n\x0f_client_version\x18\x02 \x01(\t\x12\r\n\x05\x42\x44USS\x18\n \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'CommonReq_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_COMMONREQ']._serialized_start = 19
    _globals['_COMMONREQ']._serialized_end = 92
