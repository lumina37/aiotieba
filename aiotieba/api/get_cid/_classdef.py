import dataclasses as dcs

from ...exception import TbErrorExt


@dcs.dataclass
class Cid(TbErrorExt):
    """
    精华分区id

    Attributes:
        err (Exception | None): 捕获的异常

        cid (int): 精华分区id
    """

    cid: int = 0

    def __int__(self) -> int:
        return self.cid
