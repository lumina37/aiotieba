from typing import List

from .._classdef import TypeMessage


class UserInfo_ws(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名

        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_ws":
        self._user_id = data_proto.userId
        if '?' in (portrait := data_proto.portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.userName
        return self

    def _init_null(self) -> "UserInfo_ws":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        return self

    def __str__(self) -> str:
        return self._user_name or self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'user_name': self._user_name,
                'portrait': self._portrait,
            }
        )

    def __eq__(self, obj: "UserInfo_ws") -> bool:
        return self._user_id == obj._user_id

    def __hash__(self) -> int:
        return self._user_id

    def __int__(self) -> int:
        return self._user_id

    def __bool__(self) -> bool:
        return bool(self._user_id)

    @property
    def user_id(self) -> int:
        """
        用户user_id

        Note:
            唯一 不可变 不可为空\n
            请注意与用户个人页的tieba_uid区分
        """

        return self._user_id

    @property
    def portrait(self) -> str:
        """
        用户portrait

        Note:
            唯一 不可变 不可为空
        """

        return self._portrait

    @property
    def user_name(self) -> str:
        """
        用户名

        Note:
            唯一 可变 可为空\n
            请注意与用户昵称区分
        """

        return self._user_name

    @property
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        return self.__str__()


class WsMessage(object):
    """
    websocket消息
    """

    __slots__ = [
        '_msg_id',
        '_msg_type',
        '_text',
        '_user',
        '_create_time',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._msg_id = data_proto.msgId
        self._msg_type = data_proto.msgType
        self._text = data_proto.content
        self._user = UserInfo_ws()._init(data_proto.userInfo)
        self._create_time = data_proto.createTime

    def __repr__(self) -> str:
        return str(
            {
                'text': self._text,
                'user': self._user,
            }
        )

    @property
    def msg_id(self) -> int:
        """
        消息id
        """

        return self._msg_id

    @property
    def msg_type(self) -> int:
        """
        消息类型
        """

        return self._msg_type

    @property
    def text(self) -> str:
        """
        文本内容
        """

        return self._text

    @property
    def user(self) -> UserInfo_ws:
        """
        发信人的用户信息
        """

        return self._user

    @property
    def create_time(self) -> int:
        """
        发送时间

        Note:
            10位时间戳 以秒为单位
        """

        return self._create_time


class WsMsgGroup(object):
    """
    websocket消息组
    """

    __slots__ = [
        '_group_type',
        '_group_id',
        '_messages',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._group_type = data_proto.groupInfo.groupType
        self._group_id = data_proto.groupInfo.groupId
        self._messages = [WsMessage(p) for p in data_proto.msgList]

    def __repr__(self) -> str:
        return str(
            {
                'group_type': self._group_type,
                'group_id': self._group_id,
                'messages': self._messages,
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
    def messages(self) -> List[WsMessage]:
        """
        消息列表
        """

        return self._messages
