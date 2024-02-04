import enum


class Gender(enum.IntEnum):
    """
    用户性别

    Note:
        UNKNOWN 未知\n
        MALE 男性\n
        FEMALE 女性
    """

    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


class PrivLike(enum.IntEnum):
    """
    关注吧列表的公开状态

    Note:
        PUBLIC 所有人可见\n
        FRIEND 好友可见\n
        HIDE 完全隐藏
    """

    PUBLIC = 1
    FRIEND = 2
    HIDE = 3


class PrivReply(enum.IntEnum):
    """
    帖子评论权限

    Note:
        ALL 允许所有人\n
        FANS 仅允许我的粉丝\n
        FOLLOW 仅允许我的关注
    """

    ALL = 1
    FANS = 5
    FOLLOW = 6


class ReqUInfo(enum.IntEnum):
    """
    使用该枚举类指定待获取的用户信息字段

    Note:
        各bit位的含义由高到低分别为 OTHER, TIEBA_UID, NICK_NAME, USER_NAME, PORTRAIT, USER_ID\n
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
        对于有热门分区的贴吧 0热门排序(HOT) 1按发布时间(CREATE) 2关注的人(FOLLOW) 34热门排序(HOT) >=5是按回复时间(REPLY)\n
        对于无热门分区的贴吧 0按回复时间(REPLY) 1按发布时间(CREATE) 2关注的人(FOLLOW) >=3按回复时间(REPLY)
    """

    REPLY = 5
    CREATE = 1
    HOT = 3
    FOLLOW = 2


class PostSortType(enum.IntEnum):
    """
    回复排序

    Note:
        ASC 时间顺序\n
        DESC 时间倒序\n
        HOT 热门序
    """

    ASC = 0
    DESC = 1
    HOT = 2


class BawuSearchType(enum.IntEnum):
    """
    吧务后台搜索类型

    Note:
        USER 搜索用户\n
        OP 搜索操作者
    """

    USER = 0
    OP = 1


class BlacklistType(enum.IntEnum):
    """
    用户黑名单类型

    Note:
        NULL 正常状态\n
        FOLLOW 禁止关注\n
        INTERACT 禁止互动\n
        CHAT 禁止私信\n
        ALL 全屏蔽
    """

    NULL = 0
    FOLLOW = 1 << 0
    INTERACT = 1 << 1
    CHAT = 1 << 2
    FOLLOW_AND_INTERACT = FOLLOW | INTERACT
    FOLLOW_AND_CHAT = FOLLOW | CHAT
    INTERACT_AND_CHAT = INTERACT | CHAT
    ALL = FOLLOW | INTERACT | CHAT


class WsStatus(enum.IntEnum):
    """
    回复排序

    Note:
        CLOSED 已关闭\n
        CONNECTING 正在连接\n
        OPEN 可用
    """

    CLOSED = 0
    CONNECTING = 1
    OPEN = 2


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
