import dataclasses as dcs
from typing import List

from .common import TypeMessage


@dcs.dataclass
class VoteOption:
    """
    投票选项信息

    Attributes:
        vote_num (int): 得票数
        text (str): 选项描述文字
    """

    vote_num: int = 0
    text: str = ""

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "VoteOption":
        vote_num = data_proto.num
        text = data_proto.text
        return VoteOption(vote_num, text)


@dcs.dataclass
class VoteInfo:
    """
    投票信息

    Attributes:
        title (str): 投票标题
        is_multi (bool): 是否多选
        options (list[VoteOption]): 选项列表
        total_vote (int): 总投票数
        total_user (int): 总投票人数
    """

    title: str = ""
    is_multi: bool = False
    options: List[VoteOption] = dcs.field(default_factory=list)
    total_vote: int = 0
    total_user: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "VoteInfo":
        title = data_proto.title
        is_multi = bool(data_proto.is_multi)
        options = [VoteOption.from_tbdata(p) for p in data_proto.options]
        total_vote = data_proto.total_poll
        total_user = data_proto.total_num
        return VoteInfo(title, is_multi, options, total_vote, total_user)

    def __len__(self) -> int:
        return len(self.options)

    def __bool__(self) -> bool:
        return bool(self.options)
