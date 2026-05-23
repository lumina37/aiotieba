from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13\x41\x64\x64PollResIdl.proto\x1a\x0b\x45rror.proto"W\n\rAddPollResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12$\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x16.AddPollResIdl.DataRes\x1a\t\n\x07\x44\x61taResb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "AddPollResIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_ADDPOLLRESIDL"]._serialized_start = 36
    _globals["_ADDPOLLRESIDL"]._serialized_end = 123
    _globals["_ADDPOLLRESIDL_DATARES"]._serialized_start = 114
    _globals["_ADDPOLLRESIDL_DATARES"]._serialized_end = 123
