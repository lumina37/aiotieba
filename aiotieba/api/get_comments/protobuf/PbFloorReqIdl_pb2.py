"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import CommonReq_pb2 as CommonReq__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13PbFloorReqIdl.proto\x1a\x0f\x43ommonReq.proto\"\x8f\x01\n\rPbFloorReqIdl\x12$\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x16.PbFloorReqIdl.DataReq\x1aX\n\x07\x44\x61taReq\x12\x1a\n\x06\x63ommon\x18\t \x01(\x0b\x32\n.CommonReq\x12\n\n\x02kz\x18\x01 \x01(\x03\x12\x0b\n\x03pid\x18\x02 \x01(\x03\x12\x0c\n\x04spid\x18\x03 \x01(\x03\x12\n\n\x02pn\x18\x04 \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'PbFloorReqIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_PBFLOORREQIDL']._serialized_start = 41
    _globals['_PBFLOORREQIDL']._serialized_end = 184
    _globals['_PBFLOORREQIDL_DATAREQ']._serialized_start = 96
    _globals['_PBFLOORREQIDL_DATAREQ']._serialized_end = 184
