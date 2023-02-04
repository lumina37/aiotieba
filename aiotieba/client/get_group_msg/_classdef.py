class MsgGroup(object):

    __slots__ = [
        '_group_type',
        '_last_msg_id',
    ]

    def __init__(self, group_type: int, last_msg_id: int) -> None:
        self._group_type = group_type
        self._last_msg_id = last_msg_id

    def __repr__(self) -> str:
        return str(
            {
                'group_type': self._group_type,
                'last_msg_id': self._last_msg_id,
            }
        )

    def group_type(self) -> int:
        """
        消息组类别

        Returns:
            int
        """

        return self._group_type

    def last_msg_id(self) -> int:
        """
        最后一条消息的id

        Returns:
            int
        """

        return self._last_msg_id
