"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import CommonReq_pb2 as CommonReq__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13\x41\x64\x64PostReqIdl.proto\x1a\x0f\x43ommonReq.proto\"\x82\x04\n\rAddPostReqIdl\x12$\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x16.AddPostReqIdl.DataReq\x1a\xca\x03\n\x07\x44\x61taReq\x12\x1a\n\x06\x63ommon\x18\x01 \x01(\x0b\x32\n.CommonReq\x12\x11\n\tanonymous\x18\x06 \x01(\t\x12\x14\n\x0c\x63\x61n_no_forum\x18\x07 \x01(\t\x12\x13\n\x0bis_feedback\x18\x08 \x01(\t\x12\x15\n\rtakephoto_num\x18\t \x01(\t\x12\x15\n\rentrance_type\x18\n \x01(\t\x12\x11\n\tvcode_tag\x18\x10 \x01(\t\x12\x11\n\tnew_vcode\x18\x12 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x13 \x01(\t\x12\x0b\n\x03\x66id\x18\x1a \x01(\t\x12\r\n\x05v_fid\x18\x1c \x01(\t\x12\x0f\n\x07v_fname\x18\x1d \x01(\t\x12\n\n\x02kw\x18\x1e \x01(\t\x12\x12\n\nis_barrage\x18\x1f \x01(\t\x12\x14\n\x0c\x62\x61rrage_time\x18  \x01(\t\x12\x15\n\rfrom_fourm_id\x18, \x01(\t\x12\x0b\n\x03tid\x18- \x01(\t\x12\r\n\x05is_ad\x18\x33 \x01(\t\x12\x11\n\tpost_from\x18\x37 \x01(\t\x12\x11\n\tname_show\x18: \x01(\t\x12\x11\n\tis_pictxt\x18< \x01(\t\x12\x1a\n\x12show_custom_figure\x18@ \x01(\x05\x12\x15\n\ris_show_bless\x18\x43 \x01(\x05\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'AddPostReqIdl_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_ADDPOSTREQIDL']._serialized_start = 41
    _globals['_ADDPOSTREQIDL']._serialized_end = 555
    _globals['_ADDPOSTREQIDL_DATAREQ']._serialized_start = 97
    _globals['_ADDPOSTREQIDL_DATAREQ']._serialized_end = 555
