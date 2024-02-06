import dataclasses as dcs

from .common import TypeMessage


@dcs.dataclass
class VirtualImage:
    """
    虚拟形象信息

    Attributes:
        enabled (bool): 是否启用虚拟形象
        state (str): 虚拟形象状态签名
    """

    enabled: bool = False
    state: str = ""

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "VirtualImage":
        enabled = bool(data_proto.custom_figure.background_value)
        state = data_proto.custom_state.content
        return VirtualImage(enabled, state)

    def __str__(self) -> str:
        return self.state

    def __bool__(self) -> bool:
        return self.enabled
