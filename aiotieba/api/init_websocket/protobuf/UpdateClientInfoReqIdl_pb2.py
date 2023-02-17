"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1cUpdateClientInfoReqIdl.proto\"\xa2\x01\n\x16UpdateClientInfoReqIdl\x12\x0c\n\x04\x63uid\x18\x01 \x01(\t\x12-\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x1f.UpdateClientInfoReqIdl.DataReq\x1aK\n\x07\x44\x61taReq\x12\r\n\x05\x62\x64uss\x18\x01 \x01(\t\x12\x0e\n\x06\x64\x65vice\x18\x02 \x01(\t\x12\x11\n\tsecretKey\x18\x03 \x01(\x0c\x12\x0e\n\x06stoken\x18\x0c \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'UpdateClientInfoReqIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_UPDATECLIENTINFOREQIDL']._serialized_start = 33
    _globals['_UPDATECLIENTINFOREQIDL']._serialized_end = 195
    _globals['_UPDATECLIENTINFOREQIDL_DATAREQ']._serialized_start = 120
    _globals['_UPDATECLIENTINFOREQIDL_DATAREQ']._serialized_end = 195
