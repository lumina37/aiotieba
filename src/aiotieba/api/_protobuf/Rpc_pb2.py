"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\tRpc.proto"0\n\tChunkInfo\x12\x11\n\tstream_id\x18\x01 \x01(\x03\x12\x10\n\x08\x63hunk_id\x18\x02 \x01(\x03"5\n\x0e\x45ventTimestamp\x12\r\n\x05\x65vent\x18\x01 \x01(\t\x12\x14\n\x0ctimestamp_ms\x18\x02 \x01(\x03"k\n\rRpcNotifyMeta\x12\x12\n\nservice_id\x18\x01 \x01(\x03\x12\x11\n\tmethod_id\x18\x02 \x01(\x03\x12\x0e\n\x06log_id\x18\x03 \x01(\x03\x12#\n\nevent_list\x18\x04 \x03(\x0b\x32\x0f.EventTimestamp"\x81\x01\n\x0eRpcRequestMeta\x12\x12\n\nservice_id\x18\x01 \x01(\x03\x12\x11\n\tmethod_id\x18\x02 \x01(\x03\x12\x0e\n\x06log_id\x18\x03 \x01(\x03\x12\x13\n\x0bneed_common\x18\x04 \x01(\x05\x12#\n\nevent_list\x18\x05 \x03(\x0b\x32\x0f.EventTimestamp"\x95\x01\n\x0fRpcResponseMeta\x12\x12\n\nservice_id\x18\x01 \x01(\x03\x12\x11\n\tmethod_id\x18\x02 \x01(\x03\x12\x0e\n\x06log_id\x18\x03 \x01(\x03\x12\x12\n\nerror_code\x18\x04 \x01(\x05\x12\x12\n\nerror_text\x18\x05 \x01(\t\x12#\n\nevent_list\x18\x06 \x03(\x0b\x32\x0f.EventTimestamp"\xa9\x02\n\x07RpcMeta\x12 \n\x07request\x18\x01 \x01(\x0b\x32\x0f.RpcRequestMeta\x12"\n\x08response\x18\x02 \x01(\x0b\x32\x10.RpcResponseMeta\x12\x1a\n\rcompress_type\x18\x03 \x01(\x05H\x00\x88\x01\x01\x12\x16\n\x0e\x63orrelation_id\x18\x04 \x01(\x03\x12\x17\n\x0f\x61ttachment_size\x18\x05 \x01(\x05\x12\x1e\n\nchunk_info\x18\x06 \x01(\x0b\x32\n.ChunkInfo\x12\x1b\n\x13\x61uthentication_data\x18\x07 \x01(\x0c\x12\x1e\n\x06notify\x18\x08 \x01(\x0b\x32\x0e.RpcNotifyMeta\x12\x1c\n\x14\x61\x63\x63\x65pt_compress_type\x18\t \x01(\x05\x42\x10\n\x0e_compress_typeB\x02H\x03\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "Rpc_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    _globals["DESCRIPTOR"]._loaded_options = None
    _globals["DESCRIPTOR"]._serialized_options = b"H\003"
    _globals["_CHUNKINFO"]._serialized_start = 13
    _globals["_CHUNKINFO"]._serialized_end = 61
    _globals["_EVENTTIMESTAMP"]._serialized_start = 63
    _globals["_EVENTTIMESTAMP"]._serialized_end = 116
    _globals["_RPCNOTIFYMETA"]._serialized_start = 118
    _globals["_RPCNOTIFYMETA"]._serialized_end = 225
    _globals["_RPCREQUESTMETA"]._serialized_start = 228
    _globals["_RPCREQUESTMETA"]._serialized_end = 357
    _globals["_RPCRESPONSEMETA"]._serialized_start = 360
    _globals["_RPCRESPONSEMETA"]._serialized_end = 509
    _globals["_RPCMETA"]._serialized_start = 512
    _globals["_RPCMETA"]._serialized_end = 809
