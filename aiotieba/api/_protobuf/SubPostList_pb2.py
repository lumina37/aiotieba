"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from . import Agree_pb2 as Agree__pb2
from . import PbContent_pb2 as PbContent__pb2
from . import User_pb2 as User__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x11SubPostList.proto\x1a\x0fPbContent.proto\x1a\nUser.proto\x1a\x0b\x41gree.proto\"\xa3\x01\n\x0bSubPostList\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x1b\n\x07\x63ontent\x18\x02 \x03(\x0b\x32\n.PbContent\x12\x0c\n\x04time\x18\x03 \x01(\r\x12\x11\n\tauthor_id\x18\x04 \x01(\x03\x12\r\n\x05title\x18\x05 \x01(\t\x12\r\n\x05\x66loor\x18\x06 \x01(\r\x12\x15\n\x06\x61uthor\x18\x07 \x01(\x0b\x32\x05.User\x12\x15\n\x05\x61gree\x18\t \x01(\x0b\x32\x06.Agree\";\n\x07SubPost\x12\x0b\n\x03pid\x18\x01 \x01(\x04\x12#\n\rsub_post_list\x18\x02 \x03(\x0b\x32\x0c.SubPostListb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'SubPostList_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_SUBPOSTLIST']._serialized_start = 64
    _globals['_SUBPOSTLIST']._serialized_end = 227
    _globals['_SUBPOST']._serialized_start = 229
    _globals['_SUBPOST']._serialized_end = 288
