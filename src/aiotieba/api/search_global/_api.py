from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

import yarl

from ...const import WEB_BASE_HOST
from ...exception import TiebaServerError
from ...helper import parse_json
from ._classdef import GlobalSearches

if TYPE_CHECKING:
    from ...core import HttpCore

# PC网页端搜索结果页 保留Referer可降低风控概率
REFERER_GLOBAL = "https://tieba.baidu.com/f/search/res"
# subapp_type=pc专属签名密钥 逆向PC网页端js所得
PC_SIGN_SECRET = "36770b1f34c9bbf2e7d1a99d2b82fa9e"


def _pc_sign(params: list[tuple[str, object]]) -> str:
    """
    PC网页端签名算法

    取除sign/sig外的全部参数 按key升序排序 逐个"key=value"无分隔拼接
    末尾拼接密钥 整体UTF-8编码后取MD5十六进制

    Args:
        params (list[tuple[str, object]]): 待签名的参数元组列表

    Returns:
        str: 32位十六进制MD5签名
    """

    kvs = sorted((k, v) for k, v in params if k not in ("sign", "sig"))
    raw = "".join(f"{k}={v}" for k, v in kvs) + PC_SIGN_SECRET
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def parse_body(body: bytes) -> GlobalSearches:
    res_json = parse_json(body)
    if code := int(res_json["no"]):
        raise TiebaServerError(code, res_json.get("error", ""))

    searches = GlobalSearches.from_json(res_json["data"])

    return searches


async def request(
    http_core: HttpCore,
    word: str,
    pn: int,
    rn: int,
    sort: int,
) -> GlobalSearches:
    params = [
        ("word", word),
        ("pn", pn),
        ("rn", rn),
        ("st", sort),
        ("tt", 1),
        ("subapp_type", "pc"),
        ("_client_type", 20),
    ]
    params.append(("sign", _pc_sign(params)))

    request = http_core.pack_web_get_request(
        yarl.URL.build(scheme="https", host=WEB_BASE_HOST, path="/mo/q/search/thread"),
        params,
        extra_headers=[("Referer", REFERER_GLOBAL)],
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)
