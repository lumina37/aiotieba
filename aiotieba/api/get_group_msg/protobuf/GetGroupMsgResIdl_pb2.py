"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x17GetGroupMsgResIdl.proto\x1a\x0b\x45rror.proto\"\xaf\x04\n\x11GetGroupMsgResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12(\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x1a.GetGroupMsgResIdl.DataRes\x1a\xd8\x03\n\x07\x44\x61taRes\x12\x36\n\tgroupInfo\x18\x01 \x03(\x0b\x32#.GetGroupMsgResIdl.DataRes.GroupMsg\x1a\x94\x03\n\x08GroupMsg\x12@\n\tgroupInfo\x18\x01 \x01(\x0b\x32-.GetGroupMsgResIdl.DataRes.GroupMsg.GroupInfo\x12<\n\x07msgList\x18\x02 \x03(\x0b\x32+.GetGroupMsgResIdl.DataRes.GroupMsg.MsgInfo\x1a/\n\tGroupInfo\x12\x0f\n\x07groupId\x18\x01 \x01(\x03\x12\x11\n\tgroupType\x18\x14 \x01(\x05\x1a\xd6\x01\n\x07MsgInfo\x12\r\n\x05msgId\x18\x01 \x01(\x03\x12\x0f\n\x07msgType\x18\x03 \x01(\x05\x12\x0f\n\x07\x63ontent\x18\x05 \x01(\t\x12\x12\n\ncreateTime\x18\x08 \x01(\x05\x12\x46\n\x08userInfo\x18\n \x01(\x0b\x32\x34.GetGroupMsgResIdl.DataRes.GroupMsg.MsgInfo.UserInfo\x1a>\n\x08UserInfo\x12\x0e\n\x06userId\x18\x01 \x01(\x03\x12\x10\n\x08userName\x18\x02 \x01(\t\x12\x10\n\x08portrait\x18\x04 \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'GetGroupMsgResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_GETGROUPMSGRESIDL']._serialized_start = 41
    _globals['_GETGROUPMSGRESIDL']._serialized_end = 600
    _globals['_GETGROUPMSGRESIDL_DATARES']._serialized_start = 128
    _globals['_GETGROUPMSGRESIDL_DATARES']._serialized_end = 600
    _globals['_GETGROUPMSGRESIDL_DATARES_GROUPMSG']._serialized_start = 196
    _globals['_GETGROUPMSGRESIDL_DATARES_GROUPMSG']._serialized_end = 600
    _globals['_GETGROUPMSGRESIDL_DATARES_GROUPMSG_GROUPINFO']._serialized_start = 336
    _globals['_GETGROUPMSGRESIDL_DATARES_GROUPMSG_GROUPINFO']._serialized_end = 383
    _globals['_GETGROUPMSGRESIDL_DATARES_GROUPMSG_MSGINFO']._serialized_start = 386
    _globals['_GETGROUPMSGRESIDL_DATARES_GROUPMSG_MSGINFO']._serialized_end = 600
    _globals['_GETGROUPMSGRESIDL_DATARES_GROUPMSG_MSGINFO_USERINFO']._serialized_start = 538
    _globals['_GETGROUPMSGRESIDL_DATARES_GROUPMSG_MSGINFO_USERINFO']._serialized_end = 600
