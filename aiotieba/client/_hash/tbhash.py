from . import _hash


def cuid_galaxy2(android_id: str) -> str:
    """
    使用给定的android_id生成cuid_galaxy2

    Args:
        android_id (str): 长度为16的16进制字符串 包含8字节信息

    Returns:
        str: cuid_galaxy2 长度为42的字符串

    Examples:
        A3ED2D7B9CFC28E8934A3FBD3A9579C7|VZ5FKB5XS

    Note:
        此实现与12.x版本及以前的官方实现一致
    """

    return _hash.cuid_galaxy2((android_id,))


def c3_aid(android_id: str, uuid: str) -> str:
    """
    使用给定的android_id和uuid生成c3_aid

    Args:
        android_id (str): 长度为16的16进制字符串 包含8字节信息
        uuid (str): 包含16字节信息

    Returns:
        str: c3_aid 长度为45的字符串

    Examples:
        A00-ZNU3O3EP74D727LMQY745CZSGZQJQZGP-3JXCKC7X

    Note:
        此实现与12.x版本及以前的官方实现一致
    """

    return _hash.c3_aid((android_id, uuid))
