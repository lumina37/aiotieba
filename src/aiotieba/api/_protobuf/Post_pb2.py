from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from . import Agree_pb2 as Agree__pb2
from . import PbContent_pb2 as PbContent__pb2
from . import SubPostList_pb2 as SubPostList__pb2
from . import User_pb2 as User__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b"\n\nPost.proto\x1a\x0fPbContent.proto\x1a\x11SubPostList.proto\x1a\nUser.proto\x1a\x0b\x41gree.proto\"\xc4\x04\n\x04Post\x12\n\n\x02id\x18\x01 \x01(\x03\x12\r\n\x05\x66loor\x18\x03 \x01(\r\x12\x0c\n\x04time\x18\x04 \x01(\r\x12\x1b\n\x07\x63ontent\x18\x05 \x03(\x0b\x32\n.PbContent\x12\x17\n\x0fsub_post_number\x18\r \x01(\r\x12\x11\n\tauthor_id\x18\x13 \x01(\x03\x12$\n\rsub_post_list\x18\x0f \x01(\x0b\x32\r.Post.SubPost\x12&\n\tsignature\x18\x15 \x01(\x0b\x32\x13.Post.SignatureData\x12\x15\n\x06\x61uthor\x18\x17 \x01(\x0b\x32\x05.User\x12\x15\n\x05\x61gree\x18% \x01(\x0b\x32\x06.Agree\x12\x0b\n\x03tid\x18. \x01(\x03\x12'\n\x0c\x63hat_content\x18N \x01(\x0b\x32\x11.Post.ChatContent\x12.\n\x10sprite_meme_info\x18O \x01(\x0b\x32\x14.Post.SpriteMemeInfo\x1a.\n\x07SubPost\x12#\n\rsub_post_list\x18\x02 \x03(\x0b\x32\x0c.SubPostList\x1av\n\rSignatureData\x12\x35\n\x07\x63ontent\x18\x04 \x03(\x0b\x32$.Post.SignatureData.SignatureContent\x1a.\n\x10SignatureContent\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\x0c\n\x04text\x18\x02 \x01(\t\x1a\x1d\n\x0b\x43hatContent\x12\x0e\n\x06\x62ot_uk\x18\x01 \x01(\t\x1a!\n\x0eSpriteMemeInfo\x12\x0f\n\x07meme_id\x18\x01 \x01(\x03\x62\x06proto3"
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "Post_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_POST"]._serialized_start = 76
    _globals["_POST"]._serialized_end = 656
    _globals["_POST_SUBPOST"]._serialized_start = 424
    _globals["_POST_SUBPOST"]._serialized_end = 470
    _globals["_POST_SIGNATUREDATA"]._serialized_start = 472
    _globals["_POST_SIGNATUREDATA"]._serialized_end = 590
    _globals["_POST_SIGNATUREDATA_SIGNATURECONTENT"]._serialized_start = 544
    _globals["_POST_SIGNATUREDATA_SIGNATURECONTENT"]._serialized_end = 590
    _globals["_POST_CHATCONTENT"]._serialized_start = 592
    _globals["_POST_CHATCONTENT"]._serialized_end = 621
    _globals["_POST_SPRITEMEMEINFO"]._serialized_start = 623
    _globals["_POST_SPRITEMEMEINFO"]._serialized_end = 656
