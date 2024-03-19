import enum
import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from strenum import StrEnum


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


class ReqUInfo(enum.Flag):
    """
    使用该枚举类指定待获取的用户信息字段

    Note:
        各bit位的含义由高到低分别为 OTHER, TIEBA_UID, NICK_NAME, USER_NAME, PORTRAIT, USER_ID\n
        其中BASIC = USER_ID | PORTRAIT | USER_NAME
    """

    USER_ID = enum.auto()
    PORTRAIT = enum.auto()
    USER_NAME = enum.auto()
    NICK_NAME = enum.auto()
    TIEBA_UID = enum.auto()
    OTHER = enum.auto()
    BASIC = USER_ID | PORTRAIT | USER_NAME
    ALL = BASIC | NICK_NAME | TIEBA_UID | OTHER


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


class SearchType(enum.IntEnum):
    """
    搜索类型

    Note:
        ALL 搜索全部\n
        TIME app时间倒序\n
        RELATION app相关性排序
    """

    ALL = 0
    TIME = 1
    RELATION = 2


class BawuType(StrEnum):
    """
    吧务类型

    Note:
        MANAGER 小吧\n
        IMAGE_EDITOR 图片小编\n
        VOICE_EDITOR 语音小编
    """

    MANAGER = 'assist'
    IMAGE_EDITOR = 'picadmin'
    VOICE_EDITOR = 'voiceadmin'


class BawuPermType(enum.Flag):
    """
    吧务已分配的权限

    Note:
        NULL 无权限\n
        UNBLOCK 解除封禁\n
        UNBLOCK_APPEAL 封禁申诉处理\n
        RECOVER 恢复删帖\n
        RECOVER_APPEAL 删帖申诉处理\n
        ALL 所有权限
    """

    NULL = 0
    UNBLOCK = enum.auto()
    UNBLOCK_APPEAL = enum.auto()
    RECOVER = enum.auto()
    RECOVER_APPEAL = enum.auto()
    ALL = UNBLOCK | UNBLOCK_APPEAL | RECOVER | RECOVER_APPEAL


class RankForumType(enum.IntEnum):
    """
    吧签到排行榜类别

    Note:
        TODAY 今日排行\n
        YESTERDAY 昨日排行\n
        WEEKLY 周排行\n
        MONTHLY 月排行
    """

    TODAY = 0
    YESTERDAY = 1
    WEEKLY = 2
    MONTHLY = 3


class BlacklistType(enum.Flag):
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
    FOLLOW = enum.auto()
    INTERACT = enum.auto()
    CHAT = enum.auto()
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
    CONNECTING = enum.auto()
    OPEN = enum.auto()


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
