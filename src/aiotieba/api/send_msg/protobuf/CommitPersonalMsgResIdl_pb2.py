from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1d\x43ommitPersonalMsgResIdl.proto\x1a\x0b\x45rror.proto"\xb6\x02\n\x17\x43ommitPersonalMsgResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12.\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32 .CommitPersonalMsgResIdl.DataRes\x1a\xd3\x01\n\x07\x44\x61taRes\x12\r\n\x05msgId\x18\x01 \x01(\x03\x12\x0f\n\x07groupId\x18\x02 \x01(\x03\x12\x10\n\x08recordId\x18\x03 \x01(\x03\x12\r\n\x05toUid\x18\x04 \x01(\x03\x12\x12\n\ntoUserType\x18\x05 \x01(\x05\x12=\n\tblockInfo\x18\x06 \x01(\x0b\x32*.CommitPersonalMsgResIdl.DataRes.BlockInfo\x1a\x34\n\tBlockInfo\x12\x12\n\nblockErrno\x18\x01 \x01(\x05\x12\x13\n\x0b\x62lockErrmsg\x18\x02 \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "CommitPersonalMsgResIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_COMMITPERSONALMSGRESIDL"]._serialized_start = 47
    _globals["_COMMITPERSONALMSGRESIDL"]._serialized_end = 357
    _globals["_COMMITPERSONALMSGRESIDL_DATARES"]._serialized_start = 146
    _globals["_COMMITPERSONALMSGRESIDL_DATARES"]._serialized_end = 357
    _globals["_COMMITPERSONALMSGRESIDL_DATARES_BLOCKINFO"]._serialized_start = 305
    _globals["_COMMITPERSONALMSGRESIDL_DATARES_BLOCKINFO"]._serialized_end = 357
