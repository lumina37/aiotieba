import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign


def pack_request(
    client: httpx.AsyncClient, bduss: str, tbs: str, version: str, fid: int, tid: int, to_tab_id: int, from_tab_id: int
) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('_client_version', version),
        ('forum_id', fid),
        ('tbs', tbs),
        ('threads', jsonlib.dumps([{'thread_id', tid, 'from_tab_id', from_tab_id, 'to_tab_id', to_tab_id}])),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/c/bawu/moveTabThread", sign(data))

    return request


def parse_response(response: httpx.Response) -> None:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
