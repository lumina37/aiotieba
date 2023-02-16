from .common import TypeMessage


class Forum(object):
    """
    吧基本信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名
    """

    __slots__ = [
        '_fid',
        '_fname',
    ]

    def _init(self, data_proto: TypeMessage) -> "Forum":
        self._fid = data_proto.id
        self._fname = data_proto.name
        return self

    def _init_null(self) -> "Forum":
        self._fid = 0
        self._fname = ''
        return self

    def __repr__(self) -> str:
        return str(
            {
                'fid': self._fid,
                'fname': self._fname,
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
