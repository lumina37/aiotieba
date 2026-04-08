"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x17GetBawuInfoResIdl.proto\x1a\x0b\x45rror.proto"\xe0\x02\n\x07\x44\x61taRes\x12)\n\x0e\x62\x61wu_team_info\x18\x01 \x01(\x0b\x32\x11.DataRes.BawuTeam\x1a\xa9\x02\n\x08\x42\x61wuTeam\x12\x11\n\ttotal_num\x18\x01 \x01(\x05\x12\x35\n\x0e\x62\x61wu_team_list\x18\x02 \x03(\x0b\x32\x1d.DataRes.BawuTeam.BawuRoleDes\x1a\xd2\x01\n\x0b\x42\x61wuRoleDes\x12\x11\n\trole_name\x18\x01 \x01(\t\x12@\n\trole_info\x18\x02 \x03(\x0b\x32-.DataRes.BawuTeam.BawuRoleDes.BawuRoleInfoPub\x1an\n\x0f\x42\x61wuRoleInfoPub\x12\x0f\n\x07user_id\x18\x02 \x01(\x03\x12\x10\n\x08portrait\x18\x05 \x01(\t\x12\x12\n\nuser_level\x18\x06 \x01(\x05\x12\x11\n\tuser_name\x18\x08 \x01(\t\x12\x11\n\tname_show\x18\t \x01(\t"B\n\x11GetBawuInfoResIdl\x12\x16\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x08.DataRes\x12\x15\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x06.Errorb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "GetBawuInfoResIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_DATARES"]._serialized_start = 41
    _globals["_DATARES"]._serialized_end = 393
    _globals["_DATARES_BAWUTEAM"]._serialized_start = 96
    _globals["_DATARES_BAWUTEAM"]._serialized_end = 393
    _globals["_DATARES_BAWUTEAM_BAWUROLEDES"]._serialized_start = 183
    _globals["_DATARES_BAWUTEAM_BAWUROLEDES"]._serialized_end = 393
    _globals["_DATARES_BAWUTEAM_BAWUROLEDES_BAWUROLEINFOPUB"]._serialized_start = 283
    _globals["_DATARES_BAWUTEAM_BAWUROLEDES_BAWUROLEINFOPUB"]._serialized_end = 393
    _globals["_GETBAWUINFORESIDL"]._serialized_start = 395
    _globals["_GETBAWUINFORESIDL"]._serialized_end = 461
