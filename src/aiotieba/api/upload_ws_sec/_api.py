from __future__ import annotations

import binascii
import time
from typing import TYPE_CHECKING

from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.serialization import load_der_public_key

from ...__version__ import __version__
from ...exception import TiebaServerError, TiebaValueError
from ...helper import pack_json
from ._classdef import InitWsInfo
from .protobuf import UpdateClientInfoReqIdl_pb2, UpdateClientInfoResIdl_pb2

if TYPE_CHECKING:
    from ...core import Account, WsCore

CMD = 1001


PUBLIC_KEY = binascii.a2b_base64(
    b"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwQpwBZxXJV/JVRF/uNfyMSdu7YWwRNLM8+2xbniGp2iIQHOikPpTYQjlQgMi1uvq1kZpJ32rHo3hkwjy2l0lFwr3u4Hk2Wk7vnsqYQjAlYlK0TCzjpmiI+OiPOUNVtbWHQiLiVqFtzvpvi4AU7C1iKGvc/4IS45WjHxeScHhnZZ7njS4S1UgNP/GflRIbzgbBhyZ9kEW5/OO5YfG1fy6r4KSlDJw4o/mw5XhftyIpL+5ZBVBC6E1EIiP/dd9AbK62VV1PByfPMHMixpxI3GM2qwcmFsXcCcgvUXJBa9k6zP8dDQ3csCM2QNT+CQAOxthjtp/TFWaD7MzOdsIYb3THwIDAQAB"
)


def pack_min_device(account: Account, client_version: str) -> dict[str, str]:
    return {
        "_client_type": "2",
        "_client_version": client_version,
    }


def pack_full_device(account: Account, client_version: str) -> dict[str, str]:
    tsec = int(time.time())
    tmsec = tsec * 1000
    date = time.localtime(tsec)

    device = {
        "model": "PDEM10",
        "brand": "Xiaomi",
        "_phone_imei": "000000000000000",
        "_os_version": "13",
        "android_id": account.android_id,
        "mac": "",
        "_client_type": "2",
        "_client_version": client_version,
        "user_agent": f"aiotieba/{__version__}",
        "_client_id": account.client_id,
        "net_type": "1",
        "net": "1",
        "cuid": account.cuid_galaxy2,
        "cuid_galaxy2": account.cuid_galaxy2,
        "c3_aid": account.c3_aid,
        "cuid_gid": "",
        "timestamp": str(tmsec),
        "sample_id": account.sample_id,
        "z_id": account.zid,
        "baiduid": account.baidu_id,
        "sdk_ver": "3.36.0",
        "framework_ver": "",
        "naws_game_ver": "",
        "_phone_screen": "1080,2340",
        "_msg_status": "0",
        "_pic_quality": "0",
        "pversion": "1.0.3",
        "q_type": "0",
        "scr_h": "2340",
        "scr_w": "1080",
        "scr_dip": "2.75",
        "active_timestamp": str(tmsec),
        "first_install_time": str(tmsec - 86400000),
        "update_time": str(tmsec - 3600000),
        "event_day": f"{date.tm_year}{date.tm_mon}{date.tm_mday}",
        "cmode": "1",
        "extra": "",
        "personalized_rec_switch": "1",
        "ad_context": "",
        "start_type": "99",
        "start_scheme": "",
    }

    return device


def pack_proto(account: Account, client_version: str, full: bool) -> bytes:
    req_proto = UpdateClientInfoReqIdl_pb2.UpdateClientInfoReqIdl()
    req_proto.data.bduss = account.BDUSS

    device = pack_full_device(account, client_version) if full else pack_min_device(account, client_version)
    req_proto.data.device = pack_json(device)

    rsa_chiper = load_der_public_key(PUBLIC_KEY)
    secret_key = rsa_chiper.encrypt(account.ws_sec_key, PKCS1v15())
    req_proto.data.secretKey = secret_key
    if full:
        req_proto.data.stoken = account.STOKEN
        req_proto.cuid = f"{account.cuid}|com.baidu.tieba{client_version}"
    else:
        req_proto.cuid = f"-|com.baidu.tieba{client_version}"

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> InitWsInfo:
    res_proto = UpdateClientInfoResIdl_pb2.UpdateClientInfoResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    user_id = data_proto.userInfo.userId
    if not user_id or data_proto.isUserAvailable != user_id:
        raise TiebaValueError(f"isUserAvailable({data_proto.isUserAvailable}) userId({user_id})")

    info = InitWsInfo.from_proto(res_proto)

    return info


async def request(ws_core: WsCore, full: bool) -> InitWsInfo:
    data = pack_proto(ws_core.account, ws_core.client_version, full)

    resp = await ws_core.send(data, CMD, compress=False, encrypt=False)
    info = parse_body(await resp.read())

    return info
