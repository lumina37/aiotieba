import aiohttp
import yarl

from .._core import APP_BASE_HOST, TbCore
from .._exception import TiebaServerError
from .._helper import APP_SECURE_SCHEME, pack_form_request, parse_json, send_request


async def request(
    connector: aiohttp.TCPConnector, core: TbCore, tbs: str, tid: int, pid: int, is_disagree: bool, is_undo: bool
) -> bytes:

    data = [
        ('BDUSS', core._BDUSS),
        ('_client_version', core.main_version),
        ('agree_type', '5' if is_disagree else '2'),
        ('cuid', core.cuid_galaxy2),
        ('obj_type', '1' if pid else '3'),
        ('op_type', str(int(is_undo))),
        ('post_id', pid),
        ('tbs', tbs),
        ('thread_id', tid),
    ]

    request = pack_form_request(
        core,
        yarl.URL.build(scheme=APP_SECURE_SCHEME, host=APP_BASE_HOST, path="/c/c/agree/opAgree"),
        data,
    )

    body = await send_request(request, connector, read_bufsize=1024)

    return body


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json['error_code']):
        raise TiebaServerError(code, res_json['error_msg'])
