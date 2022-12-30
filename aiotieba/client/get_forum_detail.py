import httpx
from google.protobuf.json_format import ParseDict

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign
from .common.protobuf import ForumList_pb2
from .common.typedef import Forum


def pack_request(client: httpx.AsyncClient, version: str, fid: int) -> httpx.Request:

    data = [
        ('_client_version', version),
        ('forum_id', fid),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/f/forum/getforumdetail", sign(data))

    return request


def parse_response(response: httpx.Response) -> Forum:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    forum_dict = res_json['forum_info']
    forum_dict['thread_num'] = forum_dict.pop('thread_count')

    forum = Forum(ParseDict(forum_dict, ForumList_pb2.ForumList(), ignore_unknown_fields=True))

    return forum
