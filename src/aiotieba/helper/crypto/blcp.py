from __future__ import annotations

import base64
import random
import time
from sys import maxsize as LONG_MAX

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_AES_KEY = b"AFD311832EDEEAEF"
_AES_IV = b"2011121211143000"


def user_id2bduk(user_id: int) -> str:
    """
    将user_id加密为群聊报文中的baidu_uk

    Args:
        user_id (int): 用户的user_id

    Returns:
        str: baidu_uk
    """

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(str(user_id).encode()) + padder.finalize()

    encryptor = Cipher(algorithms.AES(_AES_KEY), modes.CBC(_AES_IV)).encryptor()
    encrypted = encryptor.update(padded) + encryptor.finalize()

    bduk = base64.urlsafe_b64encode(encrypted).strip(b"=").decode()
    return bduk


def bduk2user_id(bduk: str) -> int:
    """
    将群聊报文中的baidu_uk解密为user_id

    Args:
        bduk (str): baidu_uk

    Returns:
        int: 用户的user_id
    """

    encrypted = base64.urlsafe_b64decode(bduk + "=" * (-len(bduk) % 4))

    decryptor = Cipher(algorithms.AES(_AES_KEY), modes.CBC(_AES_IV)).decryptor()
    padded = decryptor.update(encrypted) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded) + unpadder.finalize()

    user_id = int(data.decode())
    return user_id


def compute_msg_key(bduk: str) -> str:
    """
    计算群聊消息的去重键

    Args:
        bduk (str): baidu_uk

    Returns:
        str: msg_key
    """

    timestamp = int(time.time() * 1000) * 1000
    randint = random.randint(-LONG_MAX, LONG_MAX)

    msg_key = bduk + str(timestamp) + str(randint)
    return msg_key
