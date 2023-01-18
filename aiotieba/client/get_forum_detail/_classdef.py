from typing import Mapping


class Forum_detail(object):
    """
    吧基本信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名
        member_num (int): 吧会员数
        post_num (int): 发帖量
    """

    __slots__ = [
        '_fid',
        '_fname',
        '_member_num',
        '_post_num',
    ]

    def _init(self, data_map: Mapping) -> "Forum_detail":
        self._fid = int(data_map['forum_id'])
        self._fname = data_map['forum_name']
        self._member_num = int(data_map['member_count'])
        self._post_num = int(data_map['thread_count'])
        return self

    def _init_null(self) -> "Forum_detail":
        self._fid = 0
        self._fname = ''
        self._member_num = 0
        self._post_num = 0
        return self

    def __repr__(self) -> str:
        return str(
            {
                'fid': self._fid,
                'fname': self._fname,
                'member_num': self._member_num,
                'post_num': self._post_num,
            }
        )

    @property
    def fid(self) -> int:
        """
        贴吧id
        """

        return self._fid

    @property
    def fname(self) -> str:
        """
        贴吧名
        """

        return self._fname

    @property
    def member_num(self) -> int:
        """
        吧会员数
        """

        return self._member_num

    @property
    def post_num(self) -> str:
        """
        发帖量
        """

        return self._post_num
