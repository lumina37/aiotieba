import dataclasses as dcs

from ...exception import TbErrorExt


@dcs.dataclass
class Fid(TbErrorExt):
    """
    forum_id

    Attributes:
        err (Exception | None): 捕获的异常

        fid (int): forum_id
    """

    fid: int = 0

    def __int__(self) -> int:
        return self.fid
