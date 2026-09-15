from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\nUser.proto"\xe0\x06\n\x04User\x12\n\n\x02id\x18\x02 \x01(\x03\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x11\n\tname_show\x18\x04 \x01(\t\x12\x10\n\x08portrait\x18\x05 \x01(\t\x12\x1c\n\x08iconinfo\x18\x11 \x03(\x0b\x32\n.User.Icon\x12\x13\n\x0bis_coreuser\x18\x14 \x01(\x05\x12\x10\n\x08level_id\x18\x17 \x01(\x05\x12\x0f\n\x07is_bawu\x18\x19 \x01(\x05\x12\x11\n\tbawu_type\x18\x1a \x01(\t\x12\r\n\x05\x42\x44USS\x18\x1d \x01(\t\x12\x10\n\x08\x66\x61ns_num\x18\x1e \x01(\x05\x12\x13\n\x0b\x63oncern_num\x18\x1f \x01(\x05\x12\x0b\n\x03sex\x18  \x01(\x05\x12\x13\n\x0bmy_like_num\x18! \x01(\x05\x12\r\n\x05intro\x18" \x01(\t\x12\x10\n\x08post_num\x18% \x01(\x05\x12\x0e\n\x06tb_age\x18& \x01(\t\x12\x0e\n\x06is_mem\x18\' \x01(\x05\x12\x0e\n\x06gender\x18* \x01(\x05\x12!\n\tpriv_sets\x18- \x01(\x0b\x32\x0e.User.PrivSets\x12\x11\n\tis_friend\x18. \x01(\x05\x12&\n\tlikeForum\x18/ \x03(\x0b\x32\x13.User.LikeForumInfo\x12\x13\n\x0bis_guanfang\x18\x34 \x01(\x05\x12\x0f\n\x07is_fans\x18[ \x01(\x05\x12\x19\n\x11is_default_avatar\x18j \x01(\x05\x12\x11\n\ttieba_uid\x18x \x01(\t\x12\x12\n\nip_address\x18\x7f \x01(\t\x12&\n\x0buser_growth\x18\x89\x01 \x01(\x0b\x32\x10.User.UserGrowth\x1a\x14\n\x04Icon\x12\x0c\n\x04name\x18\x01 \x01(\t\x1a\xab\x01\n\x08PrivSets\x12\x10\n\x08location\x18\x01 \x01(\x05\x12\x0c\n\x04like\x18\x02 \x01(\x05\x12\r\n\x05group\x18\x03 \x01(\x05\x12\x0c\n\x04post\x18\x04 \x01(\x05\x12\x0e\n\x06\x66riend\x18\x05 \x01(\x05\x12\x0c\n\x04live\x18\x06 \x01(\x05\x12\r\n\x05reply\x18\x07 \x01(\x05\x12\x19\n\x11\x62\x61zhu_show_inside\x18\x08 \x01(\x05\x12\x1a\n\x12\x62\x61zhu_show_outside\x18\t \x01(\x05\x1a\x35\n\rLikeForumInfo\x12\x12\n\nforum_name\x18\x01 \x01(\t\x12\x10\n\x08\x66orum_id\x18\x02 \x01(\x04\x1a\x1e\n\nUserGrowth\x12\x10\n\x08level_id\x18\x01 \x01(\rb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "User_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_USER"]._serialized_start = 15
    _globals["_USER"]._serialized_end = 879
    _globals["_USER_ICON"]._serialized_start = 598
    _globals["_USER_ICON"]._serialized_end = 618
    _globals["_USER_PRIVSETS"]._serialized_start = 621
    _globals["_USER_PRIVSETS"]._serialized_end = 792
    _globals["_USER_LIKEFORUMINFO"]._serialized_start = 794
    _globals["_USER_LIKEFORUMINFO"]._serialized_end = 847
    _globals["_USER_USERGROWTH"]._serialized_start = 849
    _globals["_USER_USERGROWTH"]._serialized_end = 879
