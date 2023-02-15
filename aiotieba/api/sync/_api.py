import yarl

from ...const import APP_BASE_HOST, APP_SECURE_SCHEME
from ...core import HttpCore
from ...exception import TiebaServerError
from ...helper import parse_json
from ...request import pack_form_request, send_request


def parse_body(body: bytes) -> str:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])

    client_id = res_json['client']['client_id']

    return client_id


async def request(http_core: HttpCore) -> str:
    data = [('BDUSS', http_core.account._BDUSS)]

    request = pack_form_request(
        http_core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/s/sync"),
        data,
    )

    body = await send_request(request, http_core.network, read_bufsize=64 * 1024)
    return parse_body(body)
