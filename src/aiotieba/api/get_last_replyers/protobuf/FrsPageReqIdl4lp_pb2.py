"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import CommonReq_pb2 as CommonReq__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b"\n\x16\x46rsPageReqIdl4lp.proto\x1a\x0f\x43ommonReq.proto\"\xc9\x01\n\x10\x46rsPageReqIdl4lp\x12'\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x19.FrsPageReqIdl4lp.DataReq\x1a\x8b\x01\n\x07\x44\x61taReq\x12\x1a\n\x06\x63ommon\x18' \x01(\x0b\x32\n.CommonReq\x12\n\n\x02kw\x18\x01 \x01(\t\x12\n\n\x02rn\x18\x02 \x01(\x05\x12\x0f\n\x07rn_need\x18\x03 \x01(\x05\x12\x0f\n\x07is_good\x18\x04 \x01(\x05\x12\x0b\n\x03\x63id\x18\x05 \x01(\x05\x12\n\n\x02pn\x18\x0f \x01(\x05\x12\x11\n\tsort_type\x18/ \x01(\x05\x62\x06proto3"
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "FrsPageReqIdl4lp_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_FRSPAGEREQIDL4LP"]._serialized_start = 44
    _globals["_FRSPAGEREQIDL4LP"]._serialized_end = 245
    _globals["_FRSPAGEREQIDL4LP_DATAREQ"]._serialized_start = 106
    _globals["_FRSPAGEREQIDL4LP_DATAREQ"]._serialized_end = 245
