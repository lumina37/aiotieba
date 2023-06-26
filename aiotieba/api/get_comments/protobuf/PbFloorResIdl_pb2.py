"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2
from ..._protobuf import Page_pb2 as Page__pb2
from ..._protobuf import Post_pb2 as Post__pb2
from ..._protobuf import SubPostList_pb2 as SubPostList__pb2
from ..._protobuf import ThreadInfo_pb2 as ThreadInfo__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13PbFloorResIdl.proto\x1a\x0b\x45rror.proto\x1a\nPage.proto\x1a\nPost.proto\x1a\x10ThreadInfo.proto\x1a\x11SubPostList.proto\"\x9f\x02\n\rPbFloorResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12$\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x16.PbFloorResIdl.DataRes\x1a\xd0\x01\n\x07\x44\x61taRes\x12\x13\n\x04page\x18\x01 \x01(\x0b\x32\x05.Page\x12\x13\n\x04post\x18\x03 \x01(\x0b\x32\x05.Post\x12\"\n\x0csubpost_list\x18\x04 \x03(\x0b\x32\x0c.SubPostList\x12\x1b\n\x06thread\x18\x05 \x01(\x0b\x32\x0b.ThreadInfo\x12\x31\n\x05\x66orum\x18\x06 \x01(\x0b\x32\".PbFloorResIdl.DataRes.SimpleForum\x1a\'\n\x0bSimpleForum\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x0c\n\x04name\x18\x02 \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'PbFloorResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_PBFLOORRESIDL']._serialized_start = 98
    _globals['_PBFLOORRESIDL']._serialized_end = 385
    _globals['_PBFLOORRESIDL_DATARES']._serialized_start = 177
    _globals['_PBFLOORRESIDL_DATARES']._serialized_end = 385
    _globals['_PBFLOORRESIDL_DATARES_SIMPLEFORUM']._serialized_start = 346
    _globals['_PBFLOORRESIDL_DATARES_SIMPLEFORUM']._serialized_end = 385
