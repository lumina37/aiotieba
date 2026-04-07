"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\tLcm.proto"\xd5\x01\n\x06\x43ommon\x12\x0c\n\x04\x63uid\x18\x01 \x01(\t\x12\x0e\n\x06\x64\x65vice\x18\x02 \x01(\t\x12\x12\n\nos_version\x18\x03 \x01(\t\x12\x13\n\x0bmanufacture\x18\x04 \x01(\t\x12\x12\n\nmodel_type\x18\x05 \x01(\t\x12\x0e\n\x06\x61pp_id\x18\x06 \x01(\t\x12\x13\n\x0b\x61pp_version\x18\x07 \x01(\t\x12\x13\n\x0bsdk_version\x18\x08 \x01(\t\x12\x0f\n\x07network\x18\t \x01(\t\x12\x13\n\x0brom_version\x18\n \x01(\t\x12\x10\n\x08user_key\x18\x0b \x01(\t"+\n\tLcmNotify\x12\x0e\n\x06log_id\x18\x01 \x01(\x03\x12\x0e\n\x06\x61\x63tion\x18\x02 \x01(\x05"\x8e\x01\n\nLcmRequest\x12\x0e\n\x06log_id\x18\x01 \x01(\x03\x12\r\n\x05token\x18\x02 \x01(\t\x12\x17\n\x06\x63ommon\x18\x03 \x01(\x0b\x32\x07.Common\x12\x11\n\ttimestamp\x18\x04 \x01(\x03\x12\x0e\n\x06\x61\x63tion\x18\x05 \x01(\x05\x12\x12\n\nstart_type\x18\x06 \x01(\x05\x12\x11\n\tconn_type\x18\x07 \x01(\x05"s\n\x0bLcmResponse\x12\x0e\n\x06log_id\x18\x01 \x01(\x03\x12\x12\n\nerror_code\x18\x02 \x01(\x05\x12\x11\n\terror_msg\x18\x03 \x01(\t\x12\x18\n\x10next_interval_ms\x18\x04 \x01(\x03\x12\x13\n\x0bserver_info\x18\x05 \x01(\t"o\n\x07RpcData\x12 \n\x0blcm_request\x18\x01 \x01(\x0b\x32\x0b.LcmRequest\x12"\n\x0clcm_response\x18\x02 \x01(\x0b\x32\x0c.LcmResponse\x12\x1e\n\nlcm_notify\x18\x03 \x01(\x0b\x32\n.LcmNotifyB\x02H\x03\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "Lcm_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    _globals["DESCRIPTOR"]._loaded_options = None
    _globals["DESCRIPTOR"]._serialized_options = b"H\003"
    _globals["_COMMON"]._serialized_start = 14
    _globals["_COMMON"]._serialized_end = 227
    _globals["_LCMNOTIFY"]._serialized_start = 229
    _globals["_LCMNOTIFY"]._serialized_end = 272
    _globals["_LCMREQUEST"]._serialized_start = 275
    _globals["_LCMREQUEST"]._serialized_end = 417
    _globals["_LCMRESPONSE"]._serialized_start = 419
    _globals["_LCMRESPONSE"]._serialized_end = 534
    _globals["_RPCDATA"]._serialized_start = 536
    _globals["_RPCDATA"]._serialized_end = 647
