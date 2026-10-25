from __future__ import annotations

import gzip
from typing import TYPE_CHECKING

from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

if TYPE_CHECKING:
    from ..account import Account


def _create_ws_chiper(account: Account) -> Cipher[modes.ECB]:
    """
    构造供websocket使用的AES-ECB加密器

    Args:
        account (Account): 贴吧的用户参数容器

    Returns:
        Cipher[modes.ECB]: AES-ECB加密器
    """

    kdf = PBKDF2HMAC(hashes.SHA1(), 32, b"\xa4\x0b\xc8\x34\xd6\x95\xf3\x13", 5)
    ws_secret_key = kdf.derive(account.ws_sec_key)
    return Cipher(algorithms.AES(ws_secret_key), modes.ECB())


def pack_ws_bytes(
    account: Account, data: bytes, cmd: int, req_id: int, *, compress: bool = False, encrypt: bool = True
) -> bytes:
    """
    打包数据并添加9字节头部

    Args:
        account (Account): 贴吧的用户参数容器
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
        data = gzip.compress(data, compresslevel=6, mtime=0)
    if encrypt:
        flag |= 0b10000000
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        data = padder.update(data) + padder.finalize()
        ws_chiper = _create_ws_chiper(account)
        encryptor = ws_chiper.encryptor()
        data = encryptor.update(data) + encryptor.finalize()

    data = b"".join([
        flag.to_bytes(1, "big"),
        cmd.to_bytes(4, "big"),
        req_id.to_bytes(4, "big"),
        data,
    ])

    return data


def parse_ws_bytes(account: Account, data: bytes) -> tuple[bytes, int, int]:
    """
    对websocket返回数据进行解包

    Args:
        account (Account): 贴吧的用户参数容器
        data (bytes): 接收到的websocket数据

    Returns:
        tuple[bytes, int, int]: 解包后的websocket数据 依次为数据、cmd类型、请求id
    """

    data_view = memoryview(data)
    flag = data_view[0]
    cmd = int.from_bytes(data_view[1:5], "big")
    req_id = int.from_bytes(data_view[5:9], "big")

    data = data_view[9:].tobytes()
    if flag & 0b10000000:
        ws_chiper = _create_ws_chiper(account)
        decryptor = ws_chiper.decryptor()
        data = decryptor.update(data) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(data) + unpadder.finalize()
    if flag & 0b01000000:
        data = gzip.decompress(data)

    return data, cmd, req_id
