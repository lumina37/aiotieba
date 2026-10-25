from __future__ import annotations

from collections import OrderedDict
from typing import ClassVar


class ForumInfoCache:
    """
    吧信息缓存
    """

    _maxsize: ClassVar[int] = 128
    _fname2fid: ClassVar[OrderedDict[str, int]] = OrderedDict()

    @classmethod
    def get_fid(cls, fname: str) -> int:
        """
        通过贴吧名获取forum_id

        Args:
            fname (str): 贴吧名

        Returns:
            int: 该贴吧的forum_id
        """

        if (fid := cls._fname2fid.get(fname)) is None:
            return 0

        cls._fname2fid.move_to_end(fname)

        return fid

    @classmethod
    def get_fname(cls, fid: int) -> str:
        """
        通过forum_id获取贴吧名

        Args:
            fid (int): forum_id

        Returns:
            str: 该贴吧的贴吧名
        """

        for fname, cached_fid in reversed(cls._fname2fid.items()):
            if cached_fid == fid:
                cls._fname2fid.move_to_end(fname)
                return fname

        return ""

    @classmethod
    def add_forum(cls, fname: str, fid: int) -> None:
        """
        将贴吧名与forum_id的映射关系添加到缓存

        Args:
            fname (str): 贴吧名
            fid (int): 贴吧id
        """

        if fname in cls._fname2fid:
            cls._fname2fid.move_to_end(fname)
        elif len(cls._fname2fid) >= cls._maxsize:
            cls._fname2fid.popitem(last=False)

        cls._fname2fid[fname] = fid
