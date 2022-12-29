import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, pack_form_request, sign


def pack_request(client: httpx.AsyncClient, bduss: str, fname: str) -> httpx.Request:

    data = [
        ('BDUSS', bduss),
        ('word', fname),
    ]

    request = pack_form_request(client, "http://tiebac.baidu.com/c/c/bawu/goodlist", sign(data))

    return request


def parse_response(response: httpx.Response, cname: str) -> int:
    response.raise_for_status()

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    cid = 0
    for item in res_json['cates']:
        if cname == item['class_name']:
            cid = int(item['class_id'])
            break

    return cid
