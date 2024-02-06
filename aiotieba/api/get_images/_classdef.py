import dataclasses as dcs
from typing import TYPE_CHECKING

from ...exception import TbErrorExt

if TYPE_CHECKING:
    import numpy as np


def _null_factory() -> "np.ndarray":
    import numpy as np

    return np.empty(0, dtype=np.uint8)


@dcs.dataclass
class Image(TbErrorExt):
    """
    图像

    Attributes:
        err (Exception | None): 捕获的异常

        img (np.ndarray): 图像
    """

    img: "np.ndarray" = dcs.field(default_factory=_null_factory)


@dcs.dataclass
class ImageBytes(TbErrorExt):
    """
    图像原始字节流

    Attributes:
        err (Exception | None): 捕获的异常

        data (bytes): 图像原始字节流
    """

    data: bytes = b""
