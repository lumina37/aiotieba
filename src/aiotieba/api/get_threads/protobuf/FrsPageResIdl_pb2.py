from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2
from ..._protobuf import FrsTabInfo_pb2 as FrsTabInfo__pb2
from ..._protobuf import Page_pb2 as Page__pb2
from ..._protobuf import PollInfo_pb2 as PollInfo__pb2
from ..._protobuf import ThreadInfo_pb2 as ThreadInfo__pb2
from ..._protobuf import User_pb2 as User__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13\x46rsPageResIdl.proto\x1a\x0b\x45rror.proto\x1a\nPage.proto\x1a\x10ThreadInfo.proto\x1a\nUser.proto\x1a\x10\x46rsTabInfo.proto\x1a\x0ePollInfo.proto"\x8e\x0b\n\x08PageData\x12*\n\tfeed_list\x18\x02 \x03(\x0b\x32\x17.PageData.LayoutFactory\x1a\xd5\n\n\rLayoutFactory\x12\x0e\n\x06layout\x18\x01 \x01(\t\x12\x30\n\x04\x66\x65\x65\x64\x18\x02 \x01(\x0b\x32".PageData.LayoutFactory.FeedLayout\x1a\x81\n\n\nFeedLayout\x12G\n\ncomponents\x18\x01 \x03(\x0b\x32\x33.PageData.LayoutFactory.FeedLayout.ComponentFactory\x12@\n\rbusiness_info\x18\x05 \x03(\x0b\x32).PageData.LayoutFactory.FeedLayout.FeedKV\x1a\xc1\x08\n\x10\x43omponentFactory\x12\x11\n\tcomponent\x18\x01 \x01(\t\x12V\n\nfeed_title\x18\x03 \x01(\x0b\x32\x42.PageData.LayoutFactory.FeedLayout.ComponentFactory.TitleComponent\x12\\\n\rfeed_abstract\x18\x04 \x01(\x0b\x32\x45.PageData.LayoutFactory.FeedLayout.ComponentFactory.AbstractComponent\x12V\n\x08\x66\x65\x65\x64_pic\x18\x07 \x01(\x0b\x32\x44.PageData.LayoutFactory.FeedLayout.ComponentFactory.FeedPicComponent\x12\x1c\n\tfeed_poll\x18\x16 \x01(\x0b\x32\t.PollInfo\x1a\xcb\x02\n\x13\x46\x65\x65\x64\x43ontentResource\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12j\n\ttext_info\x18\x08 \x01(\x0b\x32W.PageData.LayoutFactory.FeedLayout.ComponentFactory.FeedContentResource.FeedContentText\x12l\n\nemoji_info\x18\n \x01(\x0b\x32X.PageData.LayoutFactory.FeedLayout.ComponentFactory.FeedContentResource.FeedContentEmoji\x1a\x1f\n\x0f\x46\x65\x65\x64\x43ontentText\x12\x0c\n\x04text\x18\x01 \x01(\t\x1a+\n\x10\x46\x65\x65\x64\x43ontentEmoji\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\t\n\x01\x63\x18\x02 \x01(\t\x1al\n\x07PicInfo\x12\x15\n\rsmall_pic_url\x18\x01 \x01(\t\x12\x13\n\x0b\x62ig_pic_url\x18\x02 \x01(\t\x12\x16\n\x0eorigin_pic_url\x18\x03 \x01(\t\x12\r\n\x05width\x18\x04 \x01(\r\x12\x0e\n\x06height\x18\x05 \x01(\r\x1ag\n\x0eTitleComponent\x12U\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32G.PageData.LayoutFactory.FeedLayout.ComponentFactory.FeedContentResource\x1aj\n\x11\x41\x62stractComponent\x12U\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32G.PageData.LayoutFactory.FeedLayout.ComponentFactory.FeedContentResource\x1a]\n\x10\x46\x65\x65\x64PicComponent\x12I\n\x04pics\x18\x01 \x03(\x0b\x32;.PageData.LayoutFactory.FeedLayout.ComponentFactory.PicInfo\x1a$\n\x06\x46\x65\x65\x64KV\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t"\x94\x05\n\rFrsPageResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12$\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x16.FrsPageResIdl.DataRes\x1a\xc5\x04\n\x07\x44\x61taRes\x12/\n\x05\x66orum\x18\x02 \x01(\x0b\x32 .FrsPageResIdl.DataRes.ForumInfo\x12\x13\n\x04page\x18\x04 \x01(\x0b\x32\x05.Page\x12 \n\x0bthread_list\x18\x07 \x03(\x0b\x32\x0b.ThreadInfo\x12\x18\n\tuser_list\x18\x11 \x03(\x0b\x32\x05.User\x12\x37\n\x0cnav_tab_info\x18% \x01(\x0b\x32!.FrsPageResIdl.DataRes.NavTabInfo\x12:\n\nforum_rule\x18i \x01(\x0b\x32&.FrsPageResIdl.DataRes.ForumRuleStatus\x12\x1c\n\tpage_data\x18~ \x01(\x0b\x32\t.PageData\x1a\xd1\x01\n\tForumInfo\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0b\x66irst_class\x18\x03 \x01(\t\x12\x14\n\x0csecond_class\x18\x04 \x01(\t\x12\x12\n\nmember_num\x18\t \x01(\x05\x12\x12\n\nthread_num\x18\n \x01(\x05\x12\x10\n\x08post_num\x18\x0b \x01(\x05\x12:\n\x08managers\x18\x11 \x03(\x0b\x32(.FrsPageResIdl.DataRes.ForumInfo.Manager\x1a\t\n\x07Manager\x1a&\n\nNavTabInfo\x12\x18\n\x03tab\x18\x01 \x03(\x0b\x32\x0b.FrsTabInfo\x1a)\n\x0f\x46orumRuleStatus\x12\x16\n\x0ehas_forum_rule\x18\x04 \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "FrsPageResIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_PAGEDATA"]._serialized_start = 113
    _globals["_PAGEDATA"]._serialized_end = 1535
    _globals["_PAGEDATA_LAYOUTFACTORY"]._serialized_start = 170
    _globals["_PAGEDATA_LAYOUTFACTORY"]._serialized_end = 1535
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT"]._serialized_start = 254
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT"]._serialized_end = 1535
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY"]._serialized_start = 408
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY"]._serialized_end = 1497
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_FEEDCONTENTRESOURCE"]._serialized_start = 748
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_FEEDCONTENTRESOURCE"]._serialized_end = 1079
    _globals[
        "_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_FEEDCONTENTRESOURCE_FEEDCONTENTTEXT"
    ]._serialized_start = 1003
    _globals[
        "_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_FEEDCONTENTRESOURCE_FEEDCONTENTTEXT"
    ]._serialized_end = 1034
    _globals[
        "_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_FEEDCONTENTRESOURCE_FEEDCONTENTEMOJI"
    ]._serialized_start = 1036
    _globals[
        "_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_FEEDCONTENTRESOURCE_FEEDCONTENTEMOJI"
    ]._serialized_end = 1079
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_PICINFO"]._serialized_start = 1081
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_PICINFO"]._serialized_end = 1189
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_TITLECOMPONENT"]._serialized_start = 1191
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_TITLECOMPONENT"]._serialized_end = 1294
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_ABSTRACTCOMPONENT"]._serialized_start = 1296
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_ABSTRACTCOMPONENT"]._serialized_end = 1402
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_FEEDPICCOMPONENT"]._serialized_start = 1404
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_COMPONENTFACTORY_FEEDPICCOMPONENT"]._serialized_end = 1497
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_FEEDKV"]._serialized_start = 1499
    _globals["_PAGEDATA_LAYOUTFACTORY_FEEDLAYOUT_FEEDKV"]._serialized_end = 1535
    _globals["_FRSPAGERESIDL"]._serialized_start = 1538
    _globals["_FRSPAGERESIDL"]._serialized_end = 2198
    _globals["_FRSPAGERESIDL_DATARES"]._serialized_start = 1617
    _globals["_FRSPAGERESIDL_DATARES"]._serialized_end = 2198
    _globals["_FRSPAGERESIDL_DATARES_FORUMINFO"]._serialized_start = 1906
    _globals["_FRSPAGERESIDL_DATARES_FORUMINFO"]._serialized_end = 2115
    _globals["_FRSPAGERESIDL_DATARES_FORUMINFO_MANAGER"]._serialized_start = 2106
    _globals["_FRSPAGERESIDL_DATARES_FORUMINFO_MANAGER"]._serialized_end = 2115
    _globals["_FRSPAGERESIDL_DATARES_NAVTABINFO"]._serialized_start = 2117
    _globals["_FRSPAGERESIDL_DATARES_NAVTABINFO"]._serialized_end = 2155
    _globals["_FRSPAGERESIDL_DATARES_FORUMRULESTATUS"]._serialized_start = 2157
    _globals["_FRSPAGERESIDL_DATARES_FORUMRULESTATUS"]._serialized_end = 2198
