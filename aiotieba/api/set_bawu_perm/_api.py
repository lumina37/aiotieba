import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...enums import BawuPermType
from ...exception import BoolResponse, TiebaServerError
from ...helper import pack_json, parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])


def pack_perm_settings(perms: BawuPermType) -> list:
    perm2id = [
        (BawuPermType.UNBLOCK, 4),
        (BawuPermType.UNBLOCK_APPEAL, 5),
        (BawuPermType.RECOVER, 3),
        (BawuPermType.RECOVER_APPEAL, 2),
    ]
    perm_settings = []

    for perm, id_ in perm2id:
        switch = 1 if perms & perm else 0
        perm_setting = {"switch": switch, "perm": id_}
        perm_settings.append(perm_setting)

    return perm_settings


async def request(http_core: HttpCore, fid: int, portrait: str, perms: BawuPermType) -> BoolResponse:
    data = [
        ('forum_id', fid),
        ('auth_user_portrait', portrait),
        ('perm_setting', pack_json(pack_perm_settings(perms))),
    ]

    request = http_core.pack_web_form_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/setAuthToolPerm"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    parse_body(body)

    return BoolResponse()
