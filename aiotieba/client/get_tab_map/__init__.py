import httpx

from ..._exception import TiebaServerError
from ..common.helper import pack_proto_request
from ..common.typedef import UserInfo
from .protobuf import SearchPostForumReqIdl_pb2, SearchPostForumResIdl_pb2


def pack_request(client: httpx.AsyncClient, bduss: str, version: str, fname: str) -> httpx.Request:

    req_proto = SearchPostForumReqIdl_pb2.SearchPostForumReqIdl()
    req_proto.data.common.BDUSS = bduss
    req_proto.data.common._client_version = version
    req_proto.data.fname = fname

    request = pack_proto_request(
        client,
        "http://tiebac.baidu.com/c/f/forum/searchPostForum?cmd=309466",
        req_proto.SerializeToString(),
    )

    return request


def parse_response(response: httpx.Response) -> UserInfo:
    response.raise_for_status()

    res_proto = SearchPostForumResIdl_pb2.SearchPostForumResIdl()
    res_proto.ParseFromString(response.content)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    tab_map = {tab_proto.tab_name: tab_proto.tab_id for tab_proto in res_proto.data.exact_match.tab_info}

    return tab_map
