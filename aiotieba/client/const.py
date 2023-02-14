from typing import Optional

import aiohttp

APP_SECURE_SCHEME = "https"
APP_INSECURE_SCHEME = "http"

APP_BASE_HOST = "tiebac.baidu.com"
WEB_BASE_HOST = "tieba.baidu.com"

CHECK_URL_PERFIX = "http://tieba.baidu.com/mo/q/checkurl?url="


class TimeConfig(object):
    """
    各种时间设置

    Note:
        所有时间均以秒为单位
    """

    __slots__ = [
        '_http',
        '_http_keepalive',
        '_ws_send',
        '_ws_read',
        '_ws_keepalive',
        '_ws_heartbeat',
        '_dns_ttl',
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
        self._http = aiohttp.ClientTimeout(connect=http_acquire_conn, sock_read=http_read, sock_connect=http_connect)
        self._http_keepalive = http_keepalive
        self._ws_send = ws_send
        self._ws_read = ws_read
        self._ws_keepalive = ws_keepalive
        self._ws_heartbeat = ws_heartbeat
        self._dns_ttl = dns_ttl

    @property
    def http(self) -> aiohttp.ClientTimeout:
        """
        与aiohttp兼容的超时设置
        """

        return self._http

    @property
    def http_acquire_conn(self) -> float:
        """
        从连接池获取一个可用连接的超时时间
        """

        return self._http.connect

    @http_acquire_conn.setter
    def http_acquire_conn(self, new_val: float) -> None:
        self._http.connect = new_val

    @property
    def http_read(self) -> float:
        """
        从发送http请求到读取全部响应的超时时间
        """

        return self._http.sock_read

    @http_read.setter
    def http_read(self, new_val: float) -> None:
        self._http.sock_read = new_val

    @property
    def http_connect(self) -> float:
        """
        新建一个socket连接的超时时间
        """

        return self._http.sock_connect

    @http_connect.setter
    def http_connect(self, new_val: float) -> None:
        self._http.sock_connect = new_val

    @property
    def http_keepalive(self) -> float:
        """
        http长连接的保持时间
        """

        return self._http_keepalive

    @http_keepalive.setter
    def http_keepalive(self, new_val: float) -> None:
        self._http_keepalive = new_val

    @property
    def ws_send(self) -> float:
        """
        websocket发送数据的超时时间
        """

        return self._ws_send

    @ws_send.setter
    def ws_send(self, new_val: float) -> None:
        self._ws_send = new_val

    @property
    def ws_read(self) -> float:
        """
        从发送websocket数据到结束等待响应的超时时间
        """

        return self._ws_read

    @ws_read.setter
    def ws_read(self, new_val: float) -> None:
        self._ws_read = new_val

    @property
    def ws_keepalive(self) -> float:
        """
        websocket在长达ws_keepalive的时间内未发生IO则发送close信号关闭连接
        """

        return self._ws_keepalive

    @ws_keepalive.setter
    def ws_keepalive(self, new_val: float) -> None:
        self._ws_keepalive = new_val

    @property
    def ws_heartbeat(self) -> Optional[float]:
        """
        websocket心跳间隔
        """

        return self._ws_heartbeat

    @ws_heartbeat.setter
    def ws_heartbeat(self, new_val: Optional[float]) -> None:
        self._ws_heartbeat = new_val

    @property
    def dns_ttl(self) -> float:
        """
        dns的本地缓存超时时间
        """

        return self._dns_ttl

    @dns_ttl.setter
    def dns_ttl(self, new_val: float) -> None:
        self._dns_ttl = new_val


TIME_CONFIG = TimeConfig()
