import yarl

from ...const import WEB_BASE_HOST
from ...core import HttpCore
from ...enums import BawuPerm
from ...exception import TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> BawuPerm:
    res_json = parse_json(body)
    if code := res_json['no']:
        raise TiebaServerError(code, res_json['error'])

    data_dict = res_json['data']

    perms = 0
    for cate in ['category_user', 'category_thread']:
        for unblock_perm_dict in data_dict['perm_setting'][cate]:
            if not unblock_perm_dict['switch']:
                continue

            perm_idx: int = unblock_perm_dict['perm'] - 2
            perm = [
                BawuPerm.RECOVER_APPEAL,
                BawuPerm.RECOVER,
                BawuPerm.UNBLOCK,
                BawuPerm.UNBLOCK_APPEAL,
            ][perm_idx]

            perms |= perm

    return BawuPerm(perms)


async def request(http_core: HttpCore, fid: int, portrait: str) -> BawuPerm:
    params = [
        ('forum_id', fid),
        ('portrait', portrait),
    ]

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/getAuthToolPerm"), params
    )

    body = await http_core.net_core.send_request(request, read_bufsize=4 * 1024)
    return parse_body(body)
