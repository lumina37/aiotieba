"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2
from ..._protobuf import Page_pb2 as Page__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x19UserMuteQueryResIdl.proto\x1a\x0b\x45rror.proto\x1a\nPage.proto\"\x9b\x02\n\x13UserMuteQueryResIdl\x12*\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x1c.UserMuteQueryResIdl.DataRes\x12\x15\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x06.Error\x1a\xc0\x01\n\x07\x44\x61taRes\x12\x38\n\tmute_user\x18\x01 \x03(\x0b\x32%.UserMuteQueryResIdl.DataRes.MuteUser\x12\x13\n\x04page\x18\x02 \x01(\x0b\x32\x05.Page\x1a\x66\n\x08MuteUser\x12\x0f\n\x07user_id\x18\x01 \x01(\x03\x12\x11\n\tuser_name\x18\x02 \x01(\t\x12\x11\n\tmute_time\x18\x03 \x01(\x05\x12\x10\n\x08portrait\x18\x04 \x01(\t\x12\x11\n\tname_show\x18\x05 \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'UserMuteQueryResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_USERMUTEQUERYRESIDL']._serialized_start = 55
    _globals['_USERMUTEQUERYRESIDL']._serialized_end = 338
    _globals['_USERMUTEQUERYRESIDL_DATARES']._serialized_start = 146
    _globals['_USERMUTEQUERYRESIDL_DATARES']._serialized_end = 338
    _globals['_USERMUTEQUERYRESIDL_DATARES_MUTEUSER']._serialized_start = 236
    _globals['_USERMUTEQUERYRESIDL_DATARES_MUTEUSER']._serialized_end = 338
