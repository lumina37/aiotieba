import binascii
import gzip
import hashlib
import time

import aiohttp
import yarl
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from ...core import HttpCore
from ...helper import pack_json, parse_json
from ...helper.crypto import rc4_42
from ...request import send_request

SOFIRE_HOST = "sofire.baidu.com"


async def request(http_core: HttpCore):
    app_key = '740017'  # get by p/5/aio
    sec_key = '7aaf37cac7c3aaac3456b22832aabd56'
    xyus = (
        hashlib.md5((http_core.account.android_id + http_core.account.uuid).encode('ascii')).hexdigest().upper() + '|0'
    )
    xyus_md5_str = hashlib.md5(xyus.encode('ascii')).hexdigest()
    curr_time = str(int(time.time()))

    params = {"module_section": [{'zid': xyus}]}

    req_body = pack_json(params)
    req_body = gzip.compress(req_body.encode('utf-8'), compresslevel=-1, mtime=0)
    req_body_aes = http_core.account.aes_cbc_chiper.encrypt(pad(req_body, block_size=AES.block_size))
    req_body_md5 = hashlib.md5(req_body).digest()

    payload = aiohttp.payload.BytesPayload(
        req_body_aes + req_body_md5,
        content_type="application/x-www-form-urlencoded",
    )

    headers = {
        "x-device-id": xyus_md5_str,
        "User-Agent": 'x6/740017//4.3.0',
        "x-plu-ver": 'x6/4.3.0',
    }

    path_combine = ''.join((app_key, curr_time, sec_key))
    path_combine_md5 = hashlib.md5(path_combine.encode('ascii')).hexdigest()
    req_query_skey = rc4_42(xyus_md5_str, http_core.account.aes_cbc_sec_key)
    req_query_skey = binascii.b2a_base64(req_query_skey).decode('ascii').replace('+', '%2B')
    url = yarl.URL.build(
        scheme="https",
        host=SOFIRE_HOST,
        path=f"/c/11/z/100/{app_key}/{curr_time}/{path_combine_md5}",
        query_string=f'skey={req_query_skey}',
    )

    request = aiohttp.ClientRequest(
        aiohttp.hdrs.METH_POST,
        url,
        headers=headers,
        data=payload,
        loop=http_core.loop,
        proxy=http_core.network.proxy,
        proxy_auth=http_core.network.proxy,
        ssl=False,
    )

    body = await send_request(request, http_core.network, read_bufsize=1024)
    res_json = parse_json(body)

    res_query_skey = binascii.a2b_base64(res_json['skey'])
    res_aes_sec_key = rc4_42(xyus_md5_str, res_query_skey)
    aes_chiper = AES.new(res_aes_sec_key, AES.MODE_CBC, iv=b'\x00' * 16)
    res_data = binascii.a2b_base64(res_json['data'])
    res_data = unpad(aes_chiper.decrypt(res_data)[:-16], AES.block_size)  # [:-16] remove md5
    res_data = res_data.decode('utf-8')
    del res_json  # enable reuse of json parser
    res_data = parse_json(res_data)
    zid = res_data['token']

    return zid
