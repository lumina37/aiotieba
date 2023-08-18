"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from . import Agree_pb2 as Agree__pb2
from . import Media_pb2 as Media__pb2
from . import PbContent_pb2 as PbContent__pb2
from . import PollInfo_pb2 as PollInfo__pb2
from . import User_pb2 as User__pb2
from . import VideoInfo_pb2 as VideoInfo__pb2
from . import Voice_pb2 as Voice__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x10ThreadInfo.proto\x1a\nUser.proto\x1a\x0bVoice.proto\x1a\x0ePollInfo.proto\x1a\x0fVideoInfo.proto\x1a\x0fPbContent.proto\x1a\x0b\x41gree.proto\x1a\x0bMedia.proto\"\xcc\x08\n\nThreadInfo\x12\n\n\x02id\x18\x01 \x01(\x03\x12\r\n\x05title\x18\x03 \x01(\t\x12\x11\n\treply_num\x18\x04 \x01(\x05\x12\x10\n\x08view_num\x18\x05 \x01(\x05\x12\x15\n\rlast_time_int\x18\x07 \x01(\x05\x12\x0e\n\x06is_top\x18\t \x01(\x05\x12\x0f\n\x07is_good\x18\n \x01(\x05\x12\x17\n\x0fis_voice_thread\x18\x0f \x01(\x05\x12\x15\n\x06\x61uthor\x18\x12 \x01(\x0b\x32\x05.User\x12\x1a\n\nvoice_info\x18\x17 \x03(\x0b\x32\x06.Voice\x12\x13\n\x0bthread_type\x18\x1a \x01(\x05\x12\x0b\n\x03\x66id\x18\x1b \x01(\x03\x12\r\n\x05\x66name\x18\x1c \x01(\t\x12\x13\n\x0bis_livepost\x18\x1e \x01(\x05\x12\x15\n\rfirst_post_id\x18( \x01(\x03\x12\x13\n\x0b\x63reate_time\x18- \x01(\x05\x12\x0f\n\x07post_id\x18\x34 \x01(\x03\x12\x11\n\tauthor_id\x18\x38 \x01(\x03\x12\r\n\x05is_ad\x18; \x01(\r\x12\x1c\n\tpoll_info\x18J \x01(\x0b\x32\t.PollInfo\x12\x1e\n\nvideo_info\x18O \x01(\x0b\x32\n.VideoInfo\x12\x1e\n\x16is_godthread_recommend\x18U \x01(\x05\x12\x15\n\x05\x61gree\x18~ \x01(\x0b\x32\x06.Agree\x12\x12\n\tshare_num\x18\x87\x01 \x01(\x05\x12\x39\n\x12origin_thread_info\x18\x8d\x01 \x01(\x0b\x32\x1c.ThreadInfo.OriginThreadInfo\x12\'\n\x12\x66irst_post_content\x18\x8e\x01 \x03(\x0b\x32\n.PbContent\x12\x18\n\x0fis_share_thread\x18\x8f\x01 \x01(\x05\x12\x0f\n\x06tab_id\x18\xaf\x01 \x01(\x05\x12\x13\n\nis_deleted\x18\xb5\x01 \x01(\x05\x12\x14\n\x0bis_frs_mask\x18\xc6\x01 \x01(\x05\x12\x30\n\rcustom_figure\x18\xd3\x01 \x01(\x0b\x32\x18.ThreadInfo.CustomFigure\x12.\n\x0c\x63ustom_state\x18\xd4\x01 \x01(\x0b\x32\x17.ThreadInfo.CustomState\x1a\xe5\x01\n\x10OriginThreadInfo\x12\r\n\x05title\x18\x01 \x01(\t\x12\x15\n\x05media\x18\x02 \x03(\x0b\x32\x06.Media\x12\r\n\x05\x66name\x18\x04 \x01(\t\x12\x0b\n\x03tid\x18\x05 \x01(\t\x12\x0b\n\x03\x66id\x18\x07 \x01(\x03\x12\x1a\n\nvoice_info\x18\x0c \x03(\x0b\x32\x06.Voice\x12\x1e\n\nvideo_info\x18\r \x01(\x0b\x32\n.VideoInfo\x12\x1b\n\x07\x63ontent\x18\x0e \x03(\x0b\x32\n.PbContent\x12\x1c\n\tpoll_info\x18\x15 \x01(\x0b\x32\t.PollInfo\x12\x0b\n\x03pid\x18\x19 \x01(\x03\x1a(\n\x0c\x43ustomFigure\x12\x18\n\x10\x62\x61\x63kground_value\x18\x03 \x01(\t\x1a\x1e\n\x0b\x43ustomState\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ThreadInfo_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    _globals['_THREADINFO']._serialized_start = 122
    _globals['_THREADINFO']._serialized_end = 1222
    _globals['_THREADINFO_ORIGINTHREADINFO']._serialized_start = 919
    _globals['_THREADINFO_ORIGINTHREADINFO']._serialized_end = 1148
    _globals['_THREADINFO_CUSTOMFIGURE']._serialized_start = 1150
    _globals['_THREADINFO_CUSTOMFIGURE']._serialized_end = 1190
    _globals['_THREADINFO_CUSTOMSTATE']._serialized_start = 1192
    _globals['_THREADINFO_CUSTOMSTATE']._serialized_end = 1222
