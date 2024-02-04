import dataclasses as dcs

from ...exception import TbErrorPlugin


@dcs.dataclass
class Fname(TbErrorPlugin):
    """
    吧名

    Attributes:
        err (Exception | None): 捕获的异常

        fname (str): 吧名
    """

    fname: str = ''

    def __str__(self) -> str:
        return self.fname
