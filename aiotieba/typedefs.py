__all__ = [
    'BasicUserInfo',
    'UserInfo',
    'FragmentUnknown',
    'FragText',
    'FragEmoji',
    'FragImage',
    'FragAt',
    'FragLink',
    'FragVoice',
    'FragTiebaPlus',
    'FragItem',
    'Fragments',
    'BasicForum',
    'Page',
    'VoteInfo',
    'ShareThread',
    'Thread',
    'Threads',
    'Post',
    'Posts',
    'Comment',
    'Comments',
    'Reply',
    'Replys',
    'At',
    'Ats',
    'Search',
    'Searches',
    'NewThread',
    'UserPost',
    'UserPosts',
    'RankUser',
    'RankUsers',
    'MemberUser',
    'MemberUsers',
    'SquareForum',
    'SquareForums',
    'Forum',
    'FollowForums',
    'RecomThreads',
    'Recover',
    'Recovers',
    'BlacklistUsers',
    'Appeal',
    'Appeals',
    'Fans',
    'Follows',
    'SelfFollowForums',
    'DislikeForums',
]

import abc
import json
import urllib.parse
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    SupportsIndex,
    TypeVar,
    Union,
    overload,
    runtime_checkable,
)

import bs4
import yarl
from google.protobuf.message import Message
from google.protobuf.json_format import ParseDict

from ._logger import LOG
from .protobuf import GetDislikeListResIdl_pb2, Page_pb2, ThreadInfo_pb2, User_pb2

_TypeMessage = TypeVar('_TypeMessage', bound=Message)


class BasicUserInfo(object):
    """
    基本用户属性

    Args:
        _id (str | int, optional): 用于快速构造BasicUserInfo的自适应参数 输入用户名/portrait/user_id
        _raw_data (_TypeMessage): protobuf源数据

    Attributes:
        user_id (int): user_id
        user_name (str): 用户名
        portrait (str): portrait
    """

    __slots__ = [
        '_user_id',
        '_user_name',
        '_portrait',
    ]

    def __init__(self, _id: Union[str, int, None] = None, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(BasicUserInfo, self).__init__()

        if _raw_data:
            self._user_id = _raw_data.id
            self._user_name = _raw_data.name
            self.portrait = _raw_data.portrait

        else:
            self._user_id = 0
            self._user_name = ''
            self._portrait = ''

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
            }
        )

    def __eq__(self, obj: "BasicUserInfo") -> bool:
        return self.user_id == obj.user_id and self.user_name == obj.user_name and self.portrait == obj.portrait

    def __hash__(self) -> int:
        return self.user_id

    def __int__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @staticmethod
    def is_portrait(portrait: Any) -> bool:
        """
        判断数据是否符合portrait格式
        """

        return isinstance(portrait, str) and portrait.startswith('tb.')

    @staticmethod
    def is_user_id(user_id: Any) -> bool:
        """
        判断数据是否符合user_id格式
        """

        return isinstance(user_id, int)

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
    def log_name(self) -> str:
        """
        用于在日志中记录用户属性
        """

        if self.user_name:
            return self.user_name
        elif self.portrait:
            return self.portrait
        else:
            return str(self.user_id)


