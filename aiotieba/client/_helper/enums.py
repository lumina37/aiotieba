import enum


class GroupType(enum.IntEnum):
    """
    消息组类型
    """

    PRIVATE_MSG = 6
    MISC = 8


class MsgType(enum.IntEnum):
    """
    消息类型
    """

    PRIVATE_MSG = 1
    MISC = 10
    READED = 22


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


class ThreadSortType(enum.IntEnum):
    """
    主题帖排序

    Note:
        对于有热门分区的贴吧 0热门排序 1按发布时间 2关注的人 34热门排序 >=5是按回复时间
        对于无热门分区的贴吧 0按回复时间 1按发布时间 2关注的人 >=3按回复时间
    """

    REPLY = 5
    CREATE = 1
    HOT = 3
    FOLLOW = 2


class PostSortType(enum.IntEnum):
    """
    回复排序

    Note:
        0时间顺序 1时间倒序 2热门序
    """

    ASC = 0
    DESC = 1
    HOT = 2


class WsStatus(enum.IntEnum):
    """
    回复排序

    Note:
        0已关闭 1正在连接 2可用
    """

    CLOSED = 0
    CONNECTING = 1
    OPEN = 2
