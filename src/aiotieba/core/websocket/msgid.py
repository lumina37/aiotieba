from __future__ import annotations

import dataclasses as dcs


@dcs.dataclass
class MsgIDPair:
    """
    长度为2的msg_id队列 记录新旧msg_id
    """

    last_id: int = 0
    curr_id: int = 0

    def update_msg_id(self, curr_id: int) -> None:
        """
        更新msg_id

        Args:
            curr_id (int): 当前消息的msg_id
        """

        self.last_id = self.curr_id
        self.curr_id = curr_id


@dcs.dataclass
class PrivChatCursors:
    """
    与某个用户的私信会话游标

    Attributes:
        local_msg_id (int): 本端最后一次发送使用的local_msg_id 由服务端回显
        pulled_msg_id (int): 已拉取到的最新msg_id
        sent_msg_id (int): 最近一次上报的已读位置msg_id
        read_msg_id (int): 对方已读到的最新msg_id
    """

    local_msg_id: int = 0
    pulled_msg_id: int = 0
    sent_msg_id: int = 0
    read_msg_id: int = 0


@dcs.dataclass
class MsgIDManager:
    """
    msg_id管理器
    """

    priv_gid: int = 0
    gid2mid: dict[int, MsgIDPair] = dcs.field(default_factory=lambda: {0: MsgIDPair()})
    uid2cursors: dict[int, PrivChatCursors] = dcs.field(default_factory=dict)

    def update_msg_id(self, group_id: int, msg_id: int) -> None:
        """
        更新group_id对应的msg_id

        Args:
            group_id (int): 消息组id
            msg_id (int): 当前消息的msg_id
        """

        mid_pair = self.gid2mid.get(group_id, None)
        if mid_pair is not None:
            mid_pair.update_msg_id(msg_id)
        else:
            self.gid2mid[group_id] = MsgIDPair(msg_id, msg_id)

    def get_msg_id(self, group_id: int) -> int:
        """
        获取group_id对应的msg_id

        Args:
            group_id (int): 消息组id

        Returns:
            int: 上一条消息的msg_id
        """

        return self.gid2mid[group_id].last_id

    def get_cursors(self, user_id: int) -> PrivChatCursors:
        """
        获取与某个用户的私信会话游标 不存在时创建

        Args:
            user_id (int): 用户的user_id

        Returns:
            PrivChatCursors: 私信会话游标
        """

        cursors = self.uid2cursors.get(user_id, None)
        if cursors is None:
            cursors = PrivChatCursors()
            self.uid2cursors[user_id] = cursors

        return cursors

    def get_local_msg_id(self, user_id: int) -> int:
        """
        获取下一条私信的local_msg_id

        Args:
            user_id (int): 接收方的user_id

        Returns:
            int: local_msg_id
        """

        cursors = self.get_cursors(user_id)
        base = max(cursors.local_msg_id, cursors.pulled_msg_id * 100)

        return base + 1

    def update_local_msg_id(self, user_id: int, local_msg_id: int) -> None:
        """
        更新最近一次发送使用的local_msg_id

        Args:
            user_id (int): 接收方的user_id
            local_msg_id (int): 发送时使用的local_msg_id
        """

        cursors = self.get_cursors(user_id)
        if local_msg_id > cursors.local_msg_id:
            cursors.local_msg_id = local_msg_id

    def update_pulled_msg_id(self, user_id: int, msg_id: int) -> None:
        """
        更新已拉取到的最新msg_id

        Args:
            user_id (int): 对端的user_id
            msg_id (int): 拉取到的msg_id
        """

        cursors = self.get_cursors(user_id)
        if msg_id > cursors.pulled_msg_id:
            cursors.pulled_msg_id = msg_id

    def update_sent_msg_id(self, user_id: int, msg_id: int) -> None:
        """
        更新最近一次上报的已读位置msg_id

        Args:
            user_id (int): 对端的user_id
            msg_id (int): 上报的已读位置msg_id
        """

        cursors = self.get_cursors(user_id)
        if msg_id > cursors.sent_msg_id:
            cursors.sent_msg_id = msg_id

    def update_read_msg_id(self, user_id: int, msg_id: int) -> None:
        """
        更新对方已读到的最新msg_id

        Args:
            user_id (int): 对端的user_id
            msg_id (int): 对方已读位置msg_id
        """

        cursors = self.get_cursors(user_id)
        if msg_id > cursors.read_msg_id:
            cursors.read_msg_id = msg_id
