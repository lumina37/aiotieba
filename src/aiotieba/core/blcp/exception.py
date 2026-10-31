from __future__ import annotations


class BlcpError(Exception):
    """
    BLCP协议异常基类
    """


class BlcpProtocolError(BlcpError):
    """
    报文格式非法
    """


class BlcpLoginError(BlcpError):
    """
    BLCP登录失败
    """


class BlcpConnectionError(BlcpError, ConnectionError):
    """
    BLCP连接异常
    """
