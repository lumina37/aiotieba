from typing import Mapping

from .._helper import removesuffix


class UserInfo_panel(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称
        nick_name_old (str): 旧版昵称

        gender (int): 性别
        age (float): 吧龄
        post_num (int): 发帖数
        fan_num (int): 粉丝数

        is_vip (bool): 是否超级会员

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
        '_nick_name_new',
        '_nick_name_old',
        '_gender',
        '_age',
        '_post_num',
        '_fan_num',
        '_is_vip',
    ]

    def _init(self, data_map: Mapping) -> "UserInfo_panel":
        self._user_name = data_map['name']
        self._portrait = data_map['portrait']
        self._nick_name_new = data_map['show_nickname']
        self._nick_name_old = data_map['name_show']

        sex = data_map['sex']
        if sex == 'male':
            self._gender = 1
        elif sex == 'female':
            self._gender = 2
        else:
            self._gender = 0

        if (tb_age := data_map['tb_age']) != '-':
            self._age = float(tb_age)
        else:
            self._age = 0.0

        self._post_num = self._num2int(data_map['post_num'])
        self._fan_num = self._num2int(data_map['followed_count'])

        if vip_dict := data_map['vipInfo']:
            self._is_vip = bool(int(vip_dict['v_status']))
        else:
            self._is_vip = False

        return self

    def _init_null(self) -> "UserInfo_panel":
        self._user_id = 0
        self._portrait = ''
        self._user_name = ''
        self._nick_name_new = ''
        self._nick_name_old = ''
        self._gender = 0
        self._age = 0.0
        self._post_num = 0
        self._fan_num = 0
        self._is_vip = False
        return self

    def __str__(self) -> str:
        return self._user_name or self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_name': self._user_name,
                'portrait': self._portrait,
                'show_name': self.show_name,
                'gender': self._gender,
                'age': self._age,
                'post_num': self._post_num,
            }
        )

    def __eq__(self, obj: "UserInfo_panel") -> bool:
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
    def nick_name_old(self) -> str:
        """
        旧版昵称
        """

        return self._nick_name_old

    @property
    def nick_name_new(self) -> str:
        """
        新版昵称
        """

        return self._nick_name_old

    @property
    def gender(self) -> int:
        """
        性别

        Note:
            0未知 1男 2女
        """

        return self._gender

    @property
    def age(self) -> float:
        """
        吧龄

        Note:
            以年为单位
        """

        return self._age

    @property
    def post_num(self) -> int:
        """
        发帖数

        Note:
            是回复数和主题帖数的总和
        """

        return self._post_num

    @property
    def fan_num(self) -> int:
        """
        粉丝数
        """

        return self._fan_num

    @property
    def is_vip(self) -> bool:
        """
        是否超级会员
        """

        return self._is_vip

    @property
    def nick_name(self) -> str:
        """
        用户昵称

        Note:
            该字段不具有唯一性
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

    @staticmethod
    def _num2int(tb_num: str) -> int:
        if isinstance(tb_num, str):
            return int(float(removesuffix(tb_num, '万')) * 1e4)
        else:
            return tb_num
