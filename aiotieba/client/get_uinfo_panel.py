import httpx

from .._exception import TiebaServerError
from .common.helper import jsonlib, raise_for_status, url
from .common.typedef import UserInfo


def pack_request(client: httpx.AsyncClient, name_or_portrait: str) -> httpx.Request:

    params = {'id' if UserInfo.is_portrait(name_or_portrait) else 'un': name_or_portrait}

    request = httpx.Request(
        "GET",
        url("https", "tieba.baidu.com", "/home/get/panel"),
        params=params,
        headers=client.headers,
        cookies=client.cookies,
    )

    return request


def _num2int(tb_num: str) -> int:
    """
    将贴吧数字字符串转为int
    可能会以xx万作为单位

    Args:
        tb_num (str): 贴吧数字字符串

    Returns:
        int: 对应数字
    """

    if isinstance(tb_num, str):
        return int(float(tb_num.removesuffix('万')) * 1e4)
    else:
        return tb_num


def parse_response(response: httpx.Response) -> UserInfo:
    raise_for_status(response)

    res_json = jsonlib.loads(response.content)
    if code := int(res_json['no']):
        raise TiebaServerError(code, res_json['error'])

    user_dict = res_json['data']
    user = UserInfo()

    # user.user_id = user_dict['id']
    user.user_name = user_dict['name']
    user.portrait = user_dict['portrait']
    user.nick_name = user_dict['show_nickname']

    _sex = user_dict['sex']
    if _sex == 'male':
        user.gender = 1
    elif _sex == 'female':
        user.gender = 2
    else:
        user.gender = 0

    user.age = float(tb_age) if (tb_age := user_dict['tb_age']) != '-' else 0.0

    user.post_num = _num2int(user_dict['post_num'])
    user.fan_num = _num2int(user_dict['followed_count'])

    user.is_vip = bool(int(vip_dict['v_status'])) if (vip_dict := user_dict['vipInfo']) else False

    return user
