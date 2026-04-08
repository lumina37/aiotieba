"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x17GetGroupMsgReqIdl.proto"v\n\x07\x44\x61taReq\x12\'\n\tgroupMids\x18\x06 \x03(\x0b\x32\x14.DataReq.GroupLastId\x12\x0f\n\x07gettype\x18\x07 \x01(\t\x1a\x31\n\x0bGroupLastId\x12\x0f\n\x07groupId\x18\x01 \x01(\x03\x12\x11\n\tlastMsgId\x18\x02 \x01(\x03"9\n\x11GetGroupMsgReqIdl\x12\x0c\n\x04\x63uid\x18\x01 \x01(\t\x12\x16\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x08.DataReqb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "GetGroupMsgReqIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_DATAREQ"]._serialized_start = 27
    _globals["_DATAREQ"]._serialized_end = 145
    _globals["_DATAREQ_GROUPLASTID"]._serialized_start = 96
    _globals["_DATAREQ_GROUPLASTID"]._serialized_end = 145
    _globals["_GETGROUPMSGREQIDL"]._serialized_start = 147
    _globals["_GETGROUPMSGREQIDL"]._serialized_end = 204
