"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1aGetForumDetailResIdl.proto\x1a\x0b\x45rror.proto\"\xc6\x03\n\x14GetForumDetailResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12+\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x1d.GetForumDetailResIdl.DataRes\x1a\xe9\x02\n\x07\x44\x61taRes\x12\x44\n\nforum_info\x18\x01 \x01(\x0b\x32\x30.GetForumDetailResIdl.DataRes.RecommendForumInfo\x12\x46\n\x0c\x65lection_tab\x18\x08 \x01(\x0b\x32\x30.GetForumDetailResIdl.DataRes.ManagerElectionTab\x1a\x9d\x01\n\x12RecommendForumInfo\x12\x0e\n\x06\x61vatar\x18\x01 \x01(\t\x12\x10\n\x08\x66orum_id\x18\x02 \x01(\x04\x12\x12\n\nforum_name\x18\x03 \x01(\t\x12\x14\n\x0cmember_count\x18\x05 \x01(\r\x12\x14\n\x0cthread_count\x18\x06 \x01(\r\x12\x0e\n\x06slogan\x18\x07 \x01(\t\x12\x15\n\ravatar_origin\x18\x14 \x01(\t\x1a\x30\n\x12ManagerElectionTab\x12\x1a\n\x12new_manager_status\x18\x04 \x01(\rb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'GetForumDetailResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_GETFORUMDETAILRESIDL']._serialized_start = 44
    _globals['_GETFORUMDETAILRESIDL']._serialized_end = 498
    _globals['_GETFORUMDETAILRESIDL_DATARES']._serialized_start = 137
    _globals['_GETFORUMDETAILRESIDL_DATARES']._serialized_end = 498
    _globals['_GETFORUMDETAILRESIDL_DATARES_RECOMMENDFORUMINFO']._serialized_start = 291
    _globals['_GETFORUMDETAILRESIDL_DATARES_RECOMMENDFORUMINFO']._serialized_end = 448
    _globals['_GETFORUMDETAILRESIDL_DATARES_MANAGERELECTIONTAB']._serialized_start = 450
    _globals['_GETFORUMDETAILRESIDL_DATARES_MANAGERELECTIONTAB']._serialized_end = 498
