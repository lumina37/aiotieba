import enum


class ReqUInfo(enum.IntEnum):
    """
    使用该枚举类指定待获取的用户信息字段

    Note:
        各bit位的含义由高到低分别为
        OTHER, TIEBA_UID, NICK_NAME, USER_NAME, PORTRAIT, USER_ID
        其中BASIC = USER_ID | PORTRAIT | USER_NAME
    """

    USER_ID = 1 << 0
    PORTRAIT = 1 << 1
    USER_NAME = 1 << 2
    NICK_NAME = 1 << 3
    TIEBA_UID = 1 << 4
    OTHER = 1 << 5
    BASIC = USER_ID | PORTRAIT | USER_NAME
    ALL = (1 << 6) - 1


class Header(object):
    ACCEPT_ENCODING = "Accept-Encoding"
    BAIDU_DATA_TYPE = "x_bd_data_type"
    CACHE_CONTROL = "Cache-Control"
    CONNECTION = "Connection"
    HOST = "Host"
    KEEP_ALIVE = "Keep-Alive"
    SEC_WEBSOCKET_EXTENSIONS = "Sec-WebSocket-Extensions"
    USER_AGENT = "User-Agent"
