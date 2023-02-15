from .._classdef import TypeMessage


class WsMsgGroupInfo(object):
    """
    websocket消息组的相关信息
    """

    __slots__ = [
        '_group_type',
        '_group_id',
        '_last_msg_id',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._group_type = data_proto.groupType
        self._group_id = data_proto.groupId
        self._last_msg_id = data_proto.lastMsgId

    def __repr__(self) -> str:
        return str(
            {
                'group_type': self._group_type,
                'group_id': self._group_id,
                'last_msg_id': self._last_msg_id,
            }
        )

    @property
    def group_type(self) -> int:
        """
        消息组类别
        """

        return self._group_type

    @property
    def group_id(self) -> int:
        """
        消息组id
        """

        return self._group_id

    @property
    def last_msg_id(self) -> int:
        """
        最后一条消息的id
        """

        return self._last_msg_id
