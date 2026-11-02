from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def compute_sign(data: Sequence[tuple[str, str | int]], *, salt: bytes) -> str:
    """
    计算贴吧客户端签名

    Args:
        data (Sequence[tuple[str, str | int]]): 参数元组列表
        salt (bytes): 计算签名使用的盐值

    Returns:
        str: 签名
    """

    md5obj = hashlib.md5()

    for key, val in sorted(data):
        md5obj.update(f"{key}={val}".encode())

    md5obj.update(salt)

    return md5obj.hexdigest()


def sign(data: Sequence[tuple[str, str | int]], *, salt: bytes) -> list[tuple[str, str | int]]:
    """
    为参数元组列表添加贴吧客户端签名

    Args:
        data (Sequence[tuple[str, str | int]]): 参数元组列表
        salt (bytes): 计算签名使用的盐值

    Returns:
        list[tuple[str, str | int]]: 签名后的form参数元组列表
    """

    signed_data = [*data, ("sign", compute_sign(data, salt=salt))]
    return signed_data
