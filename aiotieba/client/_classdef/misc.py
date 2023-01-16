import asyncio
import time
import weakref
from collections import OrderedDict


class WebsocketResponse(object):
    """
    websocket响应

    Attributes:
        timestamp (int): 请求时间戳
        req_id (int): 唯一的请求id
    """

    __slots__ = [
        '__weakref__',
        '__dict__',
        '_timestamp',
        '_req_id',
        '_data_future',
    ]

    ws_res_wait_dict = weakref.WeakValueDictionary()
    _websocket_request_id: int = None

    def __init__(self) -> None:
        self._timestamp: int = int(time.time())
        self._req_id = None
        self._data_future: asyncio.Future = asyncio.Future()

        self.ws_res_wait_dict[self.req_id] = self

    def __hash__(self) -> int:
        return self.req_id

    def __eq__(self, obj: "WebsocketResponse") -> bool:
        return self.req_id == obj.req_id

    @property
    def timestamp(self) -> int:
        """
        请求时间戳

        Note:
            13位时间戳 以毫秒为单位
        """

        return self._timestamp

    @property
    def req_id(self) -> int:
        """
        返回一个唯一的请求id
        在初次生成后该属性便不会再发生变化
        """

        if self._req_id is None:

            if self._websocket_request_id is None:
                self._websocket_request_id = self._timestamp
            self._websocket_request_id += 1
            self._req_id = self._websocket_request_id

        return self._req_id


class ForumInfoCache(object):
    """
    吧信息缓存
    """

    __slots__ = []

    _fname2fid = OrderedDict()
    _fid2fname = OrderedDict()

    @classmethod
    def get_fid(cls, fname: str) -> int:
        """
        通过贴吧名获取forum_id

        Args:
            fname (str): 贴吧名

        Returns:
            int: 该贴吧的forum_id
        """

        return cls._fname2fid.get(fname, '')

    @classmethod
    def get_fname(cls, fid: int) -> str:
        """
        通过forum_id获取贴吧名

        Args:
            fid (int): forum_id

        Returns:
            str: 该贴吧的贴吧名
        """

        return cls._fid2fname.get(fid, '')

    @classmethod
    def add_forum(cls, fname: str, fid: int) -> None:
        """
        将贴吧名与forum_id的映射关系添加到缓存

        Args:
            fname (str): 贴吧名
            fid (int): 贴吧id
        """

        if len(cls._fname2fid) == 128:
            cls._fname2fid.popitem(last=False)
            cls._fid2fname.popitem(last=False)

        cls._fname2fid[fname] = fid
        cls._fid2fname[fid] = fname
