from .common import TypeMessage


class VirtualImage(object):
    """
    虚拟形象信息

    Attributes:
        enabled (bool): 是否启用虚拟形象
        state (str): 虚拟形象状态签名
    """

    __slots__ = [
        '_enabled',
        '_state',
    ]

    def _init(self, data_proto: TypeMessage) -> "VirtualImage":
        self._enabled = bool(data_proto.custom_figure.background_value)
        self._state = data_proto.custom_state.content
        return self

    def _init_null(self) -> "VirtualImage":
        self._enabled = False
        self._state = ''
        return self

    def __str__(self) -> str:
        return self._state

    def __repr__(self) -> str:
        return str(
            {
                'enabled': self.enabled,
                'state': self.state,
            }
        )

    def __bool__(self) -> bool:
        return self._enabled

    @property
    def enabled(self) -> bool:
        """
        是否启用虚拟形象
        """

        return self._enabled

    @property
    def state(self) -> str:
        """
        虚拟形象状态签名
        """

        return self._state
