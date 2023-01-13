from .._classdef import TypeMessage


class UserInfo_TUid(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称
        tieba_uid (int): 用户个人主页uid

        age (float): 吧龄
        sign (str): 个性签名

        is_god (bool): 是否大神

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
        '_nick_name_new',
        '_tieba_uid',
        '_age',
        '_sign',
        '_is_god',
    ]

    def _init(self, data_proto: TypeMessage) -> "UserInfo_TUid":
        self._user_id = data_proto.id
        if '?' in (portrait := data_proto.portrait):
            self._portrait = portrait[:-13]
        else:
            self._portrait = portrait
        self._user_name = data_proto.name
        self._nick_name_new = data_proto.name_show
        self._tieba_uid = int(data_proto.tieba_uid)
        self._age = float(data_proto.tb_age)
        self._sign = data_proto.intro
        self._is_god = bool(data_proto.new_god_data.status)
        return self

    def _init_null(self) -> "UserInfo_TUid":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
        self._tieba_uid = 0
        self._age = 0.0
        self._sign = ''
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
                'show_name': self.show_name,
                'age': self._age,
                'sign': self._sign,
            }
        )

    def __eq__(self, obj: "UserInfo_TUid") -> bool:
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
    def nick_name_new(self) -> str:
        """
        新版昵称
        """

        return self._nick_name_new

    @property
    def tieba_uid(self) -> int:
        """
        用户个人主页uid

        Note:
            唯一 不可变 可为空
            请注意与user_id区分
        """

        return self._tieba_uid

    @property
    def age(self) -> float:
        """
        吧龄

        Note:
            以年为单位
        """

        return self._age

    @property
    def sign(self) -> str:
        """
        个性签名
        """

        return self._sign

    @property
    def is_god(self) -> bool:
        """
        是否贴吧大神
        """

        return self._is_god

    @property
    def nick_name(self) -> str:
        """
        用户昵称
        """

        return self._nick_name_new

    @property
    def show_name(self) -> str:
        """
        显示名称
        """

        return self._nick_name_new or self._user_name

    @property
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        if self._user_name:
            return self._user_name
        elif self._portrait:
            return f"{self._nick_name_new}/{self._portrait}"
        else:
            return str(self._user_id)
