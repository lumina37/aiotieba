from __future__ import annotations


class BLCPError(Exception):
    """
    BLCP协议异常基类
    """


class BLCPProtocolError(BLCPError):
    """
    报文格式非法
    """


class BLCPLoginError(BLCPError):
    """
    BLCP登录失败
    """


class BLCPConnectionError(BLCPError, ConnectionError):
    """
    BLCP连接异常
    """
