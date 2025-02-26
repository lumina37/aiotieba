"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2
from ..._protobuf import Page_pb2 as Page__pb2
from ..._protobuf import ThreadInfo_pb2 as ThreadInfo__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b"\n\x16\x46rsPageResIdl4lp.proto\x1a\x0b\x45rror.proto\x1a\nPage.proto\x1a\x10ThreadInfo.proto\"\xf0\x01\n\x10\x46rsPageResIdl4lp\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12'\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x19.FrsPageResIdl4lp.DataRes\x1a\x9b\x01\n\x07\x44\x61taRes\x12\x32\n\x05\x66orum\x18\x02 \x01(\x0b\x32#.FrsPageResIdl4lp.DataRes.ForumInfo\x12\x13\n\x04page\x18\x04 \x01(\x0b\x32\x05.Page\x12 \n\x0bthread_list\x18\x07 \x03(\x0b\x32\x0b.ThreadInfo\x1a%\n\tForumInfo\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x0c\n\x04name\x18\x02 \x01(\tb\x06proto3"
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "FrsPageResIdl4lp_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_FRSPAGERESIDL4LP"]._serialized_start = 70
    _globals["_FRSPAGERESIDL4LP"]._serialized_end = 310
    _globals["_FRSPAGERESIDL4LP_DATARES"]._serialized_start = 155
    _globals["_FRSPAGERESIDL4LP_DATARES"]._serialized_end = 310
    _globals["_FRSPAGERESIDL4LP_DATARES_FORUMINFO"]._serialized_start = 273
    _globals["_FRSPAGERESIDL4LP_DATARES_FORUMINFO"]._serialized_end = 310
