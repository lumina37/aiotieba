from ..common.typedef import VirtualImage


class UserInfo_getuserinfo(object):
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称
        nick_name_old (str): 旧版昵称
        tieba_uid (int): 用户个人主页uid

        level (int): 等级
        glevel (int): 贴吧成长等级
        gender (int): 性别
        age (float): 吧龄
        post_num (int): 发帖数
        fan_num (int): 粉丝数
        follow_num (int): 关注数
        sign (str): 个性签名
        ip (str): ip归属地
        vimage (VirtualImage): 虚拟形象信息

        is_bawu (bool): 是否吧务
        is_vip (bool): 是否超级会员
        is_god (bool): 是否大神
        priv_like (int): 公开关注吧列表的设置状态
        priv_reply (int): 帖子评论权限的设置状态

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
        '_tieba_uid',
        '_level',
        '_glevel',
        '_gender',
        '_age',
        '_post_num',
        '_fan_num',
        '_follow_num',
        '_sign',
        '_vimage',
        '_ip',
        '_is_bawu',
        '_is_vip',
        '_is_god',
        '_priv_like',
        '_priv_reply',
    ]

    @staticmethod
    def _default() -> "UserInfo_getuserinfo":
        user = UserInfo_getuserinfo()
        user._user_id = 0
        user._portrait = ''
        user._user_name = ''
        user._nick_name_new = ''
        user._nick_name_old = ''
        user._tieba_uid = 0

        user._level = 0
        user._glevel = 0
        user._gender = 0
        user._age = 0.0
        user._post_num = 0
        user._fan_num = 0
        user._follow_num = 0
        user._sign = ''
        user._vimage = VirtualImage()
        user._ip = ''

        user._is_bawu = False
        user._is_vip = False
        user._is_god = False
        user._priv_like = 1
        user._priv_reply = 1

        return user

    def __str__(self) -> str:
        return self._user_name or self._portrait or str(self._user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self._user_id,
                'user_name': self._user_name,
                'portrait': self._portrait,
                'show_name': self.show_name,
                'gender': self._gender,
                'age': self._age,
                'post_num': self._post_num,
            }
        )

    def __eq__(self, obj: "UserInfo_getuserinfo") -> bool:
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
            该字段具有唯一性且不可变
            请注意与用户个人页的tieba_uid区分
        """

        return self._user_id

    @property
    def portrait(self) -> str:
        """
        用户portrait

        Note:
            该字段具有唯一性且不可变
        """

        return self._portrait

    @property
    def user_name(self) -> str:
        """
        用户名

        Note:
            该字段具有唯一性但可变
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

        return self._nick_name_new

    @property
    def tieba_uid(self) -> int:
        """
        用户个人主页uid

        Note:
            具有唯一性
            请注意与user_id区分
        """

        return self._tieba_uid

    @property
    def level(self) -> int:
        """
        等级
        """

        return self._level

    @property
    def glevel(self) -> int:
        """
        贴吧成长等级
        """

        return self._glevel

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
    def follow_num(self) -> int:
        """
        关注数
        """

        return self._follow_num

    @property
    def sign(self) -> str:
        """
        个性签名
        """

        return self._sign

    @property
    def ip(self) -> str:
        """
        ip归属地
        """

        return self._ip

    @property
    def vimage(self) -> VirtualImage:
        """
        虚拟形象信息
        """

        return self._vimage

    @property
    def is_bawu(self) -> bool:
        """
        是否吧务
        """

        return self._is_bawu

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
    def priv_like(self) -> int:
        """
        公开关注吧列表的设置状态

        Note:
            1完全可见 2好友可见 3完全隐藏
        """

        return self._priv_like

    @property
    def priv_reply(self) -> int:
        """
        帖子评论权限的设置状态

        Note:
            1允许所有人 5仅允许我的粉丝 6仅允许我的关注
        """

        return self._priv_reply

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
