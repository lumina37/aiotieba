import gzip
from typing import Tuple

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from ..core import Account


def pack_ws_bytes(
    account: Account, data: bytes, cmd: int, req_id: int, *, compress: bool = False, encrypt: bool = True
) -> bytes:
    """
    打包数据并添加9字节头部

    Args:
        account (Account): 贴吧的用户信息容器
        data (bytes): 待发送的websocket数据
        cmd (int): 请求的cmd类型
        req_id (int): 请求的id
        compress (bool, optional): 是否需要gzip压缩. Defaults to False.
        encrypt (bool, optional): 是否需要aes加密. Defaults to True.

    Returns:
        bytes: 打包后的websocket数据
    """

    flag = 0x08

    if compress:
        flag |= 0b01000000
        data = gzip.compress(data, compresslevel=-1, mtime=0)
    if encrypt:
        flag |= 0b10000000
        data = pad(data, AES.block_size)
        data = account.aes_ecb_chiper.encrypt(data)

    data = b''.join(
        [
            flag.to_bytes(1, 'big'),
            cmd.to_bytes(4, 'big'),
            req_id.to_bytes(4, 'big'),
            data,
        ]
    )

    return data


def parse_ws_bytes(account: Account, data: bytes) -> Tuple[bytes, int, int]:
    """
    对websocket返回数据进行解包

    Args:
        account (Account): 贴吧的用户信息容器
        data (bytes): 接收到的websocket数据

    Returns:
        bytes: 解包后的websocket数据
        int: 对应请求的cmd类型
        int: 对应请求的id
    """

    data_view = memoryview(data)
    flag = data_view[0]
    cmd = int.from_bytes(data_view[1:5], 'big')
    req_id = int.from_bytes(data_view[5:9], 'big')

    data = data_view[9:].tobytes()
    if flag & 0b10000000:
        data = account.aes_ecb_chiper.decrypt(data)
        data = unpad(data, AES.block_size)
    if flag & 0b01000000:
        data = gzip.decompress(data)

    return data, cmd, req_id
