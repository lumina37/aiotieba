import binascii
import sys
import time
from typing import List

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from .._core import TbCore, WsCore
from .._helper import log_exception, pack_json
from ..exception import TiebaServerError
from ._classdef import WsMsgGroupInfo
from .protobuf import UpdateClientInfoReqIdl_pb2, UpdateClientInfoResIdl_pb2

CMD = 1001


PUBLIC_KEY = binascii.a2b_base64(
    b"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwQpwBZxXJV/JVRF/uNfyMSdu7YWwRNLM8+2xbniGp2iIQHOikPpTYQjlQgMi1uvq1kZpJ32rHo3hkwjy2l0lFwr3u4Hk2Wk7vnsqYQjAlYlK0TCzjpmiI+OiPOUNVtbWHQiLiVqFtzvpvi4AU7C1iKGvc/4IS45WjHxeScHhnZZ7njS4S1UgNP/GflRIbzgbBhyZ9kEW5/OO5YfG1fy6r4KSlDJw4o/mw5XhftyIpL+5ZBVBC6E1EIiP/dd9AbK62VV1PByfPMHMixpxI3GM2qwcmFsXcCcgvUXJBa9k6zP8dDQ3csCM2QNT+CQAOxthjtp/TFWaD7MzOdsIYb3THwIDAQAB"
)


def pack_proto(core: TbCore) -> bytes:
    req_proto = UpdateClientInfoReqIdl_pb2.UpdateClientInfoReqIdl()
    req_proto.data.bduss = core._BDUSS

    device = {
        'subapp_type': 'mini',
        'cuid': core.cuid,
        '_client_version': core.post_version,
        'pversion': '1.0.3',
        '_msg_status': '1',
        '_phone_imei': '000000000000000',
        'from': "1021099l",
        'cuid_galaxy2': core.cuid_galaxy2,
        '_client_type': '2',
        'timestamp': str(int(time.time() * 1e3)),
    }
    req_proto.data.device = pack_json(device)

    rsa_chiper = PKCS1_v1_5.new(RSA.import_key(PUBLIC_KEY))
    secret_key = rsa_chiper.encrypt(core.aes_ecb_sec_key)
    req_proto.data.secretKey = secret_key

    req_proto.data.width = 105
    req_proto.data.height = 105
    req_proto.data.stoken = core._STOKEN
    req_proto.cuid = f"{core.cuid}|com.baidu.tieba_mini{core.post_version}"

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> List[WsMsgGroupInfo]:
    res_proto = UpdateClientInfoResIdl_pb2.UpdateClientInfoResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    groups = [WsMsgGroupInfo()._init(p) for p in res_proto.data.groupInfo]

    return groups


async def request(ws_core: WsCore) -> List[WsMsgGroupInfo]:
    data = pack_proto(ws_core.core)

    try:
        resq = await ws_core.send(data, CMD, compress=False, encrypt=False)
        groups = parse_body(await resq.read())

    except Exception as err:
        log_exception(sys._getframe(1), err)
        groups = []

    return groups
