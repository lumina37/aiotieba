from ..._logging import get_logger as LOG


def is_valid_BDUSS(BDUSS: str) -> bool:
    if not BDUSS:
        return False

    legal_length = 192
    if (len_new_BDUSS := len(BDUSS)) != legal_length:
        LOG().warning(f"BDUSS的长度应为{legal_length}个字符 而输入的{BDUSS}有{len_new_BDUSS}个字符")
        return False

    return True


def is_valid_STOKEN(STOKEN: str) -> bool:
    if not STOKEN:
        return False

    legal_length = 64
    if (len_new_STOKEN := len(STOKEN)) != legal_length:
        LOG().warning(f"STOKEN的长度应为{legal_length}个字符 而输入的{STOKEN}有{len_new_STOKEN}个字符")
        return False

    return True
