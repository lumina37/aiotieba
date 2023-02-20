"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2
from ..._protobuf import Page_pb2 as Page__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1aGetForumSquareResIdl.proto\x1a\x0b\x45rror.proto\x1a\nPage.proto\"\xba\x02\n\x14GetForumSquareResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12+\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x1d.GetForumSquareResIdl.DataRes\x1a\xdd\x01\n\x07\x44\x61taRes\x12\x44\n\nforum_info\x18\x02 \x03(\x0b\x32\x30.GetForumSquareResIdl.DataRes.RecommendForumInfo\x12\x13\n\x04page\x18\x03 \x01(\x0b\x32\x05.Page\x1aw\n\x12RecommendForumInfo\x12\x10\n\x08\x66orum_id\x18\x02 \x01(\x04\x12\x12\n\nforum_name\x18\x03 \x01(\t\x12\x0f\n\x07is_like\x18\x04 \x01(\r\x12\x14\n\x0cmember_count\x18\x05 \x01(\r\x12\x14\n\x0cthread_count\x18\x06 \x01(\rb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'GetForumSquareResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_GETFORUMSQUARERESIDL']._serialized_start = 56
    _globals['_GETFORUMSQUARERESIDL']._serialized_end = 370
    _globals['_GETFORUMSQUARERESIDL_DATARES']._serialized_start = 149
    _globals['_GETFORUMSQUARERESIDL_DATARES']._serialized_end = 370
    _globals['_GETFORUMSQUARERESIDL_DATARES_RECOMMENDFORUMINFO']._serialized_start = 251
    _globals['_GETFORUMSQUARERESIDL_DATARES_RECOMMENDFORUMINFO']._serialized_end = 370
