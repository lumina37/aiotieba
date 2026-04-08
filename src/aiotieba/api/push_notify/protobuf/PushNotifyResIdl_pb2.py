"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x16PushNotifyResIdl.proto"\x91\x01\n\tPusherMsg\x12&\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x18.PusherMsg.PusherMsgInfo\x1a\\\n\rPusherMsgInfo\x12\x0f\n\x07groupId\x18\x01 \x01(\x03\x12\r\n\x05msgId\x18\x02 \x01(\x03\x12\x0c\n\x04type\x18\x04 \x01(\x05\x12\n\n\x02\x65t\x18\x06 \x01(\t\x12\x11\n\tgroupType\x18\x07 \x01(\x05"0\n\x10PushNotifyResIdl\x12\x1c\n\x08multiMsg\x18\x02 \x03(\x0b\x32\n.PusherMsgb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "PushNotifyResIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_PUSHERMSG"]._serialized_start = 27
    _globals["_PUSHERMSG"]._serialized_end = 172
    _globals["_PUSHERMSG_PUSHERMSGINFO"]._serialized_start = 80
    _globals["_PUSHERMSG_PUSHERMSGINFO"]._serialized_end = 172
    _globals["_PUSHNOTIFYRESIDL"]._serialized_start = 174
    _globals["_PUSHNOTIFYRESIDL"]._serialized_end = 222
