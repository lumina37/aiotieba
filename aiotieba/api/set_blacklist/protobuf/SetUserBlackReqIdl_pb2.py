"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import CommonReq_pb2 as CommonReq__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x18SetUserBlackReqIdl.proto\x1a\x0f\x43ommonReq.proto\"\xfb\x01\n\x12SetUserBlackReqIdl\x12)\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x1b.SetUserBlackReqIdl.DataReq\x1a\xb9\x01\n\x07\x44\x61taReq\x12\x1a\n\x06\x63ommon\x18\x01 \x01(\x0b\x32\n.CommonReq\x12\x11\n\tblack_uid\x18\x02 \x01(\x03\x12=\n\tperm_list\x18\x03 \x01(\x0b\x32*.SetUserBlackReqIdl.DataReq.PermissionList\x1a@\n\x0ePermissionList\x12\x0e\n\x06\x66ollow\x18\x01 \x01(\x05\x12\x10\n\x08interact\x18\x02 \x01(\x05\x12\x0c\n\x04\x63hat\x18\x03 \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'SetUserBlackReqIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_SETUSERBLACKREQIDL']._serialized_start = 46
    _globals['_SETUSERBLACKREQIDL']._serialized_end = 297
    _globals['_SETUSERBLACKREQIDL_DATAREQ']._serialized_start = 112
    _globals['_SETUSERBLACKREQIDL_DATAREQ']._serialized_end = 297
    _globals['_SETUSERBLACKREQIDL_DATAREQ_PERMISSIONLIST']._serialized_start = 233
    _globals['_SETUSERBLACKREQIDL_DATAREQ_PERMISSIONLIST']._serialized_end = 297
