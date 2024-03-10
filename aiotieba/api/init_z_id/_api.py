import binascii
import gzip
import hashlib
import time

import aiohttp
import yarl
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ...const import MAIN_VERSION
from ...core import HttpCore
from ...helper import pack_json, parse_json
from ...helper.crypto import rc4_42

SOFIRE_HOST = "sofire.baidu.com"


async def request(http_core: HttpCore):
    app_key = '200033'  # get by p/5/aio
    sec_key = 'ea737e4f435b53786043369d2e5ace4f'
    xyus = (
        hashlib.md5((http_core.account.android_id + http_core.account.uuid).encode('ascii')).hexdigest().upper() + '|0'
    )
    xyus_md5_str = hashlib.md5(xyus.encode('ascii')).hexdigest()
    current_ts = str(int(time.time()))

    params = {"module_section": [{'zid': xyus}]}

    req_body = pack_json(params)
    req_body = gzip.compress(req_body.encode('utf-8'), compresslevel=6, mtime=0)

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_req_body = padder.update(req_body) + padder.finalize()
    aes_encryptor = http_core.account.aes_cbc_chiper.encryptor()
    req_body_aes = aes_encryptor.update(padded_req_body) + aes_encryptor.finalize()

    req_body_md5 = hashlib.md5(req_body).digest()

    payload = aiohttp.payload.BytesPayload(
        req_body_aes + req_body_md5,
        content_type="application/x-www-form-urlencoded",
    )

    headers = {
        "x-device-id": xyus_md5_str,
        "User-Agent": f'x6/{app_key}/{MAIN_VERSION}/4.4.1.3',
        "x-plu-ver": 'x6/4.4.1.3',
    }

    path_combine = ''.join((app_key, current_ts, sec_key))
    path_combine_md5 = hashlib.md5(path_combine.encode('ascii')).hexdigest()
    req_query_skey = rc4_42(xyus_md5_str, http_core.account.aes_cbc_sec_key)
    req_query_skey = binascii.b2a_base64(req_query_skey).decode('ascii')
    url = yarl.URL.build(
        scheme="https",
        host=SOFIRE_HOST,
        path=f"/c/11/z/100/{app_key}/{current_ts}/{path_combine_md5}",
        query=[('skey', req_query_skey)],
    )

    request = aiohttp.ClientRequest(
        aiohttp.hdrs.METH_POST,
        url,
        headers=headers,
        data=payload,
        loop=http_core.loop,
        proxy=http_core.net_core.proxy.url,
        proxy_auth=http_core.net_core.proxy.auth,
        ssl=False,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=1024)
    res_json = parse_json(body)

    res_query_skey = binascii.a2b_base64(res_json['skey'])
    res_aes_sec_key = rc4_42(xyus_md5_str, res_query_skey)
    res_data = binascii.a2b_base64(res_json['data'])

    iv = b'\x00' * 16
    aes_chiper = Cipher(algorithms.AES(res_aes_sec_key), modes.CBC(iv))
    aes_decryptor = aes_chiper.decryptor()
    decrypted_res_data = aes_decryptor.update(res_data) + aes_decryptor.finalize()
    decrypted_res_data = decrypted_res_data[:-16]  # remove suffix md5
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = unpadder.update(decrypted_res_data) + unpadder.finalize()

    res_data = unpadded_data.decode('utf-8')
    res_data = parse_json(res_data)
    zid = res_data['token']

    return zid
