"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1e\x43ommitReceivedPmsgReqIdl.proto\"\x96\x01\n\x18\x43ommitReceivedPmsgReqIdl\x12/\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32!.CommitReceivedPmsgReqIdl.DataReq\x1aI\n\x07\x44\x61taReq\x12\x0f\n\x07groupId\x18\x01 \x01(\x03\x12\r\n\x05toUid\x18\x02 \x01(\x03\x12\x0f\n\x07msgType\x18\x03 \x01(\x05\x12\r\n\x05msgId\x18\x04 \x01(\x03\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'CommitReceivedPmsgReqIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_COMMITRECEIVEDPMSGREQIDL']._serialized_start = 35
    _globals['_COMMITRECEIVEDPMSGREQIDL']._serialized_end = 185
    _globals['_COMMITRECEIVEDPMSGREQIDL_DATAREQ']._serialized_start = 112
    _globals['_COMMITRECEIVEDPMSGREQIDL_DATAREQ']._serialized_end = 185
