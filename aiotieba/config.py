import dataclasses as dcs
from typing import Optional

import aiohttp


@dcs.dataclass
class TimeConfig:
    """
    各种时间设置

    Args:
        http_acquire_conn (float, optional): 从连接池获取一个可用连接的超时时间. Defaults to 4.0.
        http_read (float, optional): 从发送http请求到读取全部响应的超时时间. Defaults to 12.0.
        http_connect (float, optional): 新建一个socket连接的超时时间. Defaults to 3.0.
        http_keepalive (float, optional): http长连接的保持时间. Defaults to 30.0.
        ws_send (float, optional): websocket发送数据的超时时间. Defaults to 3.0.
        ws_read (float, optional): 从发送websocket数据到结束等待响应的超时时间. Defaults to 8.0.
        ws_keepalive (float, optional): websocket在长达ws_keepalive的时间内未发生IO则发送close信号关闭连接. Defaults to 300.0.
        ws_heartbeat (float, optional): websocket心跳间隔. 为None则不发送心跳. Defaults to None.
        dns_ttl (float, optional): dns的本地缓存超时时间. Defaults to 600.0.

    Note:
        所有时间均以秒为单位
    """

    __slots__ = [
        'http',
        'http_keepalive',
        'ws_send',
        'ws_read',
        'ws_keepalive',
        'ws_heartbeat',
        'dns_ttl',
    ]

    def __init__(
        self,
        http_acquire_conn: float = 4.0,
        http_read: float = 12.0,
        http_connect: float = 3.0,
        http_keepalive: float = 30.0,
        ws_send: float = 3.0,
        ws_read: float = 8.0,
        ws_keepalive: float = 300.0,
        ws_heartbeat: Optional[float] = None,
        dns_ttl: float = 600.0,
    ) -> None:
        self.http = aiohttp.ClientTimeout(connect=http_acquire_conn, sock_read=http_read, sock_connect=http_connect)
        self.http_keepalive = http_keepalive
        self.ws_send = ws_send
        self.ws_read = ws_read
        self.ws_keepalive = ws_keepalive
        self.ws_heartbeat = ws_heartbeat
        self.dns_ttl = dns_ttl

    @property
    def http_read(self) -> float:
        return self.http.sock_read

    @property
    def http_connect(self) -> float:
        return self.http.sock_connect
