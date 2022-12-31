__all__ = [
    'VirtualImage',
    'UserInfo',
    'Page',
    'VoteInfo',
]

from typing import Any, List, Optional, TypeVar, Union

from google.protobuf.message import Message

TypeMessage = TypeVar('TypeMessage', bound=Message)


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

    def __init__(self, enabled: bool = False, state: str = '') -> None:
        self._enabled = enabled
        self._state = state

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


class UserInfo(object):
    """
    用户信息

    Args:
        _id (str | int, optional): 用于快速构造UserInfo的自适应参数 输入用户名或portrait或user_id
        _raw_data (TypeMessage): protobuf源数据

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name (str): 用户昵称
        tieba_uid (int): 用户个人主页uid

        level (int): 等级
        gender (int): 性别
        age (float): 吧龄
        post_num (int): 发帖数
        fan_num (int): 粉丝数
        follow_num (int): 关注数
        glevel (int): 贴吧成长等级
        sign (str): 个性签名
        ip (str): ip归属地
        vimage (VirtualImage): 虚拟形象信息

        is_bawu (bool): 是否吧务
        is_vip (bool): 是否超级会员
        is_god (bool): 是否大神
        priv_like (int): 公开关注吧列表的设置状态
        priv_reply (int): 帖子评论权限的设置状态

        log_name (str): 用于在日志中记录用户信息
        show_name (str): 显示名称
    """

    __slots__ = [
        '_user_id',
        '_portrait',
        '_user_name',
        '_nick_name',
        '_tieba_uid',
        '_level',
        '_gender',
        '_age',
        '_post_num',
        '_fan_num',
        '_follow_num',
        '_glevel',
        '_sign',
        '_vimage',
        '_ip',
        '_is_bawu',
        '_is_vip',
        '_is_god',
        '_priv_like',
        '_priv_reply',
    ]

    def __init__(self, _id: Union[str, int, None] = None, _raw_data: Optional[TypeMessage] = None) -> None:

        if _raw_data:
            self._user_id = _raw_data.id
            self.portrait = _raw_data.portrait
            self._user_name = _raw_data.name
            self._nick_name = _raw_data.name_show
            self.tieba_uid = _raw_data.tieba_uid

            self._level = _raw_data.level_id
            self._gender = _raw_data.gender or _raw_data.sex
            self.age = _raw_data.tb_age
            self._post_num = _raw_data.post_num
            self._fan_num = _raw_data.fans_num
            self._follow_num = _raw_data.concern_num
            self._glevel = _raw_data.user_growth.level_id
            self._sign = _raw_data.intro
            self._ip = _raw_data.ip_address
            self._vimage = VirtualImage(
                bool(_raw_data.virtual_image_info.isset_virtual_image), _raw_data.virtual_image_info.personal_state.text
            )

            self._is_bawu = bool(_raw_data.is_bawu)
            self._is_vip = True if _raw_data.new_tshow_icon else bool(_raw_data.vipInfo.v_status)
            self._is_god = bool(_raw_data.new_god_data.status)
            self.priv_like = _raw_data.priv_sets.like
            self.priv_reply = _raw_data.priv_sets.reply

        else:
            self._user_id = 0
            self._portrait = ''
            self._user_name = ''
            self._nick_name = ''
            self._tieba_uid = 0

            self._level = 0
            self._gender = 0
            self._age = 0.0
            self._post_num = 0
            self._fan_num = 0
            self._follow_num = 0
            self._glevel = 0
            self._sign = ''
            self._vimage = VirtualImage()
            self._ip = ''

            self._is_bawu = False
            self._is_vip = False
            self._is_god = False
            self._priv_like = 1
            self._priv_reply = 1

            if _id:
                if self.is_user_id(_id):
                    self._user_id = _id
                else:
                    self.portrait = _id
                    if not self.portrait:
                        self._user_name = _id

    def __str__(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return self.portrait
        else:
            return str(self.user_id)

    def __repr__(self) -> str:
        return str(
            {
                'user_id': self.user_id,
                'user_name': self.user_name,
                'portrait': self.portrait,
                'nick_name': self.nick_name,
            }
        )

    def __eq__(self, obj: "UserInfo") -> bool:
        return self._user_id == obj._user_id and self._user_name == obj._user_name and self._portrait == obj._portrait

    def __hash__(self) -> int:
        return self._user_id

    def __int__(self) -> int:
        return self._user_id

    def __bool__(self) -> bool:
        return bool(self._user_id) or bool(self._user_name) or bool(self._portrait)

    def __or__(self, obj: "UserInfo") -> "UserInfo":
        self._user_id = self._user_id or obj.user_id
        self.portrait = self.portrait or obj.portrait
        self._user_name = self._user_name or obj.user_name
        self._nick_name = self._nick_name or obj.nick_name
        self.tieba_uid = self.tieba_uid or obj.tieba_uid

        return self

    @staticmethod
    def is_user_id(user_id: Any) -> bool:
        """
        判断数据是否符合user_id格式
        """

        return isinstance(user_id, int)

    @staticmethod
    def is_portrait(portrait: Any) -> bool:
        """
        判断数据是否符合portrait格式
        """

        return isinstance(portrait, str) and portrait.startswith('tb.')

    @property
    def user_id(self) -> int:
        """
        用户user_id

        Note:
            具有唯一性
            请注意与用户主页的tieba_uid区分
        """

        return self._user_id

    @user_id.setter
    def user_id(self, new_user_id: int) -> None:
        self._user_id = int(new_user_id) if new_user_id else 0

    @property
    def portrait(self) -> str:
        """
        用户portrait

        Note:
            具有唯一性
            可以用于获取用户头像
        """

        return self._portrait

    @portrait.setter
    def portrait(self, new_portrait: str) -> None:

        if new_portrait and self.is_portrait(new_portrait):

            beg_start = 33
            q_index = new_portrait.find('?', beg_start)
            and_index = new_portrait.find('&', beg_start)

            if q_index != -1:
                self._portrait = new_portrait[:q_index]
            elif and_index != -1:
                self._portrait = new_portrait[:and_index]
            else:
                self._portrait = new_portrait

        else:
            self._portrait = ''

    @property
    def user_name(self) -> str:
        """
        用户名

        Note:
            具有唯一性
            请注意与用户昵称区分
        """

        return self._user_name

    @user_name.setter
    def user_name(self, new_user_name: str) -> None:
        self._user_name = new_user_name

    @property
    def nick_name(self) -> str:
        """
        用户昵称

        Note:
            不具有唯一性
        """

        return self._nick_name

    @nick_name.setter
    def nick_name(self, new_nick_name: str) -> None:

        if new_nick_name != self.user_name:
            self._nick_name = new_nick_name
        else:
            self._nick_name = ''

    @property
    def tieba_uid(self) -> int:
        """
        用户个人主页uid

        Note:
            具有唯一性
            请注意与user_id区分
        """

        return self._tieba_uid

    @tieba_uid.setter
    def tieba_uid(self, new_tieba_uid: int) -> None:
        self._tieba_uid = int(new_tieba_uid) if new_tieba_uid else 0

    @property
    def level(self) -> int:
        """
        等级
        """

        return self._level

    @level.setter
    def level(self, new_level: int) -> None:
        self._level = new_level

    @property
    def gender(self) -> int:
        """
        性别

        Note:
            0未知 1男 2女
        """

        return self._gender

    @gender.setter
    def gender(self, new_gender: int) -> None:
        self._gender = new_gender

    @property
    def age(self) -> float:
        """
        吧龄

        Note:
            以年为单位
        """

        return self._age

    @age.setter
    def age(self, new_age: float) -> None:
        self._age = float(new_age) if new_age else 0.0

    @property
    def post_num(self) -> int:
        """
        发帖数

        Note:
            是回复数和主题帖数的总和
        """

        return self._post_num

    @post_num.setter
    def post_num(self, new_post_num: int) -> None:
        self._post_num = new_post_num

    @property
    def fan_num(self) -> int:
        """
        粉丝数
        """

        return self._fan_num

    @fan_num.setter
    def fan_num(self, new_fan_num: int) -> None:
        self._fan_num = new_fan_num

    @property
    def follow_num(self) -> int:
        """
        关注数
        """

        return self._follow_num

    @follow_num.setter
    def follow_num(self, new_follow_num: int) -> None:
        self._follow_num = new_follow_num

    @property
    def glevel(self) -> int:
        """
        贴吧成长等级
        """

        return self._glevel

    @glevel.setter
    def glevel(self, new_glevel: int) -> None:
        self._glevel = new_glevel

    @property
    def sign(self) -> str:
        """
        个性签名
        """

        return self._sign

    @sign.setter
    def sign(self, new_sign: str) -> None:
        self._sign = new_sign

    @property
    def ip(self) -> str:
        """
        ip归属地
        """

        return self._ip

    @ip.setter
    def ip(self, new_ip: str) -> None:
        self._ip = new_ip

    @property
    def vimage(self) -> VirtualImage:
        """
        虚拟形象信息
        """

        return self._vimage

    @vimage.setter
    def vimage(self, new_vimage: VirtualImage) -> None:
        self._vimage = new_vimage

    @property
    def is_bawu(self) -> bool:
        """
        是否吧务
        """

        return self._is_bawu

    @is_bawu.setter
    def is_bawu(self, new_is_bawu: bool) -> None:
        self._is_bawu = new_is_bawu

    @property
    def is_vip(self) -> bool:
        """
        是否超级会员
        """

        return self._is_vip

    @is_vip.setter
    def is_vip(self, new_is_vip: bool) -> None:
        self._is_vip = new_is_vip

    @property
    def is_god(self) -> bool:
        """
        是否贴吧大神
        """

        return self._is_god

    @is_god.setter
    def is_god(self, new_is_god: bool) -> None:
        self._is_god = new_is_god

    @property
    def priv_like(self) -> int:
        """
        公开关注吧列表的设置状态

        Note:
            1完全可见 2好友可见 3完全隐藏
        """

        return self._priv_like

    @priv_like.setter
    def priv_like(self, new_priv_like: int) -> None:
        self._priv_like = int(new_priv_like) if new_priv_like else 1

    @property
    def priv_reply(self) -> int:
        """
        帖子评论权限的设置状态

        Note:
            1允许所有人 5仅允许我的粉丝 6仅允许我的关注
        """

        return self._priv_reply

    @priv_reply.setter
    def priv_reply(self, new_priv_reply: int) -> None:
        self._priv_reply = int(new_priv_reply) if new_priv_reply else 1

    @property
    def log_name(self) -> str:
        """
        用于在日志中记录用户信息
        """

        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name}/{self.portrait}"
        else:
            return str(self.user_id)

    @property
    def show_name(self) -> str:
        """
        显示名称
        """

        return self.nick_name if self.nick_name else self.user_name


