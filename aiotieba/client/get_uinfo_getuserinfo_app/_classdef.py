from .._classdef import TypeMessage


class UserInfo_guinfo_app(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称

        gender (int): 性别

        is_vip (bool): 是否超级会员
        is_god (bool): 是否大神

        nick_name (str): 用户昵称
        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
        '_nick_name_old',
        '_gender',
        '_is_vip',
        '_is_god',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_guinfo_app":
        self._user_id = data_proto.id
        if '?' in (portrait := data_proto.portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.name
        self._nick_name_old = data_proto.name_show
        self._gender = data_proto.sex
        self._is_vip = bool(data_proto.vipInfo.v_status)
        self._is_god = bool(data_proto.new_god_data.status)
        return self

    def _init_null(self) -> "UserInfo_guinfo_app":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_old = ''
        self._gender = 0
        self._is_vip = False
        self._is_god = False
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

    def __eq__(self, obj: "UserInfo_guinfo_app") -> bool:
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
            唯一 不可变 不可为空
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
            唯一 可变 可为空
            请注意与用户昵称区分
        """

        return self._user_name

    @property
    def gender(self) -> int:
        """
        性别

        Note:
            0未知 1男 2女
        """

        return self._gender

    @property
    def is_vip(self) -> bool:
        """
        是否超级会员
        """

        return self._is_vip

    @property
    def is_god(self) -> bool:
        """
        是否贴吧大神
        """

        return self._is_god

    @property
    def nick_name_old(self) -> str:
        """
        旧版昵称

        Note:
            该字段具有唯一性
        """

        return self._nick_name_old

    @property
    def nick_name(self) -> str:
        """
        用户昵称
        """

        return self._nick_name_old

    @property
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        if self._user_name:
            return self._user_name
        elif self._portrait:
            return f"{self._nick_name_old}/{self._portrait}"
        else:
            return str(self._user_id)
