"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1d\x43ommitPersonalMsgReqIdl.proto\"\x97\x01\n\x17\x43ommitPersonalMsgReqIdl\x12.\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32 .CommitPersonalMsgReqIdl.DataReq\x1aL\n\x07\x44\x61taReq\x12\r\n\x05toUid\x18\x02 \x01(\x03\x12\x0f\n\x07msgType\x18\x03 \x01(\x05\x12\x0f\n\x07\x63ontent\x18\x04 \x01(\t\x12\x10\n\x08recordId\x18\x06 \x01(\x03\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'CommitPersonalMsgReqIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_COMMITPERSONALMSGREQIDL']._serialized_start = 34
    _globals['_COMMITPERSONALMSGREQIDL']._serialized_end = 185
    _globals['_COMMITPERSONALMSGREQIDL_DATAREQ']._serialized_start = 109
    _globals['_COMMITPERSONALMSGREQIDL_DATAREQ']._serialized_end = 185
