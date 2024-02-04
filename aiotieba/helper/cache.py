from collections import OrderedDict


class ForumInfoCache:
    """
    吧信息缓存
    """

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
