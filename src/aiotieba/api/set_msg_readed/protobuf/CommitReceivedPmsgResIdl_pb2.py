from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1e\x43ommitReceivedPmsgResIdl.proto\x1a\x0b\x45rror.proto"\xb4\x01\n\x18\x43ommitReceivedPmsgResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12/\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32!.CommitReceivedPmsgResIdl.DataRes\x1aP\n\x07\x44\x61taRes\x12\x11\n\treadMsgId\x18\x01 \x01(\x03\x12\x0f\n\x07groupId\x18\x02 \x01(\x03\x12\r\n\x05toUid\x18\x03 \x01(\x03\x12\x12\n\ntoUserType\x18\x04 \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "CommitReceivedPmsgResIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_COMMITRECEIVEDPMSGRESIDL"]._serialized_start = 48
    _globals["_COMMITRECEIVEDPMSGRESIDL"]._serialized_end = 228
    _globals["_COMMITRECEIVEDPMSGRESIDL_DATARES"]._serialized_start = 148
    _globals["_COMMITRECEIVEDPMSGRESIDL_DATARES"]._serialized_end = 228
