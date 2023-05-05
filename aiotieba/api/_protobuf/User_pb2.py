"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\nUser.proto\"\x92\n\n\x04User\x12\n\n\x02id\x18\x02 \x01(\x03\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x11\n\tname_show\x18\x04 \x01(\t\x12\x10\n\x08portrait\x18\x05 \x01(\t\x12\x1c\n\x08iconinfo\x18\x11 \x03(\x0b\x32\n.User.Icon\x12\x13\n\x0bis_coreuser\x18\x14 \x01(\x05\x12\x10\n\x08level_id\x18\x17 \x01(\x05\x12\x0f\n\x07is_bawu\x18\x19 \x01(\x05\x12\x11\n\tbawu_type\x18\x1a \x01(\t\x12\r\n\x05\x42\x44USS\x18\x1d \x01(\t\x12\x10\n\x08\x66\x61ns_num\x18\x1e \x01(\x05\x12\x13\n\x0b\x63oncern_num\x18\x1f \x01(\x05\x12\x0b\n\x03sex\x18  \x01(\x05\x12\x13\n\x0bmy_like_num\x18! \x01(\x05\x12\r\n\x05intro\x18\" \x01(\t\x12\x10\n\x08post_num\x18% \x01(\x05\x12\x0e\n\x06tb_age\x18& \x01(\t\x12\x0e\n\x06gender\x18* \x01(\x05\x12!\n\tpriv_sets\x18- \x01(\x0b\x32\x0e.User.PrivSets\x12\x11\n\tis_friend\x18. \x01(\x05\x12&\n\tlikeForum\x18/ \x03(\x0b\x32\x13.User.LikeForumInfo\x12\x13\n\x0bis_guanfang\x18\x34 \x01(\x05\x12\"\n\x07vipInfo\x18= \x01(\x0b\x32\x11.User.UserVipInfo\x12\'\n\x0enew_tshow_icon\x18\x41 \x03(\x0b\x32\x0f.User.TshowInfo\x12\x0f\n\x07is_fans\x18[ \x01(\x05\x12&\n\x0cnew_god_data\x18\x65 \x01(\x0b\x32\x10.User.NewGodInfo\x12\x19\n\x11is_default_avatar\x18j \x01(\x05\x12\x11\n\ttieba_uid\x18x \x01(\t\x12\x12\n\nip_address\x18\x7f \x01(\t\x12\x33\n\x12virtual_image_info\x18\x88\x01 \x01(\x0b\x32\x16.User.VirtualImageInfo\x12&\n\x0buser_growth\x18\x89\x01 \x01(\x0b\x32\x10.User.UserGrowth\x1a\x14\n\x04Icon\x12\x0c\n\x04name\x18\x01 \x01(\t\x1a\xab\x01\n\x08PrivSets\x12\x10\n\x08location\x18\x01 \x01(\x05\x12\x0c\n\x04like\x18\x02 \x01(\x05\x12\r\n\x05group\x18\x03 \x01(\x05\x12\x0c\n\x04post\x18\x04 \x01(\x05\x12\x0e\n\x06\x66riend\x18\x05 \x01(\x05\x12\x0c\n\x04live\x18\x06 \x01(\x05\x12\r\n\x05reply\x18\x07 \x01(\x05\x12\x19\n\x11\x62\x61zhu_show_inside\x18\x08 \x01(\x05\x12\x1a\n\x12\x62\x61zhu_show_outside\x18\t \x01(\x05\x1a\x35\n\rLikeForumInfo\x12\x12\n\nforum_name\x18\x01 \x01(\t\x12\x10\n\x08\x66orum_id\x18\x02 \x01(\x04\x1a\x30\n\x0bUserVipInfo\x12\x10\n\x08v_status\x18\x01 \x01(\r\x12\x0f\n\x07v_level\x18\x05 \x01(\r\x1a\x19\n\tTshowInfo\x12\x0c\n\x04name\x18\x02 \x01(\t\x1a\x42\n\nNewGodInfo\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x10\n\x08\x66ield_id\x18\x02 \x01(\r\x12\x12\n\nfield_name\x18\x03 \x01(\t\x1a\x84\x01\n\x10VirtualImageInfo\x12\x1b\n\x13isset_virtual_image\x18\x01 \x01(\x05\x12\x38\n\x0epersonal_state\x18\t \x01(\x0b\x32 .User.VirtualImageInfo.StateInfo\x1a\x19\n\tStateInfo\x12\x0c\n\x04text\x18\x02 \x01(\t\x1a\x1e\n\nUserGrowth\x12\x10\n\x08level_id\x18\x01 \x01(\rb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'User_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_USER']._serialized_start = 15
    _globals['_USER']._serialized_end = 1313
    _globals['_USER_ICON']._serialized_start = 752
    _globals['_USER_ICON']._serialized_end = 772
    _globals['_USER_PRIVSETS']._serialized_start = 775
    _globals['_USER_PRIVSETS']._serialized_end = 946
    _globals['_USER_LIKEFORUMINFO']._serialized_start = 948
    _globals['_USER_LIKEFORUMINFO']._serialized_end = 1001
    _globals['_USER_USERVIPINFO']._serialized_start = 1003
    _globals['_USER_USERVIPINFO']._serialized_end = 1051
    _globals['_USER_TSHOWINFO']._serialized_start = 1053
    _globals['_USER_TSHOWINFO']._serialized_end = 1078
    _globals['_USER_NEWGODINFO']._serialized_start = 1080
    _globals['_USER_NEWGODINFO']._serialized_end = 1146
    _globals['_USER_VIRTUALIMAGEINFO']._serialized_start = 1149
    _globals['_USER_VIRTUALIMAGEINFO']._serialized_end = 1281
    _globals['_USER_VIRTUALIMAGEINFO_STATEINFO']._serialized_start = 1256
    _globals['_USER_VIRTUALIMAGEINFO_STATEINFO']._serialized_end = 1281
    _globals['_USER_USERGROWTH']._serialized_start = 1283
    _globals['_USER_USERGROWTH']._serialized_end = 1313
