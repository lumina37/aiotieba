import dataclasses as dcs
from typing import List

from ...enums import Gender, PrivLike, PrivReply
from .vimage import VirtualImage


@dcs.dataclass
class UserInfo:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称
        nick_name_new (str): 新版昵称
        tieba_uid (int): 用户个人主页uid

        glevel (int): 贴吧成长等级
        gender (Gender): 性别
        age (float): 吧龄 以年为单位
        post_num (int): 发帖数
        agree_num (int): 获赞数
        fan_num (int): 粉丝数
        follow_num (int): 关注数
        forum_num (int): 关注贴吧数
        sign (str): 个性签名
        ip (str): ip归属地
        icons (list[str]): 印记信息
        vimage (VirtualImage_pf): 虚拟形象信息

        is_vip (bool): 是否超级会员
        is_god (bool): 是否大神
        is_blocked (bool): 是否被永久封禁屏蔽
        priv_like (PrivLike): 关注吧列表的公开状态
        priv_reply (PrivReply): 帖子评论权限

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name_old: str = ''
    nick_name_new: str = ''
    tieba_uid: int = 0

    glevel: int = 0
    gender: Gender = Gender.UNKNOWN
    age: float = 0.0
    post_num: int = 0
    agree_num: int = 0
    fan_num: int = 0
    follow_num: int = 0
    forum_num: int = 0
    sign: str = ""
    ip: str = ''
    icons: List[str] = dcs.field(default_factory=list)
    vimage: VirtualImage = dcs.field(default_factory=VirtualImage)

    is_vip: bool = False
    is_god: bool = False
    is_blocked: bool = False
    priv_like: PrivLike = PrivLike.PUBLIC
    priv_reply: PrivReply = PrivReply.ALL

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    def __ior__(self, obj) -> "UserInfo":
        for field in dcs.fields(obj):
            if hasattr(self, field.name):
                val = getattr(obj, field.name)
                setattr(self, field.name, val)
        return self

    @property
    def nick_name(self) -> str:
        return self.nick_name_new or self.nick_name_old

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.nick_name_old or self.user_name

    @property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name}/{self.portrait}"
        else:
            return str(self.user_id)