class UserInfo(BasicUserInfo):
    """
    用户属性

    Args:
        _id (str | int, optional): 用于快速构造UserInfo的自适应参数 输入用户名或portrait或user_id
        _raw_data (_TypeMessage): protobuf源数据

    Attributes:
        user_id (int): user_id
        user_name (str): 用户名
        portrait (str): portrait
        nick_name (str): 用户昵称
        tieba_uid (int): 用户个人主页uid

        level (int): 等级
        gender (int): 性别
        age (float): 吧龄
        post_num (int): 发帖数
        fan_num (int): 粉丝数
        follow_num (int): 关注数
        sign (str): 个性签名
        ip (str): ip归属地

        is_bawu (bool): 是否吧务
        is_vip (bool): 是否vip
        is_god (bool): 是否大神
        priv_like (int): 是否公开关注贴吧
        priv_reply (int): 帖子评论权限
    """

    __slots__ = [
        '_nick_name',
        '_tieba_uid',
        '_level',
        '_gender',
        '_age',
        '_post_num',
        '_fan_num',
        '_follow_num',
        '_sign',
        '_ip',
        '_is_bawu',
        '_is_vip',
        '_is_god',
        '_priv_like',
        '_priv_reply',
    ]

    def __init__(self, _id: Union[str, int, None] = None, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(UserInfo, self).__init__(_id, _raw_data)

        if _raw_data:
            self._nick_name = _raw_data.name_show
            self.tieba_uid = _raw_data.tieba_uid

            self._level = _raw_data.level_id
            self._gender = _raw_data.gender or _raw_data.sex
            self.age = _raw_data.tb_age
            self._post_num = _raw_data.post_num
            self._fan_num = _raw_data.fans_num
            self._follow_num = _raw_data.concern_num
            self._sign = _raw_data.intro
            self._ip = _raw_data.ip_address

            self._is_bawu = bool(_raw_data.is_bawu)
            self._is_vip = True if _raw_data.new_tshow_icon else bool(_raw_data.vipInfo.v_status)
            self._is_god = bool(_raw_data.new_god_data.status)
            self.priv_like = _raw_data.priv_sets.like
            self.priv_reply = _raw_data.priv_sets.reply

        else:
            self._nick_name = ''
            self._tieba_uid = 0

            self._level = 0
            self._gender = 0
            self._age = 0.0
            self._post_num = 0
            self._fan_num = 0
            self._follow_num = 0
            self._sign = ''
            self._ip = ''

            self._is_bawu = False
            self._is_vip = False
            self._is_god = False
            self._priv_like = 1
            self._priv_reply = 1

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
        return super(UserInfo, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(UserInfo, self).__hash__()

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
    def log_name(self) -> str:
        """
        用于在日志中记录用户属性
        """

        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name}/{self.portrait}"
        else:
            return str(self.user_id)

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
            未知0 男1 女2
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
        是否公开关注贴吧

        Note:
            完全可见1 好友可见2 完全隐藏3
        """

        return self._priv_like

    @priv_like.setter
    def priv_like(self, new_priv_like: int) -> None:
        self._priv_like = int(new_priv_like) if new_priv_like else 1

    @property
    def priv_reply(self) -> int:
        """
        帖子评论权限

        Note:
            允许所有人1 仅允许我的粉丝5 仅允许我的关注6
        """

        return self._priv_reply

    @priv_reply.setter
    def priv_reply(self, new_priv_reply: int) -> None:
        self._priv_reply = int(new_priv_reply) if new_priv_reply else 1


class _Fragment(object):
    """
    内容碎片基类
    """

    __slots__ = ['_raw_data']

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        self._raw_data = _raw_data


_TypeFragment = TypeVar('_TypeFragment', bound=_Fragment)


class FragmentUnknown(_Fragment):
    """
    未知碎片
    """

    __slots__ = []


class FragText(_Fragment):
    """
    纯文本碎片

    Attributes:
        text (str): 文本内容
    """

    __slots__ = ['_text']

    def __init__(self, _raw_data: _TypeMessage) -> None:
        super(FragText, self).__init__(_raw_data)
        self._text = _raw_data.text

    def __repr__(self) -> str:
        return str({'text': self.text})

    @property
    def text(self) -> str:
        """
        文本内容
        """

        return self._text


@runtime_checkable
class ProtocolText(Protocol):
    @property
    def text(self) -> str:
        pass


class FragEmoji(_Fragment):
    """
    表情碎片

    Attributes:
        desc (str): 表情描述
    """

    __slots__ = ['_desc']

    def __init__(self, _raw_data: _TypeMessage) -> None:
        super(FragEmoji, self).__init__(_raw_data)
        self._desc: str = _raw_data.c

    def __repr__(self) -> str:
        return str({'desc': self.desc})

    @property
    def desc(self) -> str:
        """
        表情描述
        """

        return self._desc


class FragImage(_Fragment):
    """
    图像碎片

    Attributes:
        src (str): 压缩图像链接
        big_src (str): 大图链接
        origin_src (str): 原图链接
        hash (str): 百度图床hash
        show_width (int): 图像在客户端显示的宽度
        show_height (int): 图像在客户端显示的高度
    """

    __slots__ = [
        '_src',
        '_big_src',
        '_origin_src',
        '_origin_size',
        '_hash',
        '_show_width',
        '_show_height',
    ]

    def __init__(self, _raw_data: _TypeMessage) -> None:
        super(FragImage, self).__init__(_raw_data)

        self._src = _raw_data.cdn_src or _raw_data.src
        self._big_src = _raw_data.big_cdn_src or _raw_data.big_src
        self._origin_src = _raw_data.origin_src
        self._origin_size = _raw_data.origin_size

        self._hash = None
        self._show_width = None
        self._show_height = None

    def __repr__(self) -> str:
        return str({'src': self.src})

    @property
    def src(self) -> str:
        """
        压缩图像链接
        """

        return self._src

    @property
    def big_src(self) -> str:
        """
        大图链接
        """

        return self._big_src

    @property
    def origin_src(self) -> str:
        """
        原图链接
        """

        return self._origin_src

    @property
    def origin_size(self) -> int:
        """
        原图大小
        """

        return self._origin_size

    @property
    def hash(self) -> str:
        """
        图像的百度图床hash
        """

        if self._hash is None:
            first_qmark_idx = self.src.find('?')
            end_idx = self.src.rfind('.', 0, first_qmark_idx)

            if end_idx == -1:
                self._hash = ''
            else:
                start_idx = self.src.rfind('/', 0, end_idx)
                self._hash = self.src[start_idx + 1 : end_idx]

        return self._hash

    def _init_wh(self) -> None:

        bsize: str = self._raw_data.bsize
        show_width, _, show_height = bsize.partition(',')

        if show_width and show_height:
            self._show_width = int(show_width)
            self._show_height = int(show_height)

        else:
            self._show_width = 0
            self._show_height = 0

    @property
    def show_width(self) -> int:
        """
        图像在客户端显示的宽度
        """

        if self._show_width is None:
            self._init_wh()
        return self._show_width

    @property
    def show_height(self) -> int:
        """
        图像在客户端显示的高度
        """

        if self._show_height is None:
            self._init_wh()
        return self._show_height


class FragAt(_Fragment):
    """
    @碎片

    Attributes:
        text (str): 被@用户的昵称
        user_id (int): 被@用户的user_id
    """

    __slots__ = [
        '_text',
        '_user_id',
    ]

    def __init__(self, _raw_data: _TypeMessage) -> None:
        super(FragAt, self).__init__(_raw_data)

        self._text = _raw_data.text
        self._user_id = _raw_data.uid

    def __repr__(self) -> str:
        return str(
            {
                'text': self.text,
                'user_id': self.user_id,
            }
        )

    @property
    def text(self) -> str:
        """
        被@用户的昵称
        """

        return self._text

    @property
    def user_id(self) -> int:
        """
        被@用户的user_id
        """

        return self._user_id


class FragLink(_Fragment):
    """
    链接碎片

    Attributes:
        text (str): 原链接
        title (str): 链接标题
        url (yarl.URL): 使用yarl解析后的链接
        raw_url (str): 原链接
        is_external (bool): 是否外部链接
    """

    __slots__ = [
        '_text',
        '_url',
        '_raw_url',
        '_is_external',
    ]

    external_perfix: ClassVar[str] = "http://tieba.baidu.com/mo/q/checkurl"

    def __init__(self, _raw_data: _TypeMessage) -> None:
        super(FragLink, self).__init__(_raw_data)

        self._text = _raw_data.text
        self._url = None

        self._raw_url: str = _raw_data.link
        self._is_external = self._raw_url.startswith(self.external_perfix)

        if self._is_external:
            self._raw_url = urllib.parse.unquote(self._raw_url.removeprefix(self.external_perfix + "?url="))

    def __repr__(self) -> str:
        return str(
            {
                'title': self.title,
                'raw_url': self.raw_url,
            }
        )

    @property
    def text(self) -> str:
        """
        原链接

        Note:
            外链会在解析前先去除external_perfix前缀
        """

        return self._raw_url

    @property
    def title(self) -> str:
        """
        链接标题
        """

        return self._text

    @property
    def url(self) -> yarl.URL:
        """
        yarl解析后的链接

        Note:
            外链会在解析前先去除external_perfix前缀
        """

        if self._url is None:
            self._url = yarl.URL(self._raw_url)
        return self._url

    @property
    def raw_url(self) -> str:
        """
        原链接

        Note:
            外链会在解析前先去除external_perfix前缀
        """

        return self._raw_url

    @property
    def is_external(self) -> bool:
        """
        是否外部链接
        """

        return self._is_external


class FragVoice(_Fragment):
    """
    音频碎片

    Attributes:
        voice_md5 (str): 音频md5
    """

    __slots__ = ['_voice_md5']

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(FragVoice, self).__init__(_raw_data)

        if _raw_data:
            self._voice_md5 = _raw_data.voice_md5
        else:
            self._voice_md5 = ''

    def __repr__(self) -> str:
        return str({'voice_md5': self.voice_md5})

    @property
    def voice_md5(self) -> str:
        """
        音频md5

        Note:
            可用于下载音频
        """

        return self._voice_md5


class FragTiebaPlus(_Fragment):
    """
    贴吧+广告碎片

    Attributes:
        text (str): 贴吧+广告描述
        url (str): 贴吧+广告跳转链接
    """

    __slots__ = [
        '_text',
        '_url',
    ]

    def __init__(self, _raw_data: _TypeMessage) -> None:
        super(FragTiebaPlus, self).__init__(_raw_data)

        self._text = _raw_data.tiebaplus_info.desc
        self._url = _raw_data.tiebaplus_info.jump_url

    def __repr__(self) -> str:
        return str(
            {
                'text': self.text,
                'url': self.url,
            }
        )

    @property
    def text(self) -> str:
        """
        贴吧+广告描述
        """

        return self._text

    @property
    def url(self) -> str:
        """
        贴吧+广告跳转链接
        """

        return self._url


class FragItem(_Fragment):
    """
    item碎片

    Attributes:
        text (str): item名称
    """

    __slots__ = ['_text']

    def __init__(self, _raw_data: _TypeMessage) -> None:
        super(FragItem, self).__init__(_raw_data)
        self._text = _raw_data.item.item_name

    def __repr__(self) -> str:
        return str({'text': self.text})

    @property
    def text(self) -> str:
        """
        item名称
        """

        return self._text


class Fragments(object):
    """
    正文内容碎片列表

    Attributes:
        _frags (list[_TypeFragment]): 所有碎片的混合列表

        text (str): 文本内容

        texts (list[ProtocolText]): 纯文本碎片列表
        emojis (list[FragEmoji]): 表情碎片列表
        imgs (list[FragImage]): 图像碎片列表
        ats (list[FragAt]): @碎片列表
        links (list[FragLink]): 链接碎片列表
        voice (FragVoice): 音频碎片
        tiebapluses (list[FragTiebaPlus]): 贴吧+碎片列表
    """

    __slots__ = [
        '_frags',
        '_text',
        '_texts',
        '_emojis',
        '_imgs',
        '_ats',
        '_links',
        '_voice',
        '_tiebapluses',
    ]

    def __init__(self, _raw_datas: Optional[Iterable[_TypeMessage]] = None) -> None:
        def _init_by_type(_raw_data) -> _TypeFragment:
            frag_type: int = _raw_data.type
            # 0纯文本 9电话号 18话题 27百科词条
            if frag_type in [0, 9, 18, 27]:
                fragment = FragText(_raw_data)
            # 11:tid=5047676428
            elif frag_type in [2, 11]:
                fragment = FragEmoji(_raw_data)
                self._emojis.append(fragment)
            # 20:tid=5470214675
            elif frag_type in [3, 20]:
                fragment = FragImage(_raw_data)
                self._imgs.append(fragment)
            elif frag_type == 4:
                fragment = FragAt(_raw_data)
                self._ats.append(fragment)
            elif frag_type == 1:
                fragment = FragLink(_raw_data)
                self._links.append(fragment)
            elif frag_type == 5:  # video
                fragment = FragmentUnknown(_raw_data)
            elif frag_type == 10:
                fragment = FragVoice(_raw_data)
                self._voice = fragment
            # 35|36:tid=7769728331 / 37:tid=7760184147
            elif frag_type in [35, 36, 37]:
                fragment = FragTiebaPlus(_raw_data)
                self._tiebapluses.append(fragment)
            else:
                fragment = FragmentUnknown(_raw_data)
                LOG.warning(f"Unknown fragment type. type={_raw_data.type}")

            return fragment

        self._text: str = None
        self._texts: List[FragText] = None
        self._links: List[FragLink] = []
        self._imgs: List[FragImage] = []
        self._emojis: List[FragEmoji] = []
        self._ats: List[FragAt] = []
        self._voice: FragVoice = None
        self._tiebapluses: List[FragTiebaPlus] = []

        if _raw_datas:
            self._frags: List[_TypeFragment] = [_init_by_type(frag_proto) for frag_proto in _raw_datas]
        else:
            self._frags = []

    def __repr__(self) -> str:
        return str(self._frags)

    @property
    def text(self) -> str:
        """
        文本内容
        """

        if self._text is None:
            self._text = ''.join([frag.text for frag in self.texts])
        return self._text

    @property
    def texts(self) -> List[ProtocolText]:
        """
        纯文本碎片列表
        """

        if self._texts is None:
            self._texts = [frag for frag in self._frags if hasattr(frag, 'text')]
        return self._texts

    @property
    def emojis(self) -> List[FragEmoji]:
        """
        表情碎片列表
        """

        return self._emojis

    @property
    def imgs(self) -> List[FragImage]:
        """
        图像碎片列表
        """

        return self._imgs

    @property
    def ats(self) -> List[FragAt]:
        """
        @碎片列表
        """

        return self._ats

    @property
    def links(self) -> List[FragLink]:
        """
        链接碎片列表
        """

        return self._links

    @property
    def voice(self) -> FragVoice:
        """
        音频碎片
        """

        if self._voice is None:
            self._voice = FragVoice()
        return self._voice

    @property
    def tiebapluses(self) -> List[FragTiebaPlus]:
        """
        贴吧+碎片列表
        """

        return self._tiebapluses

    def __iter__(self) -> Iterator[_TypeFragment]:
        return self._frags.__iter__()

    @overload
    def __getitem__(self, idx: SupportsIndex) -> _TypeFragment:
        ...

    @overload
    def __getitem__(self, idx: slice) -> List[_TypeFragment]:
        ...

    def __getitem__(self, idx):
        return self._frags.__getitem__(idx)

    def __setitem__(self, idx, val) -> None:
        raise NotImplementedError

    def __delitem__(self, idx) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        return self._frags.__len__()

    def __bool__(self) -> bool:
        return bool(self._frags)


class BasicForum(object):
    """
    贴吧基本信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名
    """

    __slots__ = [
        '_fid',
        '_fname',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(BasicForum, self).__init__()

        if _raw_data:
            self._fid = _raw_data.forum_id
            self._fname = _raw_data.forum_name

        else:
            self._fid = 0
            self._fname = ''

    def __repr__(self) -> str:
        return str(
            {
                'fid': self.fid,
                'fname': self.fname,
            }
        )

    @property
    def fid(self) -> int:
        """
        贴吧id
        """

        return self._fid

    @property
    def fname(self) -> str:
        """
        贴吧名
        """

        return self._fname


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

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
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


class _Container(object):
    """
    基本的内容容器

    Attributes:
        text (str): 文本内容

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id
    """

    __slots__ = [
        '_text',
        '_fname',
        '_fid',
        '_tid',
        '_pid',
        '_user',
        '_author_id',
    ]

    def __init__(self) -> None:
        self._text = None
        self._fname = ''
        self._fid = 0
        self._tid = 0
        self._pid = 0
        self._user = None
        self._author_id = None

    def __repr__(self) -> str:
        return str(
            {
                'tid': self.tid,
                'pid': self.pid,
                'user': self.user.log_name,
                'text': self.text,
            }
        )

    def __eq__(self, obj: "_Container") -> bool:
        return self._pid == obj._pid

    def __hash__(self) -> int:
        return self._pid

    @property
    def text(self) -> str:
        """
        文本内容
        """

        if self._text is None:
            raise NotImplementedError
        return self._text

    @property
    def fid(self) -> int:
        """
        所在吧id
        """

        return self._fid

    @property
    def fname(self) -> str:
        """
        所在贴吧名
        """

        return self._fname

    @property
    def tid(self) -> int:
        """
        所在主题帖id
        """

        return self._tid

    @property
    def pid(self) -> int:
        """
        回复id
        """

        return self._pid

    @property
    def user(self) -> UserInfo:
        """
        发布者的用户信息
        """

        if self._user is None:
            self._user = UserInfo()
        return self._user

    @property
    def author_id(self) -> int:
        """
        发布者的user_id
        """

        if not self._author_id:
            self._author_id = self.user.user_id
        return self._author_id


_TypeContainer = TypeVar('_TypeContainer', bound=_Container)


class _Containers(Generic[_TypeContainer]):
    """
    内容列表的泛型基类
    约定取内容的通用接口

    Attributes:
        objs (list[_TypeContainer]): 内容列表
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_objs']

    def __init__(self) -> None:
        self._objs = None

    def __repr__(self) -> str:
        return str(self.objs)

    def __iter__(self) -> Iterator[_TypeContainer]:
        return self.objs.__iter__()

    @overload
    def __getitem__(self, idx: SupportsIndex) -> _TypeContainer:
        ...

    @overload
    def __getitem__(self, idx: slice) -> List[_TypeContainer]:
        ...

    def __getitem__(self, idx):
        return self.objs.__getitem__(idx)

    def __setitem__(self, idx, val):
        raise NotImplementedError

    def __delitem__(self, idx):
        raise NotImplementedError

    def __len__(self) -> int:
        return self.objs.__len__()

    def __bool__(self) -> bool:
        return bool(self.objs)

    @property
    @abc.abstractmethod
    def objs(self) -> List[_TypeContainer]:
        """
        内容列表
        """

        ...

    @property
    @abc.abstractmethod
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        ...


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

    def __init__(self, _raw_data: _TypeMessage) -> None:

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

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:

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


class ShareThread(_Container):
    """
    被分享的主题帖信息

    Attributes:
        text (str): 文本内容
        contents (Fragments): 正文内容碎片列表
        title (str): 标题内容

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼的回复id

        vote_info (VoteInfo): 投票内容
    """

    __slots__ = [
        '_contents',
        '_medias',
        '_voice',
        '_title',
        '_vote_info',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(ShareThread, self).__init__()

        if _raw_data:
            self._contents = _raw_data.content
            self._medias = _raw_data.media
            self._voice = _raw_data.voice
            self._title = _raw_data.title

            self._fid = _raw_data.fid
            self._fname = _raw_data.fname
            self._tid = int(_raw_data.tid)
            self._pid = _raw_data.pid

            self._vote_info = _raw_data.poll_info

        else:
            self._contents = None
            self._medias = None
            self._voice = None
            self._title = ''

            self._vote_info = None

    def __eq__(self, obj: "ShareThread") -> bool:
        return super(ShareThread, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(ShareThread, self).__hash__()

    @property
    def text(self) -> str:
        """
        文本内容

        Note:
            如果有标题的话还会在正文前附上标题
        """

        if self._text is None:

            if self.title:
                self._text = f"{self.title}\n{self.contents.text}"
            else:
                self._text = self.contents.text

        return self._text

    @property
    def contents(self) -> Fragments:
        """
        正文内容碎片列表
        """

        if not isinstance(self._contents, Fragments):
            if self._contents is not None:

                self._contents = Fragments(self._contents)

                img_frags = [FragImage(_proto) for _proto in self._medias]
                self._contents._frags += img_frags
                self._contents._imgs += img_frags

                if _protos := self._voice:
                    self._contents._voice = FragVoice(_protos[0])

            else:
                self._contents = Fragments()

        return self._contents

    @property
    def title(self) -> str:
        """
        帖子标题
        """

        return self._title

    @property
    def vote_info(self) -> VoteInfo:
        """
        投票内容
        """

        if not isinstance(self._vote_info, VoteInfo):
            if self._vote_info is not None:
                self._vote_info = VoteInfo(self._vote_info) if self._vote_info.options else VoteInfo()
            else:
                self._vote_info = VoteInfo()

        return self._vote_info


class Thread(_Container):
    """
    主题帖信息
    用于c/f/frs/page接口

    Attributes:
        text (str): 文本内容
        contents (Fragments): 正文内容碎片列表
        title (str): 标题

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼的回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id

        tab_id (int): 分区编号
        is_good (bool): 是否精品帖
        is_top (bool): 是否置顶帖
        is_share (bool): 是否分享帖
        is_hide (bool): 是否被屏蔽
        is_livepost (bool): 是否为置顶话题

        vote_info (VoteInfo): 投票信息
        share_origin (ShareThread): 转发来的原帖内容
        view_num (int): 浏览量
        reply_num (int): 回复数
        share_num (int): 分享数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间
        last_time (int): 最后回复时间
    """

    __slots__ = [
        '_contents',
        '_title',
        '_tab_id',
        '_is_good',
        '_is_top',
        '_is_share',
        '_is_hide',
        '_is_livepost',
        '_vote_info',
        '_share_origin',
        '_view_num',
        '_reply_num',
        '_share_num',
        '_agree',
        '_disagree',
        '_create_time',
        '_last_time',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(Thread, self).__init__()

        if _raw_data:
            self._contents = _raw_data.first_post_content
            self._title = _raw_data.title

            self._fid = _raw_data.fid
            self._fname = _raw_data.fname
            self._tid = _raw_data.id
            self._pid = _raw_data.first_post_id
            self._user = UserInfo(_raw_data=_raw_data.author) if _raw_data.author.id else None
            self._author_id = _raw_data.author_id

            self._tab_id = _raw_data.tab_id
            self._is_good = bool(_raw_data.is_good)
            self._is_top = bool(_raw_data.is_top)
            self._is_share = bool(_raw_data.is_share_thread)
            self._is_hide = bool(_raw_data.is_frs_mask)
            self._is_livepost = bool(_raw_data.is_livepost)

            self._vote_info = _raw_data.poll_info
            self._share_origin = _raw_data.origin_thread_info
            self._view_num = _raw_data.view_num
            self._reply_num = _raw_data.reply_num
            self._share_num = _raw_data.share_num
            self._agree = _raw_data.agree.agree_num
            self._disagree = _raw_data.agree.disagree_num
            self._create_time = _raw_data.create_time
            self._last_time = _raw_data.last_time_int

        else:
            self._contents = None
            self._title = ''

            self._tab_id = 0
            self._is_good = False
            self._is_top = False
            self._is_share = False
            self._is_hide = False
            self._is_livepost = False

            self._vote_info = None
            self._share_origin = None
            self._view_num = 0
            self._reply_num = 0
            self._share_num = 0
            self._agree = 0
            self._disagree = 0
            self._create_time = 0
            self._last_time = 0

    def __eq__(self, obj: "Thread") -> bool:
        return super(Thread, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(Thread, self).__hash__()

    @property
    def text(self) -> str:
        """
        文本内容

        Note:
            如果有标题的话还会在正文前附上标题
        """

        if self._text is None:

            if self.title:
                self._text = f"{self.title}\n{self.contents.text}"
            else:
                self._text = self.contents.text

        return self._text

    @property
    def contents(self) -> Fragments:
        """
        正文内容碎片列表
        """

        if not isinstance(self._contents, Fragments):
            if self._contents is not None:
                self._contents = Fragments(self._contents)
            else:
                self._contents = Fragments()

        return self._contents

    @property
    def title(self) -> str:
        """
        帖子标题
        """

        return self._title

    @property
    def tab_id(self) -> int:
        """
        帖子所在分区id
        """

        return self._tab_id

    @property
    def is_good(self) -> bool:
        """
        是否精品帖
        """

        return self._is_good

    @property
    def is_top(self) -> bool:
        """
        是否置顶帖
        """

        return self._is_top

    @property
    def is_share(self) -> bool:
        """
        是否分享帖
        """

        return self._is_share

    @property
    def is_hide(self) -> bool:
        """
        是否被屏蔽
        """

        return self._is_hide

    @property
    def is_livepost(self) -> bool:
        """
        是否为置顶话题
        """

        return self._is_livepost

    @property
    def vote_info(self) -> VoteInfo:
        """
        投票信息
        """

        if not isinstance(self._vote_info, VoteInfo):
            if self._vote_info is not None:
                self._vote_info = VoteInfo(self._vote_info) if self._vote_info.options else VoteInfo()
            else:
                self._vote_info = VoteInfo()

        return self._vote_info

    @property
    def share_origin(self) -> ShareThread:
        """
        转发来的原帖内容
        """

        if not isinstance(self._share_origin, ShareThread):
            if self._share_origin is not None and self._share_origin.tid:
                self._share_origin = ShareThread(self._share_origin)
            else:
                self._share_origin = ShareThread()

        return self._share_origin

    @property
    def view_num(self) -> int:
        """
        浏览量
        """

        return self._view_num

    @property
    def reply_num(self) -> int:
        """
        回复数
        """

        return self._reply_num

    @property
    def share_num(self) -> int:
        """
        分享数
        """

        return self._share_num

    @property
    def agree(self) -> int:
        """
        点赞数
        """

        return self._agree

    @property
    def disagree(self) -> int:
        """
        点踩数
        """

        return self._disagree

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳
        """

        return self._create_time

    @property
    def last_time(self) -> int:
        """
        最后回复时间

        Note:
            10位时间戳
        """

        return self._last_time


class Threads(_Containers[Thread]):
    """
    主题帖列表

    Attributes:
        objs (list[Thread]): 主题帖列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页

        forum (BasicForum): 所在吧信息
        tab_map (dict[str, int]): 分区名到分区id的映射表
    """

    __slots__ = [
        '_users',
        '_page',
        '_forum',
        '_tab_map',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(Threads, self).__init__()

        if _raw_data:
            self._objs = _raw_data.thread_list
            self._users = _raw_data.user_list

            self._page = _raw_data.page
            self._forum = _raw_data.forum
            self._tab_map = _raw_data.nav_tab_info.tab

        else:
            self._users = []

            self._page = None
            self._forum = None
            self._tab_map = None

    @property
    def objs(self) -> List[Thread]:
        """
        主题帖列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:

                self._objs = [Thread(_proto) for _proto in self._objs]
                users = {user.user_id: user for _proto in self._users if (user := UserInfo(_raw_data=_proto)).user_id}
                self._users = None

                for thread in self._objs:
                    thread._fname = self.forum.fname
                    thread._user = users[thread.author_id]

            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                self._page = Page(self._page)
            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more

    @property
    def forum(self) -> BasicForum:
        """
        所在吧信息
        """

        if not isinstance(self._forum, BasicForum):
            if self._forum is not None:
                self._forum = BasicForum(self._forum)
            else:
                self._forum = BasicForum()

        return self._forum

    @property
    def tab_map(self) -> Dict[str, int]:
        """
        分区名到分区id的映射表
        """

        if not isinstance(self._tab_map, dict):
            if self._tab_map is not None:
                self._tab_map = {_proto.tab_name: _proto.tab_id for _proto in self._tab_map}
            else:
                self._tab_map = {}

        return self._tab_map


class Post(_Container):
    """
    楼层信息

    Attributes:
        text (str): 文本内容
        contents (Fragments): 正文内容碎片列表
        sign (str): 小尾巴文本内容
        comments (list[Comment]): 楼中楼列表

        fid (int): 所在吧id
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id

        floor (int): 楼层数
        reply_num (int): 楼中楼数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间
        is_thread_author (bool): 是否楼主
    """

    __slots__ = [
        '_contents',
        '_sign',
        '_comments',
        '_floor',
        '_reply_num',
        '_agree',
        '_disagree',
        '_create_time',
        '_is_thread_author',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(Post, self).__init__()

        self._is_thread_author = False

        if _raw_data:
            self._contents = _raw_data.content
            self._sign = _raw_data.signature.content
            self._comments = _raw_data.sub_post_list.sub_post_list

            self._pid = _raw_data.id
            self._user = UserInfo(_raw_data=_raw_data.author) if _raw_data.author.id else None
            self._author_id = _raw_data.author_id

            self._floor = _raw_data.floor
            self._reply_num = _raw_data.sub_post_number
            self._agree = _raw_data.agree.agree_num
            self._disagree = _raw_data.agree.disagree_num
            self._create_time = _raw_data.time

        else:
            self._contents = None
            self._sign = None
            self._comments = None

            self._floor = 0
            self._reply_num = 0
            self._agree = 0
            self._disagree = 0
            self._create_time = 0

    def __eq__(self, obj: "Post") -> bool:
        return super(Post, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(Post, self).__hash__()

    @property
    def text(self) -> str:
        """
        文本内容

        Note:
            如果有小尾巴的话还会在正文后附上小尾巴
        """

        if self._text is None:

            if self.sign:
                self._text = f'{self.contents.text}\n{self.sign}'
            else:
                self._text = self.contents.text

        return self._text

    @property
    def contents(self) -> Fragments:
        """
        正文内容碎片列表
        """

        if not isinstance(self._contents, Fragments):
            if self._contents is not None:
                self._contents = Fragments(self._contents)
            else:
                self._contents = Fragments()

        return self._contents

    @property
    def sign(self) -> Fragments:
        """
        小尾巴内容碎片列表
        """

        if not isinstance(self._sign, str):
            if self._sign is not None:
                self._sign = ''.join([_proto.text for _proto in self._sign if _proto.type == 0])
            else:
                self._sign = ''

        return self._sign

    @property
    def comments(self) -> List["Comment"]:
        """
        楼中楼列表
        """

        if not isinstance(self._comments, list):
            if self._comments is not None:
                self._comments = [Comment(_proto) for _proto in self._comments]
            else:
                self._comments = []

        return self._comments

    @property
    def floor(self) -> int:
        """
        楼层数
        """

        return self._floor

    @property
    def reply_num(self) -> int:
        """
        楼中楼数
        """

        return self._reply_num

    @property
    def agree(self) -> int:
        """
        点赞数
        """

        return self._agree

    @property
    def disagree(self) -> int:
        """
        点踩数
        """

        return self._disagree

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳
        """

        return self._create_time

    @property
    def is_thread_author(self) -> bool:
        """
        是否楼主
        """

        return self._is_thread_author


class Posts(_Containers[Post]):
    """
    回复列表

    Attributes:
        objs (list[Post]): 回复列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页

        forum (BasicForum): 所在吧信息
        thread (Thread): 所在主题帖信息

        has_fold (bool): 是否存在折叠楼层
    """

    __slots__ = [
        '_users',
        '_page',
        '_forum',
        '_thread',
        '_has_fold',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(Posts, self).__init__()

        if _raw_data:
            self._objs = _raw_data.post_list
            self._users = _raw_data.user_list

            self._page = _raw_data.page
            self._forum = _raw_data.forum
            self._thread = _raw_data.thread

            self._has_fold = bool(_raw_data.has_fold_comment)

        else:
            self._users = None

            self._page = None
            self._forum = None
            self._thread = None

            self._has_fold = False

    @property
    def objs(self) -> List[Post]:
        """
        回复列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:

                self._objs = [Post(_proto) for _proto in self._objs]
                users = {user.user_id: user for _proto in self._users if (user := UserInfo(_raw_data=_proto)).user_id}
                self._users = None

                for post in self._objs:

                    post._fid = self.forum.fid
                    post._fname = self.forum.fname
                    post._tid = self.thread.tid
                    post._user = users.get(post.author_id, None)
                    post._is_thread_author = self.thread.author_id == post.author_id

                    for comment in post.comments:
                        comment._fid = post.fid
                        comment._fname = post.fname
                        comment._tid = post.tid
                        comment._user = users.get(comment.author_id, None)

            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                self._page = Page(self._page)
            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more

    @property
    def forum(self) -> BasicForum:
        """
        所在吧信息
        """

        if not isinstance(self._forum, BasicForum):
            if self._forum is not None:
                self._forum = BasicForum(self._forum)
            else:
                self._forum = BasicForum()

        return self._forum

    @property
    def thread(self) -> Thread:
        """
        所在主题帖信息
        """

        if not isinstance(self._thread, Thread):
            if self._thread is not None:
                self._thread = Thread(self._thread)
                self._thread._fid = self.forum.fid

            else:
                self._thread = Thread()

        return self._thread

    @property
    def has_fold(self) -> bool:
        """
        是否存在折叠楼层
        """

        return self._has_fold


class Comment(_Container):
    """
    楼中楼信息

    Attributes:
        text (str): 文本内容
        contents (Fragments): 正文内容碎片列表

        fid (int): 所在吧id
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id
        reply_to_id (int): 被回复者的user_id

        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间
    """

    __slots__ = [
        '_contents',
        '_reply_to_id',
        '_agree',
        '_disagree',
        '_create_time',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(Comment, self).__init__()

        self._contents = None

        if _raw_data:
            self._contents = _raw_data.content

            self._pid = _raw_data.id
            self._user = UserInfo(_raw_data=_raw_data.author)
            self._author_id = _raw_data.author_id
            self._reply_to_id = None

            self._agree = _raw_data.agree.agree_num
            self._disagree = _raw_data.agree.disagree_num
            self._create_time = _raw_data.time

        else:
            self._contents = None

            self._reply_to_id = 0

            self._agree = 0
            self._disagree = 0
            self._create_time = 0

    def __eq__(self, obj: "Comment") -> bool:
        return super(Comment, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(Comment, self).__hash__()

    @property
    def text(self) -> str:
        """
        文本内容
        """

        if not self._text:
            self._text = self.contents.text
        return self._text

    @property
    def contents(self) -> Fragments:
        """
        正文内容碎片列表
        """

        if not isinstance(self._contents, Fragments):
            if self._contents is not None:

                self._contents = Fragments(self._contents)

                first_frag = self._contents[0]
                if (
                    len(self._contents) > 1
                    and isinstance(first_frag, FragText)
                    and first_frag.text == '回复 '
                    and (reply_to_id := self._contents[1]._raw_data.uid)
                ):
                    self._reply_to_id = reply_to_id
                    if isinstance(self._contents[1], FragAt):
                        self._contents._ats = self._contents._ats[1:]
                    self._contents._frags = self._contents._frags[2:]
                    if self._contents.texts:
                        first_text_frag = self._contents.texts[0]
                        first_text_frag._text = first_text_frag.text.removeprefix(' :')

            else:
                self._contents = Fragments()

        return self._contents

    @property
    def reply_to_id(self) -> int:
        """
        被回复者的user_id
        """

        if self._reply_to_id is None:
            _ = self.contents
            if not self._reply_to_id:
                self._reply_to_id = 0

        return self._reply_to_id

    @property
    def agree(self) -> int:
        """
        点赞数
        """

        return self._agree

    @property
    def disagree(self) -> int:
        """
        点踩数
        """

        return self._disagree

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳
        """

        return self._create_time


class Comments(_Containers[Comment]):
    """
    楼中楼列表

    Attributes:
        objs (list[Comment]): 楼中楼列表

        page (Page): 页信息

        forum (BasicForum): 所在吧信息
        thread (Thread): 所在主题帖信息
        post (Post): 所在回复信息
    """

    __slots__ = [
        '_page',
        '_forum',
        '_thread',
        '_post',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(Comments, self).__init__()

        if _raw_data:
            self._objs = _raw_data.subpost_list

            self._page = _raw_data.page
            self._forum = _raw_data.forum
            self._thread = _raw_data.thread
            self._post = _raw_data.post

        else:
            self._page = None
            self._forum = None
            self._thread = None
            self._post = None

    @property
    def objs(self) -> List[Comment]:
        """
        楼中楼列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:

                self._objs = [Comment(_proto) for _proto in self._objs]

                for comment in self._objs:
                    comment._fid = self.forum.fid
                    comment._fname = self.forum.fname
                    comment._tid = self.thread.tid

            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                self._page = Page(self._page)
            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more

    @property
    def forum(self) -> BasicForum:
        """
        所在吧信息
        """

        if not isinstance(self._forum, BasicForum):
            if self._forum is not None:
                self._forum = BasicForum(self._forum)
            else:
                self._forum = BasicForum()

        return self._forum

    @property
    def thread(self) -> Thread:
        """
        所在主题帖信息
        """

        if not isinstance(self._thread, Thread):
            if self._thread is not None:
                self._thread = Thread(self._thread)
                self._thread._fid = self.forum.fid

            else:
                self._thread = Thread()

        return self._thread

    @property
    def post(self) -> Post:
        """
        所在回复信息
        """

        if not isinstance(self._post, Post):
            if self._post is not None:
                self._post = Post(self._post)
                self._post._fid = self.forum.fid
                self._post._tid = self.thread.tid

            else:
                self._post = Post()

        return self._post


class Reply(_Container):
    """
    回复信息
    Attributes:
        text (str): 文本内容

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id
        post_pid (int): 楼层pid
        post_user (BasicUserInfo): 楼层用户信息
        thread_user (BasicUserInfo): 楼主用户信息

        is_floor (bool): 是否楼中楼
        create_time (int): 创建时间
    """

    __slots__ = [
        '_post_pid',
        '_post_user',
        '_thread_user',
        '_is_floor',
        '_create_time',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(Reply, self).__init__()

        if _raw_data:
            self._text = _raw_data.content

            self._fname = _raw_data.fname
            self._tid = _raw_data.thread_id
            self._pid = _raw_data.post_id
            self._user = _raw_data.replyer
            self._post_pid = _raw_data.quote_pid
            self._post_user = _raw_data.quote_user
            self._thread_user = _raw_data.thread_author_user

            self._is_floor = bool(_raw_data.is_floor)
            self._create_time = _raw_data.time

        else:
            self._text = ''

            self._post_pid = 0
            self._post_user = None
            self._thread_user = None

            self._is_floor = False
            self._create_time = 0

    def __eq__(self, obj: "Reply") -> bool:
        return super(Reply, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(Reply, self).__hash__()

    @property
    def text(self) -> str:
        """
        文本内容
        """

        return self._text

    @property
    def user(self) -> UserInfo:
        """
        发布者的用户信息
        """

        if not isinstance(self._user, UserInfo):
            if self._user is not None:
                self._user = UserInfo(_raw_data=self._user) if self._user.id else UserInfo()
            else:
                self._user = UserInfo()

        return self._user

    @property
    def post_pid(self) -> int:
        """
        楼层pid
        """

        return self._post_pid

    @property
    def post_user(self) -> BasicUserInfo:
        """
        楼层用户信息
        """

        if not isinstance(self._post_user, BasicUserInfo):
            if self._post_user is not None:
                self._post_user = BasicUserInfo(_raw_data=self._post_user) if self._post_user.id else BasicUserInfo()
            else:
                self._post_user = BasicUserInfo()

        return self._post_user

    @property
    def thread_user(self) -> BasicUserInfo:
        """
        楼主用户信息
        """

        if not isinstance(self._thread_user, BasicUserInfo):
            if self._thread_user is not None:
                self._thread_user = (
                    BasicUserInfo(_raw_data=self._thread_user) if self._thread_user.id else BasicUserInfo()
                )
            else:
                self._thread_user = BasicUserInfo()

        return self._thread_user

    @property
    def is_floor(self) -> bool:
        """
        是否楼中楼
        """

        return self._is_floor

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳
        """

        return self._create_time


class Replys(_Containers[Reply]):
    """
    收到回复列表

    Attributes:
        objs (list[Reply]): 收到回复列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(Replys, self).__init__()

        if _raw_data:
            self._objs = _raw_data.reply_list
            self._page = _raw_data.page

        else:
            self._page = None

    @property
    def objs(self) -> List[Reply]:
        """
        收到回复列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:
                self._objs = [Reply(_proto) for _proto in self._objs]
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                self._page = Page(self._page)
            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more


class At(_Container):
    """
    @信息

    Attributes:
        text (str): 文本内容

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id

        is_floor (bool): 是否楼中楼
        is_thread (bool): 是否主题帖

        create_time (int): 创建时间
    """

    __slots__ = [
        '_is_floor',
        '_is_thread',
        '_create_time',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(At, self).__init__()

        if _raw_data:
            self._text = _raw_data['content']

            self._fname = _raw_data['fname']
            self._tid = int(_raw_data['thread_id'])
            self._pid = int(_raw_data['post_id'])
            self._user = _raw_data['replyer']

            self._is_floor = bool(int(_raw_data['is_floor']))
            self._is_thread = bool(int(_raw_data['is_first_post']))
            self._create_time = int(_raw_data['time'])

        else:
            self._text = ''

            self._is_floor = False
            self._is_thread = False
            self._create_time = 0

    def __eq__(self, obj: "At") -> bool:
        return super(At, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(At, self).__hash__()

    @property
    def user(self) -> UserInfo:
        """
        发布者的用户信息
        """

        if not isinstance(self._user, UserInfo):
            if self._user is not None:
                user_proto = ParseDict(self._user, User_pb2.User(), ignore_unknown_fields=True)
                self._user = UserInfo(_raw_data=user_proto) if user_proto.id else UserInfo()
            else:
                self._user = UserInfo()

        return self._user

    @property
    def is_floor(self) -> bool:
        """
        是否楼中楼
        """

        return self._is_floor

    @property
    def is_thread(self) -> bool:
        """
        是否主题帖
        """

        return self._is_thread

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳
        """

        return self._create_time


class Ats(_Containers[At]):
    """
    @信息列表

    Attributes:
        objs (list[At]): @信息列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Ats, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data.get('at_list', None)
            self._page = _raw_data['page']

        else:
            self._raw_objs = None
            self._page = None

    @property
    def objs(self) -> List[At]:
        """
        @信息列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [At(_dict) for _dict in self._raw_objs]
                self._raw_objs = None
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                page_proto = ParseDict(self._page, Page_pb2.Page(), ignore_unknown_fields=True)
                self._page = Page(page_proto)
            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more


class Search(_Container):
    """
    搜索结果

    Attributes:
        text (str): 文本内容
        title (str): 标题

        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo): 发布者的用户信息

        is_floor (bool): 是否楼中楼

        create_time (int): 创建时间
    """

    __slots__ = [
        '_title',
        '_is_floor',
        '_create_time',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Search, self).__init__()

        if _raw_data:
            self._text = _raw_data['content']
            self._title = _raw_data['title']

            self._fname = _raw_data['fname']
            self._tid = int(_raw_data['tid'])
            self._pid = int(_raw_data['pid'])
            self._user = _raw_data['author']

            self._is_floor = bool(int(_raw_data['is_floor']))
            self._create_time = int(_raw_data['time'])

        else:
            self._text = ''
            self._title = ''

            self._is_floor = False
            self._create_time = 0

    def __eq__(self, obj: "Search") -> bool:
        return super(Search, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(Search, self).__hash__()

    @property
    def title(self) -> str:
        """
        帖子标题
        """

        return self._title

    @property
    def user(self) -> UserInfo:
        """
        发布者的用户信息
        """

        if not isinstance(self._user, UserInfo):
            if self._user is not None:
                self._user = UserInfo(_raw_data=ParseDict(self._user, User_pb2.User(), ignore_unknown_fields=True))
            else:
                self._user = UserInfo()

        return self._user

    @property
    def is_floor(self) -> bool:
        """
        是否楼中楼
        """

        return self._is_floor

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳
        """

        return self._create_time


class Searches(_Containers[Search]):
    """
    搜索结果列表

    Attributes:
        objs (list[Search]): 搜索结果列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Searches, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data.get('post_list', None)
            self._page = _raw_data['page']

        else:
            self._raw_objs = None
            self._page = None

    @property
    def objs(self) -> List[Search]:
        """
        搜索结果列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [Search(_dict) for _dict in self._raw_objs]
                self._raw_objs = None
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                page_proto = ParseDict(self._page, Page_pb2.Page(), ignore_unknown_fields=True)
                self._page = Page(page_proto)

            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more


class NewThread(_Container):
    """
    新版主题帖信息
    删除无用字段并适配新版字段名

    Attributes:
        text (str): 文本内容
        contents (Fragments): 正文内容碎片列表
        title (str): 标题内容

        fid (int): 所在吧id
        fname (str): 所在吧名
        tid (int): 主题帖tid
        pid (int): 首楼的回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id

        vote_info (VoteInfo): 投票内容
        view_num (int): 浏览量
        reply_num (int): 回复数
        share_num (int): 分享数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 10位时间戳 创建时间
    """

    __slots__ = [
        '_contents',
        '_title',
        '_vote_info',
        '_view_num',
        '_reply_num',
        '_share_num',
        '_agree',
        '_disagree',
        '_create_time',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(NewThread, self).__init__()

        if _raw_data:
            self._contents = _raw_data.first_post_content
            self._title = _raw_data.title

            self._fid = _raw_data.forum_id
            self._fname = _raw_data.forum_name
            self._tid = _raw_data.thread_id
            self._pid = _raw_data.post_id
            self._author_id = _raw_data.user_id

            self._vote_info = _raw_data.poll_info
            self._view_num = _raw_data.freq_num
            self._reply_num = _raw_data.reply_num
            self._share_num = _raw_data.share_num
            self._agree = _raw_data.agree.agree_num
            self._disagree = _raw_data.agree.disagree_num
            self._create_time = _raw_data.create_time

        else:
            self._contents = None
            self._title = ''

            self._vote_info = None
            self._view_num = 0
            self._reply_num = 0
            self._share_num = 0
            self._agree = 0
            self._disagree = 0
            self._create_time = 0

    def __eq__(self, obj: "NewThread") -> bool:
        return super(NewThread, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(NewThread, self).__hash__()

    @property
    def text(self) -> str:
        """
        文本内容

        Note:
            如果有标题的话还会在正文前附上标题
        """

        if self._text is None:

            if self.title:
                self._text = f"{self.title}\n{self.contents.text}"
            else:
                self._text = self.contents.text

        return self._text

    @property
    def contents(self) -> Fragments:
        """
        正文内容碎片列表
        """

        if not isinstance(self._contents, Fragments):
            if self._contents is not None:
                self._contents = Fragments(self._contents)
            else:
                self._contents = Fragments()

        return self._contents

    @property
    def title(self) -> str:
        """
        帖子标题
        """

        return self._title

    @property
    def vote_info(self) -> VoteInfo:
        """
        投票信息
        """

        if not isinstance(self._vote_info, VoteInfo):
            if self._vote_info is not None:
                self._vote_info = VoteInfo(self._vote_info) if self._vote_info.options else VoteInfo()
            else:
                self._vote_info = VoteInfo()

        return self._vote_info

    @property
    def view_num(self) -> int:
        """
        浏览量
        """

        return self._view_num

    @property
    def reply_num(self) -> int:
        """
        回复数
        """

        return self._reply_num

    @property
    def share_num(self) -> int:
        """
        分享数
        """

        return self._share_num

    @property
    def agree(self) -> int:
        """
        点赞数
        """

        return self._agree

    @property
    def disagree(self) -> int:
        """
        点踩数
        """

        return self._disagree

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳
        """

        return self._create_time


class UserPost(_Container):
    """
    用户历史回复信息

    Attributes:
        text (str): 文本内容
        contents (Fragments): 正文内容碎片列表

        fid (int): 所在吧id
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id

        create_time (int): 创建时间
    """

    __slots__ = [
        '_contents',
        '_create_time',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(UserPost, self).__init__()

        if _raw_data:
            self._contents = _raw_data.post_content
            self._pid = _raw_data.post_id
            self._create_time = _raw_data.create_time

        else:
            self._contents = None
            self._create_time = 0

    def __eq__(self, obj: "UserPost") -> bool:
        return super(UserPost, self).__eq__(obj)

    def __hash__(self) -> int:
        return super(UserPost, self).__hash__()

    @property
    def text(self) -> str:
        """
        文本内容
        """

        if self._text is None:
            self._text = self.contents.text
        return self._text

    @property
    def contents(self) -> Fragments:
        """
        正文内容碎片列表
        """

        if not isinstance(self._contents, Fragments):
            if self._contents is not None:
                self._contents = Fragments(self._contents)
            else:
                self._contents = Fragments()

        return self._contents

    @property
    def create_time(self) -> int:
        """
        创建时间

        Note:
            10位时间戳
        """

        return self._create_time


class UserPosts(_Containers[UserPost]):
    """
    用户历史回复信息列表

    Attributes:
        objs (list[UserPost]): 用户历史回复信息列表
        fid (int): 所在吧id
        tid (int): 所在主题帖id
    """

    __slots__ = [
        '_fid',
        '_tid',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(UserPosts, self).__init__()

        if _raw_data:
            self._objs = _raw_data.content
            self._fid = _raw_data.forum_id
            self._tid = _raw_data.thread_id

        else:
            self._fid = 0
            self._tid = 0

    @property
    def objs(self) -> List[UserPost]:
        """
        用户历史回复信息列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:

                self._objs = [UserPost(_proto) for _proto in self._objs]

                for post in self._objs:
                    post._fid = self.fid
                    post._tid = self.tid

            else:
                self._objs = []

        return self._objs

    @property
    def fid(self) -> int:
        """
        所在吧id
        """

        return self._fid

    @property
    def tid(self) -> int:
        """
        所在主题帖id
        """

        return self._tid


class RankUser(object):
    """
    等级排行榜用户信息

    Attributes:
        user_name (str): 用户名
        level (int): 等级
        exp (int): 经验值
        is_vip (bool): 是否vip
    """

    __slots__ = [
        '_user_name',
        '_level',
        '_exp',
        '_is_vip',
    ]

    def __init__(self, _raw_data: Optional[bs4.element.Tag] = None) -> None:
        super(RankUser, self).__init__()

        if _raw_data:
            user_name_item = _raw_data.td.next_sibling
            self._user_name = user_name_item.text
            self._is_vip = 'drl_item_vip' in user_name_item.div['class']
            level_item = user_name_item.next_sibling
            # e.g. get level 16 from "bg_lv16" by slicing [5:]
            self._level = int(level_item.div['class'][0][5:])
            exp_item = level_item.next_sibling
            self._exp = int(exp_item.text)

        else:
            self._user_name = ''
            self._level = 0
            self._exp = 0
            self._is_vip = False

    def __repr__(self) -> str:
        return str(
            {
                'user_name': self.user_name,
                'level': self.level,
                'exp': self.exp,
                'is_vip': self.is_vip,
            }
        )

    @property
    def user_name(self) -> str:
        """
        用户名
        """

        return self._user_name

    @property
    def level(self) -> int:
        """
        等级
        """

        return self._level

    @property
    def exp(self) -> int:
        """
        经验值
        """

        return self._exp

    @property
    def is_vip(self) -> bool:
        """
        是否vip
        """

        return self._is_vip


class RankUsers(_Containers[RankUser]):
    """
    等级排行榜用户列表

    Attributes:
        objs (list[RankUser]): 等级排行榜用户列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[bs4.BeautifulSoup] = None) -> None:
        super(RankUsers, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data('tr', class_=['drl_list_item', 'drl_list_item_self'])

            page_item = _raw_data.find('ul', class_='p_rank_pager')
            self._page = json.loads(page_item['data-field'])

        else:
            self._raw_objs = None
            self._page = None

    @property
    def objs(self) -> List[RankUser]:
        """
        等级排行榜用户列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [RankUser(_tag) for _tag in self._raw_objs]
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                self._page['current_page'] = self._page.pop('cur_page')
                self._page['total_count'] = self._page.pop('total_num')
                page_proto = ParseDict(self._page, Page_pb2.Page(), ignore_unknown_fields=True)
                self._page = Page(page_proto)

            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more


class MemberUser(object):
    """
    最新关注用户信息

    Attributes:
        user_name (str): 用户名
        portrait (str): portrait
        level (int): 等级
    """

    __slots__ = [
        '_user_name',
        '_portrait',
        '_level',
    ]

    def __init__(self, _raw_data: Optional[bs4.element.Tag] = None) -> None:
        super(MemberUser, self).__init__()

        if _raw_data:
            user_item = _raw_data.a
            self._user_name = user_item['title']
            self._portrait = user_item['href'][14:]
            level_item = _raw_data.span
            self._level = int(level_item['class'][1][12:])

        else:
            self._user_name = ''
            self._portrait = ''
            self._level = 0

    def __repr__(self) -> str:
        return str(
            {
                'user_name': self.user_name,
                'portrait': self.portrait,
                'level': self.level,
            }
        )

    @property
    def user_name(self) -> str:
        """
        用户名

        Note:
            具有唯一性
            请注意与用户昵称区分
        """

        return self._user_name

    @property
    def portrait(self) -> str:
        """
        用户portrait

        Note:
            具有唯一性
            可以用于获取用户头像
        """

        return self._portrait

    @property
    def level(self) -> int:
        """
        等级
        """

        return self._level


class MemberUsers(_Containers[MemberUser]):
    """
    最新关注用户列表

    Attributes:
        objs (list[MemberUser]): 最新关注用户列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[bs4.BeautifulSoup] = None) -> None:
        super(MemberUsers, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data('div', class_='name_wrap')
            self._page = _raw_data.find('div', class_='tbui_pagination').find('li', class_='active')

        else:
            self._raw_objs = None
            self._page = None

        self._page = None

    @property
    def objs(self) -> List[MemberUser]:
        """
        最新关注用户列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [MemberUser(_raw_data=_tag) for _tag in self._raw_objs]
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                page_proto = Page_pb2.Page()
                page_proto.current_page = int(self._page.text)
                total_page_item = self._page.parent.next_sibling
                page_proto.total_page = int(total_page_item.text[1:-1])
                self._page = Page(page_proto)

            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more


class SquareForum(BasicForum):
    """
    吧广场贴吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        member_num (int): 吧会员数
        thread_num (int): 主题帖数

        is_followed (bool): 是否已关注
        level (int): 等级
        exp (int): 经验值
    """

    __slots__ = [
        '_member_num',
        '_thread_num',
        '_is_followed',
        '_level',
        '_exp',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(SquareForum, self).__init__(_raw_data)

        self._level = 0
        self._exp = 0

        if _raw_data:
            self._member_num = _raw_data.member_count
            self._thread_num = _raw_data.thread_num

            self._is_followed = bool(_raw_data.is_like)

        else:
            self._member_num = 0
            self._thread_num = 0

            self._is_followed = False

    @property
    def member_num(self) -> int:
        """
        吧会员数
        """

        return self._member_num

    @property
    def thread_num(self) -> int:
        """
        主题帖数
        """

        return self._thread_num

    @property
    def is_followed(self) -> bool:
        """
        是否已关注
        """

        return self._is_followed

    @property
    def level(self) -> int:
        """
        等级
        """

        return self._level

    @property
    def exp(self) -> int:
        """
        经验值
        """

        return self._exp


class SquareForums(_Containers[SquareForum]):
    """
    吧广场列表

    Attributes:
        objs (list[SquareForum]): 吧广场列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def __init__(self, _raw_data: Optional[Iterable[_TypeMessage]] = None) -> None:
        super(SquareForums, self).__init__()

        if _raw_data:
            self._objs = _raw_data.forum_info
            self._page = _raw_data.page

        else:
            self._page = None

    @property
    def objs(self) -> List[SquareForum]:
        """
        吧广场列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:
                self._objs = [SquareForum(_proto) for _proto in self._objs]
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                self._page = Page(self._page)
            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more


class Forum(BasicForum):
    """
    贴吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        member_num (int): 吧会员数
        thread_num (int): 主题帖数
        post_num (int): 总发帖数

        level (int): 等级
        exp (int): 经验值
    """

    __slots__ = [
        '_member_num',
        '_thread_num',
        '_post_num',
        '_level',
        '_exp',
    ]

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(Forum, self).__init__(_raw_data)

        self._level = 0
        self._exp = 0

        if _raw_data:
            self._member_num = _raw_data.member_count
            self._thread_num = _raw_data.thread_num
            self._post_num = _raw_data.post_num

        else:
            self._member_num = 0
            self._thread_num = 0
            self._post_num = 0

    @property
    def member_num(self) -> int:
        """
        吧会员数
        """

        return self._member_num

    @property
    def thread_num(self) -> int:
        """
        主题帖数
        """

        return self._thread_num

    @property
    def post_num(self) -> int:
        """
        总发帖数
        """

        return self._post_num

    @property
    def level(self) -> int:
        """
        等级
        """

        return self._level

    @property
    def exp(self) -> int:
        """
        经验值
        """

        return self._exp


class FollowForums(_Containers[Forum]):
    """
    用户关注贴吧列表

    Attributes:
        objs (list[Forum]): 用户关注贴吧列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_has_more']

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(FollowForums, self).__init__()

        if _raw_data:
            self._objs = _raw_data.get('forum_list', {})
            self._has_more = bool(int(_raw_data.get('has_more', 0)))

        else:
            self._has_more = False

    @property
    def objs(self) -> List[Forum]:
        """
        用户关注贴吧列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:

                def parse_dict(forum_dict: Dict[str, int]) -> Forum:
                    forum = Forum()
                    forum._fname = forum_dict['name']
                    forum._fid = int(forum_dict['id'])
                    forum._level = int(forum_dict['level_id'])
                    forum._exp = int(forum_dict['cur_score'])
                    return forum

                forum_dicts: List[dict] = self._objs.get('non-gconforum', [])
                forum_dicts += self._objs.get('gconforum', [])
                self._objs = [parse_dict(_dict) for _dict in forum_dicts]

            else:
                self._objs = []

        return self._objs

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more


class RecomThreads(_Containers[Thread]):
    """
    大吧主推荐帖列表

    Attributes:
        objs (list[Thread]): 大吧主推荐帖列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_has_more',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(RecomThreads, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data['recom_thread_list']
            self._has_more = bool(int(_raw_data['is_has_more']))

        else:
            self._raw_objs = None
            self._has_more = False

    @property
    def objs(self) -> List[Thread]:
        """
        大吧主推荐帖列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [
                    Thread(ParseDict(_dict['thread_list'], ThreadInfo_pb2.ThreadInfo(), ignore_unknown_fields=True))
                    for _dict in self._raw_objs
                ]
                self._raw_objs = None
            else:
                self._objs = []

        return self._objs

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more


class Recover(object):
    """
    待恢复帖子信息

    Attributes:
        tid (int): 所在主题帖id
        pid (int): 回复id
        is_hide (bool): 是否为屏蔽
    """

    __slots__ = [
        '_tid',
        '_pid',
        '_is_hide',
    ]

    def __init__(self, _raw_data: Optional[bs4.element.Tag] = None) -> None:
        super(Recover, self).__init__()

        if _raw_data:
            self._tid = int(_raw_data['attr-tid'])
            self._pid = int(_raw_data['attr-pid'])
            self._is_hide = bool(int(_raw_data['attr-isfrsmask']))

        else:
            self._tid = 0
            self._pid = 0
            self._is_hide = False

    def __repr__(self) -> str:
        return str(
            {
                'tid': self.tid,
                'pid': self.pid,
                'is_hide': self.is_hide,
            }
        )

    @property
    def tid(self) -> int:
        """
        所在主题帖id
        """

        return self._tid

    @property
    def pid(self) -> int:
        """
        回复id
        """

        return self._pid

    @property
    def is_hide(self) -> bool:
        """
        是否为屏蔽
        """

        return self._is_hide


class Recovers(_Containers[Recover]):
    """
    待恢复帖子列表

    Attributes:
        objs (list[Recover]): 待恢复帖子列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_has_more']

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Recovers, self).__init__()

        if _raw_data:
            self._objs = _raw_data['data']['content']
            self._has_more = _raw_data['data']['page']['have_next']

        else:
            self._has_more = False

    @property
    def objs(self) -> List[Recover]:
        """
        待恢复帖子列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:
                soup = bs4.BeautifulSoup(self._objs, 'lxml')
                self._objs = [Recover(_tag) for _tag in soup('a', class_='recover_list_item_btn')]

            else:
                self._objs = []

        return self._objs

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more


class BlacklistUsers(_Containers[BasicUserInfo]):
    """
    黑名单用户列表

    Attributes:
        objs (list[BasicUserInfo]): 黑名单用户列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[bs4.BeautifulSoup] = None) -> None:
        super(BlacklistUsers, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data('td', class_='left_cell')
            self._page = _raw_data.find('div', class_='tbui_pagination').find('li', class_='active')

        else:
            self._raw_objs = None
            self._page = None

    @property
    def objs(self) -> List[BasicUserInfo]:
        """
        黑名单用户列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:

                def parse_tag(tag):
                    user_info_item = tag.previous_sibling.input
                    user = BasicUserInfo()
                    user.user_name = user_info_item['data-user-name']
                    user.user_id = int(user_info_item['data-user-id'])
                    user.portrait = tag.a['href'][14:]
                    return user

                self._objs = [parse_tag(_tag) for _tag in self._raw_objs]

            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                page_proto = Page_pb2.Page()
                page_proto.current_page = int(self._page.text)
                total_page_item = self._page.parent.next_sibling
                page_proto.total_page = int(total_page_item.text[1:-1])
                self._page = Page(page_proto)

            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more


class Appeal(object):
    """
    申诉请求信息

    Attributes:
        aid (int): 申诉请求id
    """

    __slots__ = ['_aid']

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Appeal, self).__init__()

        if _raw_data:
            self._aid = int(_raw_data['appeal_id'])

        else:
            self._aid = 0

    def __repr__(self) -> str:
        return str({'aid': self.aid})

    @property
    def aid(self) -> int:
        """
        申诉请求id
        """

        return self._aid


class Appeals(_Containers[Appeal]):
    """
    申诉请求列表

    Attributes:
        objs (list[Appeal]): 申诉请求列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_has_more',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Appeals, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data['data'].get('appeal_list', [])
            self._has_more = _raw_data['data'].get('has_more', False)

        else:
            self._raw_objs = None
            self._has_more = False

    @property
    def objs(self) -> List[Appeal]:
        """
        申诉请求列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [Appeal(_dict) for _dict in self._raw_objs]
                self._raw_objs = None
            else:
                self._objs = []

        return self._objs

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more


class Fans(_Containers[UserInfo]):
    """
    粉丝列表

    Attributes:
        objs (list[UserInfo]): 粉丝列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Fans, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data['user_list']
            self._page = _raw_data['page']

        else:
            self._raw_objs = None
            self._page = None

    @property
    def objs(self) -> List[UserInfo]:
        """
        粉丝列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [
                    UserInfo(_raw_data=ParseDict(_dict, User_pb2.User(), ignore_unknown_fields=True))
                    for _dict in self._raw_objs
                ]
                self._raw_objs = None
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                self._page = Page(ParseDict(self._page, Page_pb2.Page(), ignore_unknown_fields=True))
            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more


class Follows(_Containers[UserInfo]):
    """
    关注列表

    Attributes:
        objs (list[UserInfo]): 关注列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_has_more',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(Follows, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data['follow_list']
            self._has_more = bool(int(_raw_data['has_more']))

        else:
            self._raw_objs = None
            self._has_more = False

    @property
    def objs(self) -> List[UserInfo]:
        """
        关注列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [
                    UserInfo(_raw_data=ParseDict(_dict, User_pb2.User(), ignore_unknown_fields=True))
                    for _dict in self._raw_objs
                ]
                self._raw_objs = None
            else:
                self._objs = []

        return self._objs

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more


class SelfFollowForums(_Containers[Forum]):
    """
    本账号关注贴吧列表

    Attributes:
        objs (list[Forum]): 本账号关注贴吧列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, _raw_data: Optional[dict] = None) -> None:
        super(SelfFollowForums, self).__init__()

        self._objs = None

        if _raw_data:
            self._raw_objs = _raw_data['data']['like_forum']['list']
            self._page = _raw_data['data']['like_forum']['page']

        else:
            self._raw_objs = None
            self._page = None

    @property
    def objs(self) -> List[Forum]:
        """
        本账号关注贴吧列表
        """

        if not isinstance(self._objs, list):
            if self._raw_objs is not None:
                self._objs = [
                    Forum(
                        ParseDict(
                            _dict,
                            GetDislikeListResIdl_pb2.GetDislikeListResIdl.DataRes.ForumList(),
                            ignore_unknown_fields=True,
                        )
                    )
                    for _dict in self._raw_objs
                ]
                self._raw_objs = None
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        """
        页信息
        """

        if not isinstance(self._page, Page):
            if self._page is not None:
                self._page['current_page'] = self._page.pop('cur_page')
                self._page = Page(ParseDict(self._page, Page_pb2.Page(), ignore_unknown_fields=True))

            else:
                self._page = Page()

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self.page.has_more


class DislikeForums(_Containers[Forum]):
    """
    首页推荐屏蔽的贴吧列表

    Attributes:
        objs (list[Forum]): 首页推荐屏蔽的贴吧列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_has_more']

    def __init__(self, _raw_data: Optional[_TypeMessage] = None) -> None:
        super(DislikeForums, self).__init__()

        if _raw_data:
            self._objs = _raw_data.forum_list
            self._has_more = bool(_raw_data.has_more)

        else:
            self._has_more = False

    @property
    def objs(self) -> List[Forum]:
        """
        首页推荐屏蔽的贴吧列表
        """

        if not isinstance(self._objs, list):
            if self._objs is not None:
                self._objs = [Forum(_proto) for _proto in self._objs]
            else:
                self._objs = []

        return self._objs

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more
