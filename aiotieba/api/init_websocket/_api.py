import binascii
import time
from typing import List

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from ...const import MAIN_VERSION
from ...core import Account, WsCore
from ...exception import TiebaServerError
from ...helper import pack_json
from ._classdef import WsMsgGroupInfo
from .protobuf import UpdateClientInfoReqIdl_pb2, UpdateClientInfoResIdl_pb2

CMD = 1001


PUBLIC_KEY = binascii.a2b_base64(
    b"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwQpwBZxXJV/JVRF/uNfyMSdu7YWwRNLM8+2xbniGp2iIQHOikPpTYQjlQgMi1uvq1kZpJ32rHo3hkwjy2l0lFwr3u4Hk2Wk7vnsqYQjAlYlK0TCzjpmiI+OiPOUNVtbWHQiLiVqFtzvpvi4AU7C1iKGvc/4IS45WjHxeScHhnZZ7njS4S1UgNP/GflRIbzgbBhyZ9kEW5/OO5YfG1fy6r4KSlDJw4o/mw5XhftyIpL+5ZBVBC6E1EIiP/dd9AbK62VV1PByfPMHMixpxI3GM2qwcmFsXcCcgvUXJBa9k6zP8dDQ3csCM2QNT+CQAOxthjtp/TFWaD7MzOdsIYb3THwIDAQAB"
)


def pack_proto(account: Account) -> bytes:
    req_proto = UpdateClientInfoReqIdl_pb2.UpdateClientInfoReqIdl()
    req_proto.data.bduss = account.BDUSS

    device = {
        'cuid': account.cuid,
        '_client_version': MAIN_VERSION,
        '_msg_status': '1',
        'cuid_galaxy2': account.cuid_galaxy2,
        '_client_type': '2',
        'timestamp': str(int(time.time() * 1000)),
    }
    req_proto.data.device = pack_json(device)

    rsa_chiper = PKCS1_v1_5.new(RSA.import_key(PUBLIC_KEY))
    secret_key = rsa_chiper.encrypt(account.aes_ecb_sec_key)
    req_proto.data.secretKey = secret_key
    req_proto.data.stoken = account.STOKEN
    req_proto.cuid = f"{account.cuid}|com.baidu.tieba{MAIN_VERSION}"

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> List[WsMsgGroupInfo]:
    res_proto = UpdateClientInfoResIdl_pb2.UpdateClientInfoResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    groups = [WsMsgGroupInfo.from_tbdata(p) for p in res_proto.data.groupInfo]

    return groups


async def request(ws_core: WsCore) -> List[WsMsgGroupInfo]:
    data = pack_proto(ws_core.account)

    resp = await ws_core.send(data, CMD, compress=False, encrypt=False)
    groups = parse_body(await resp.read())

    return groups
