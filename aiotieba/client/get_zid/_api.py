import binascii
import gzip
import hashlib
import json
import random
import time

import aiohttp
import yarl
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from .._core import TbCore
from .._exception import TiebaServerError, TiebaValueError
from .._hash import swap_hash
from .._helper import jsonlib, log_exception, parse_json, send_request

SOFIRE_HOST = "sofire.baidu.com"


async def request_p_5_aio(connector: aiohttp.TCPConnector, core: TbCore):

    app_key = '200033'
    sec_key = 'ea737e4f435b53786043369d2e5ace4f'
    cuid2_md5 = hashlib.md5(core.cuid_galaxy2.encode('ascii')).hexdigest()
    aes_sec_key = random.randbytes(16)

    curr_time = str(int(time.time()))

    params = {
        '1': {
            #'0': 'SM-G988N',
            #'1': core.cuid_galaxy2,
            #'3': '28',
            #'4': '3.3.9.8.2',
            '5': '贴吧极速版',
            '6': 'com.baidu.tieba_mini',
            '7': 'c8630c10b6ea570f10f970497a006a35',
            #'8': '9.1.0.0',
            #'9': '0',
        },
    }

    req_body = jsonlib.dumps(params)
    req_body = gzip.compress(req_body.encode('utf-8'), compresslevel=-1, mtime=0)

    aes_chiper = AES.new(aes_sec_key, AES.MODE_CBC, iv=b'\x00' * 16)
    req_body_aes = aes_chiper.encrypt(pad(req_body, block_size=AES.block_size))
    req_body_md5 = hashlib.md5(req_body).digest()

    payload = aiohttp.payload.BytesPayload(
        req_body_aes + req_body_md5,
        content_type="application/x-www-form-urlencoded",
    )

    headers = {
        "User-Agent": f'eos/{app_key}/9.1.0.0/3.3.9.8.2',
        "Pragma": 'no-cache',
        "Accept": '*/*',
        "Content-Type": 'application/x-www-form-urlencoded',
        "Accept-Encoding": 'gzip,deflate',
        "Accept-Language": 'zh-CN',
        "x-device-id": cuid2_md5,
        "Host": 'sofire.baidu.com',
        "Connection": 'Keep-Alive',
    }

    path_combine = ''.join((app_key, curr_time, sec_key))
    path_combine_md5 = hashlib.md5(path_combine.encode('ascii')).hexdigest()
    # swaphash is rc4
    query_skey = binascii.b2a_base64(swap_hash(aes_sec_key, cuid2_md5.encode('ascii'))).decode('ascii')
    url = yarl.URL.build(
        scheme="https",
        host=SOFIRE_HOST,
        path=f"/p/5/aio/100/{app_key}/{curr_time}/{path_combine_md5}",
        query={'skey': query_skey},
    )

    request = aiohttp.ClientRequest(
        aiohttp.hdrs.METH_POST,
        url,
        headers=headers,
        data=payload,
        loop=core._loop,
        proxy=core._proxy,
        proxy_auth=core._proxy_auth,
        ssl=False,
    )

    body = await send_request(request, connector, read_bufsize=32 * 1024)

    res_json = json.loads(body)

    query_skey = binascii.a2b_base64(res_json['skey'])
    aes_sec_key = swap_hash(query_skey, cuid2_md5.encode('ascii'))
    aes_chiper = AES.new(aes_sec_key, AES.MODE_CBC, iv=b'\x00' * 16)
    res_data = binascii.a2b_base64(res_json['response'])
    res_data = unpad(aes_chiper.decrypt(res_data)[:-16], AES.block_size)
    res_data = json.loads(res_data.decode('utf-8'))

    app_key = int(res_data['2']['0'])
    sec_key = res_data['2']['1']