class Page(object):
    """
    页信息

    Attributes:
        page_size (int): 页大小
        current_page (int): 当前页码
        total_page (int): 总页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = [
        '_page_size',
        '_current_page',
        '_total_page',
        '_total_count',
        '_has_more',
        '_has_prev',
    ]

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:

        if _raw_data:
            self._page_size = _raw_data.page_size
            self._current_page = _raw_data.current_page
            self._total_page = _raw_data.total_page
            self._total_count = _raw_data.total_count

            if self.current_page and self.total_page:
                self._has_more = self.current_page < self.total_page
                self._has_prev = self.current_page > self.total_page
            else:
                self._has_more = bool(_raw_data.has_more)
                self._has_prev = bool(_raw_data.has_prev)

        else:
            self._page_size = 0
            self._current_page = 0
            self._total_page = 0
            self._total_count = 0
            self._has_more = False
            self._has_prev = False

    def __repr__(self) -> str:
        return str(
            {
                'current_page': self.current_page,
                'total_page': self.total_page,
                'has_more': self.has_more,
                'has_prev': self.has_prev,
            }
        )

    @property
    def page_size(self) -> int:
        """
        页大小
        """

        return self._page_size

    @property
    def current_page(self) -> int:
        """
        当前页码
        """

        return self._current_page

    @property
    def total_page(self) -> int:
        """
        总页码
        """

        return self._total_page

    @property
    def total_count(self) -> int:
        """
        总计数
        """

        return self._total_count

    @property
    def has_more(self) -> bool:
        """
        是否有后继页
        """

        return self._has_more

    @property
    def has_prev(self) -> bool:
        """
        是否有前驱页
        """

        return self._has_prev


class _VoteOption(object):
    """
    投票选项信息

    Attributes:
        vote_num (int): 得票数
        text (str): 选项描述文字
        image (str): 选项描述图像链接
    """

    __slots__ = [
        '_vote_num',
        '_text',
        '_image',
    ]

    def __init__(self, _raw_data: TypeMessage) -> None:
        self._vote_num = _raw_data.num
        self._text = _raw_data.text
        self._image = _raw_data.image

    @property
    def vote_num(self) -> int:
        """
        得票数
        """

        return self._vote_num

    @property
    def text(self) -> str:
        """
        选项文字
        """

        return self._text

    @property
    def image(self) -> str:
        """
        选项图片链接
        """

        return self._image


class VoteInfo(object):
    """
    投票信息

    Attributes:
        title (str): 投票标题
        is_multi (bool): 是否多选
        options (list[VoteOption]): 选项列表
        total_vote (int): 总投票数
        total_user (int): 总投票人数
    """

    __slots__ = [
        '_title',
        '_is_multi',
        '_options',
        '_total_vote',
        '_total_user',
    ]

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:

        if _raw_data:
            self._title = _raw_data.title
            self._is_multi = bool(_raw_data.is_multi)
            self._options = _raw_data.options
            self._total_vote = _raw_data.total_poll
            self._total_user = _raw_data.total_num

        else:
            self._title = ''
            self._is_multi = False
            self._options = None
            self._total_vote = 0
            self._total_user = 0

    def __len__(self) -> int:
        return self.options.__len__()

    def __bool__(self) -> bool:
        return bool(self.options)

    @property
    def title(self) -> str:
        """
        投票标题
        """

        return self._title

    @property
    def is_multi(self) -> bool:
        """
        是否多选
        """

        return self._is_multi

    @property
    def options(self) -> List[_VoteOption]:
        """
        选项列表
        """

        if not isinstance(self._options, list):
            if self._options is not None:
                self._options = [_VoteOption(_proto) for _proto in self._options]
            else:
                self._options = []

        return self._options

    @property
    def total_vote(self) -> int:
        """
        总投票数
        """

        return self._total_vote

    @property
    def total_user(self) -> int:
        """
        总投票人数
        """

        return self._total_user
