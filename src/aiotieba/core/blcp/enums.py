from __future__ import annotations

import enum


class BLCPServiceID(enum.IntEnum):
    """
    BLCP服务号

    Note:
        LCM 控制面 登录/心跳/登出\n
        IM 会话总线 私信/群组/业务会话/通知\n
        MCAST 多播频道 吧群/聊天室\n
        CLOUD_CONTROL 云控配置下发
    """

    LCM = 1
    IM = 2
    MCAST = 3
    CLOUD_CONTROL = 4


class BLCPMethodID(enum.IntEnum):
    """
    BLCP方法号 需与BLCPServiceID配合使用

    Note:
        LOGIN 登录 LCM登录/云控登录\n
        HEARTBEAT 心跳\n
        LOGIN_BY_TOKEN IM登录\n
        SEND_MCAST_MSG 发送吧群消息\n
        JOIN_CAST 加入吧群
    """

    LOGIN = 1
    HEARTBEAT = 3
    LOGIN_BY_TOKEN = 50
    SEND_MCAST_MSG = 185
    JOIN_CAST = 201


class CompressType(enum.IntEnum):
    """
    报文体压缩类型

    Note:
        NONE 不压缩\n
        GZIP gzip压缩
    """

    NONE = 0
    GZIP = 1

    @classmethod
    def _missing_(cls, value: object) -> CompressType:
        # 未知压缩类型一律按不压缩处理
        return cls.NONE
