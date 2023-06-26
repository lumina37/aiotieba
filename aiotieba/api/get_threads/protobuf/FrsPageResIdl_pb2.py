"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2
from ..._protobuf import FrsTabInfo_pb2 as FrsTabInfo__pb2
from ..._protobuf import Page_pb2 as Page__pb2
from ..._protobuf import ThreadInfo_pb2 as ThreadInfo__pb2
from ..._protobuf import User_pb2 as User__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13\x46rsPageResIdl.proto\x1a\x0b\x45rror.proto\x1a\nPage.proto\x1a\x10ThreadInfo.proto\x1a\nUser.proto\x1a\x10\x46rsTabInfo.proto\"\xcb\x04\n\rFrsPageResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12$\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x16.FrsPageResIdl.DataRes\x1a\xfc\x03\n\x07\x44\x61taRes\x12/\n\x05\x66orum\x18\x02 \x01(\x0b\x32 .FrsPageResIdl.DataRes.ForumInfo\x12\x13\n\x04page\x18\x04 \x01(\x0b\x32\x05.Page\x12 \n\x0bthread_list\x18\x07 \x03(\x0b\x32\x0b.ThreadInfo\x12\x18\n\tuser_list\x18\x11 \x03(\x0b\x32\x05.User\x12\x37\n\x0cnav_tab_info\x18% \x01(\x0b\x32!.FrsPageResIdl.DataRes.NavTabInfo\x12:\n\nforum_rule\x18i \x01(\x0b\x32&.FrsPageResIdl.DataRes.ForumRuleStatus\x1a\xa6\x01\n\tForumInfo\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\nmember_num\x18\t \x01(\x05\x12\x12\n\nthread_num\x18\n \x01(\x05\x12\x10\n\x08post_num\x18\x0b \x01(\x05\x12:\n\x08managers\x18\x11 \x03(\x0b\x32(.FrsPageResIdl.DataRes.ForumInfo.Manager\x1a\t\n\x07Manager\x1a&\n\nNavTabInfo\x12\x18\n\x03tab\x18\x01 \x03(\x0b\x32\x0b.FrsTabInfo\x1a)\n\x0f\x46orumRuleStatus\x12\x16\n\x0ehas_forum_rule\x18\x04 \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'FrsPageResIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_FRSPAGERESIDL']._serialized_start = 97
    _globals['_FRSPAGERESIDL']._serialized_end = 684
    _globals['_FRSPAGERESIDL_DATARES']._serialized_start = 176
    _globals['_FRSPAGERESIDL_DATARES']._serialized_end = 684
    _globals['_FRSPAGERESIDL_DATARES_FORUMINFO']._serialized_start = 435
    _globals['_FRSPAGERESIDL_DATARES_FORUMINFO']._serialized_end = 601
    _globals['_FRSPAGERESIDL_DATARES_FORUMINFO_MANAGER']._serialized_start = 592
    _globals['_FRSPAGERESIDL_DATARES_FORUMINFO_MANAGER']._serialized_end = 601
    _globals['_FRSPAGERESIDL_DATARES_NAVTABINFO']._serialized_start = 603
    _globals['_FRSPAGERESIDL_DATARES_NAVTABINFO']._serialized_end = 641
    _globals['_FRSPAGERESIDL_DATARES_FORUMRULESTATUS']._serialized_start = 643
    _globals['_FRSPAGERESIDL_DATARES_FORUMRULESTATUS']._serialized_end = 684
