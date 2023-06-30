"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import CommonReq_pb2 as CommonReq__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13ProfileReqIdl.proto\x1a\x0f\x43ommonReq.proto\"\xba\x01\n\rProfileReqIdl\x12$\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x16.ProfileReqIdl.DataReq\x1a\x82\x01\n\x07\x44\x61taReq\x12\x0b\n\x03uid\x18\x01 \x01(\x03\x12\x17\n\x0fneed_post_count\x18\x02 \x01(\r\x12\n\n\x02pn\x18\x06 \x01(\r\x12\x1a\n\x06\x63ommon\x18\t \x01(\x0b\x32\n.CommonReq\x12\x0c\n\x04page\x18\x0f \x01(\x05\x12\x1b\n\x13\x66riend_uid_portrait\x18\x10 \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ProfileReqIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_PROFILEREQIDL']._serialized_start = 41
    _globals['_PROFILEREQIDL']._serialized_end = 227
    _globals['_PROFILEREQIDL_DATAREQ']._serialized_start = 97
    _globals['_PROFILEREQIDL_DATAREQ']._serialized_end = 227
