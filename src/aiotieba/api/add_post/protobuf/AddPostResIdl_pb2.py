"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13\x41\x64\x64PostResIdl.proto\x1a\x0b\x45rror.proto"\x95\x01\n\x07\x44\x61taRes\x12\x10\n\x08video_id\x18\x04 \x01(\t\x12\x0b\n\x03msg\x18\x05 \x01(\t\x12\x0f\n\x07pre_msg\x18\x06 \x01(\t\x12\x11\n\tcolor_msg\x18\x07 \x01(\t\x12#\n\x04info\x18\x0e \x01(\x0b\x32\x15.DataRes.PostAntiInfo\x1a"\n\x0cPostAntiInfo\x12\x12\n\nneed_vcode\x18\x03 \x01(\t">\n\rAddPostResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12\x16\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x08.DataResb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "AddPostResIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_DATARES"]._serialized_start = 37
    _globals["_DATARES"]._serialized_end = 186
    _globals["_DATARES_POSTANTIINFO"]._serialized_start = 152
    _globals["_DATARES_POSTANTIINFO"]._serialized_end = 186
    _globals["_ADDPOSTRESIDL"]._serialized_start = 188
    _globals["_ADDPOSTRESIDL"]._serialized_end = 250
