"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x16PushNotifyResIdl.proto\"\xe6\x01\n\x10PushNotifyResIdl\x12-\n\x08multiMsg\x18\x02 \x03(\x0b\x32\x1b.PushNotifyResIdl.PusherMsg\x1a\xa2\x01\n\tPusherMsg\x12\x37\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32).PushNotifyResIdl.PusherMsg.PusherMsgInfo\x1a\\\n\rPusherMsgInfo\x12\x0f\n\x07groupId\x18\x01 \x01(\x03\x12\r\n\x05msgId\x18\x02 \x01(\x03\x12\x0c\n\x04type\x18\x04 \x01(\x05\x12\n\n\x02\x65t\x18\x06 \x01(\t\x12\x11\n\tgroupType\x18\x07 \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'PushNotifyResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_PUSHNOTIFYRESIDL']._serialized_start = 27
    _globals['_PUSHNOTIFYRESIDL']._serialized_end = 257
    _globals['_PUSHNOTIFYRESIDL_PUSHERMSG']._serialized_start = 95
    _globals['_PUSHNOTIFYRESIDL_PUSHERMSG']._serialized_end = 257
    _globals['_PUSHNOTIFYRESIDL_PUSHERMSG_PUSHERMSGINFO']._serialized_start = 165
    _globals['_PUSHNOTIFYRESIDL_PUSHERMSG_PUSHERMSGINFO']._serialized_end = 257
