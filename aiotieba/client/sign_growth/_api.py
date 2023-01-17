import httpx

from .._exception import TiebaServerError
from .._helper import WEB_BASE_HOST, pack_form_request, parse_json, raise_for_status, url


def pack_request(client: httpx.AsyncClient, tbs: str) -> httpx.Request:

    data = [
        ('tbs', tbs),
        ('act_type', 'page_sign'),
        ('cuid', ' '),
    ]

    request = pack_form_request(
        client,
        url("https", WEB_BASE_HOST, "/mo/q/usergrowth/commitUGTaskInfo"),
        data,
    )

    return request


def parse_response(response: httpx.Response) -> None:
    raise_for_status(response)

    res_json = parse_json(response.content)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])
