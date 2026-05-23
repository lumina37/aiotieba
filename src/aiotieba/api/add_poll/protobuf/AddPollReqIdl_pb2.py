from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import CommonReq_pb2 as CommonReq__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13\x41\x64\x64PollReqIdl.proto\x1a\x0f\x43ommonReq.proto"\x92\x01\n\rAddPollReqIdl\x12$\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x16.AddPollReqIdl.DataReq\x1a[\n\x07\x44\x61taReq\x12\x11\n\tthread_id\x18\x01 \x01(\x04\x12\x0f\n\x07options\x18\x02 \x01(\t\x12\x1a\n\x06\x63ommon\x18\x03 \x01(\x0b\x32\n.CommonReq\x12\x10\n\x08\x66orum_id\x18\x04 \x01(\x04\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "AddPollReqIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_ADDPOLLREQIDL"]._serialized_start = 41
    _globals["_ADDPOLLREQIDL"]._serialized_end = 187
    _globals["_ADDPOLLREQIDL_DATAREQ"]._serialized_start = 96
    _globals["_ADDPOLLREQIDL_DATAREQ"]._serialized_end = 187
