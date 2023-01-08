from typing import List

from .common import TypeMessage


class VoteOption(object):
    """
    投票选项信息

    Attributes:
        vote_num (int): 得票数
        text (str): 选项描述文字
    """

    __slots__ = [
        '_vote_num',
        '_text',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._vote_num = data_proto.num
        self._text = data_proto.text

    @property
    def vote_num(self) -> int:
        """
        得票数
        """

        return self._vote_num

    @property
    def text(self) -> str:
        """
        选项文字
        """

        return self._text


class VoteInfo(object):
    """
    投票信息

    Attributes:
        title (str): 投票标题
        is_multi (bool): 是否多选
        options (list[VoteOption]): 选项列表
        total_vote (int): 总投票数
        total_user (int): 总投票人数
    """

    __slots__ = [
        '_title',
        '_is_multi',
        '_options',
        '_total_vote',
        '_total_user',
    ]

    def _init(self, data_proto: TypeMessage) -> "VoteInfo":
        self._title = data_proto.title
        self._is_multi = bool(data_proto.is_multi)
        self._options = [VoteOption(p) for p in data_proto.options]
        self._total_vote = data_proto.total_poll
        self._total_user = data_proto.total_num
        return self

    def _init_null(self) -> "VoteInfo":
        self._title = ''
        self._is_multi = False
        self._options = []
        self._total_vote = 0
        self._total_user = 0
        return self

    def __len__(self) -> int:
        return self.options.__len__()

    def __bool__(self) -> bool:
        return bool(self.options)

    @property
    def title(self) -> str:
        """
        投票标题
        """

        return self._title

    @property
    def is_multi(self) -> bool:
        """
        是否多选
        """

        return self._is_multi

    @property
    def options(self) -> List[VoteOption]:
        """
        选项列表
        """

        return self._options

    @property
    def total_vote(self) -> int:
        """
        总投票数
        """

        return self._total_vote

    @property
    def total_user(self) -> int:
        """
        总投票人数
        """

        return self._total_user
