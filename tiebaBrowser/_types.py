# -*- coding:utf-8 -*-
__all__ = [
    'BasicUserInfo',
    'UserInfo',
    'Thread',
    'Post',
    'Comment',
    'At',
    'Reply',
    'Search',
    'Threads',
    'Posts',
    'Comments',
    'Ats',
    'Replys',
    'Searches',
    'Fragments',
    'NewThread',
    'UserPost',
    'UserPosts',
]

import json
from typing import Dict, Generic, Iterable, Iterator, List, Optional, TypeVar, Union

from google.protobuf.json_format import ParseDict

from ._logger import get_logger
from .tieba_proto import (
    FrsPageResIdl_pb2,
    NewThreadInfo_pb2,
    Page_pb2,
    PbContent_pb2,
    PbFloorResIdl_pb2,
    PbPageResIdl_pb2,
    PollInfo_pb2,
    Post_pb2,
    ReplyMeResIdl_pb2,
    SimpleForum_pb2,
    SubPostList_pb2,
    ThreadInfo_pb2,
    User_pb2,
    UserPostResIdl_pb2,
)

LOG = get_logger()


def _json_decoder_hook(_dict):
    for key, value in _dict.items():
        if not value:
            _dict[key] = None
    return _dict


JSON_DECODER = json.JSONDecoder(object_hook=_json_decoder_hook)


class _DataWrapper(object):
    """
    raw_data包装器

    Fields:
        _raw_data (Any): 原始raw_data数据
    """

    __slots__ = ['_raw_data']

    def __init__(self, _raw_data) -> None:
        self._raw_data = _raw_data


class BasicUserInfo(_DataWrapper):
    """
    基本用户属性

    Args:
        _id (str | int | None): 用于快速构造UserInfo的自适应参数 输入用户名/portrait/user_id
        _raw_data (User_pb2.User)

    Fields:
        user_id (int): 贴吧旧版user_id
        user_name (str): 发帖用户名
        portrait (str): 用户头像portrait值
        nick_name (str): 发帖人昵称
    """

    __slots__ = ['user_id', 'user_name', '_portrait', '_nick_name']

    def __init__(self, _id: Union[str, int, None] = None, _raw_data: Optional[User_pb2.User] = None) -> None:
        super(BasicUserInfo, self).__init__(_raw_data)

        if _raw_data:
            self.user_id: int = _raw_data.id
            self.user_name: str = _raw_data.name
            self.portrait = _raw_data.portrait
            self.nick_name = _raw_data.name_show

        else:
            self.user_id = 0
            self.user_name = ''
            self._portrait = ''
            self._nick_name = ''

            if _id:
                if self.is_user_id(_id):
                    self.user_id = _id
                else:
                    self.portrait = _id
                    if not self.portrait:
                        self.user_name = _id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [user_id:{self.user_id} / user_name:{self.user_name} / portrait:{self._portrait} / nick_name:{self._nick_name}]"

    def __eq__(self, obj: "BasicUserInfo") -> bool:
        return self.user_id == obj.user_id and self.user_name == obj.user_name and self._portrait == obj.portrait

    def __hash__(self) -> int:
        return self.user_id

    def __int__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @staticmethod
    def is_portrait(portrait: str) -> bool:
        return portrait.startswith('tb.')

    @staticmethod
    def is_user_id(user_id: int) -> bool:
        return isinstance(user_id, int)

    @property
    def portrait(self) -> str:
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
    def nick_name(self) -> str:
        return self._nick_name

    @nick_name.setter
    def nick_name(self, new_nick_name: str) -> None:

        if self.user_name != new_nick_name:
            self._nick_name = new_nick_name
        else:
            self._nick_name = ''

    @property
    def show_name(self) -> str:
        return self.nick_name if self.nick_name else self.user_name

    @property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        else:
            return f"{self._nick_name} / {self._portrait}"


class UserInfo(BasicUserInfo):
    """
    用户属性

    Args:
        _id (Union[str, int, None]): 用于快速构造UserInfo的自适应参数 输入用户名或portrait或user_id
        _raw_data (User_pb2.User)

    Fields:
        user_id (int): 贴吧旧版user_id
        user_name (str): 发帖用户名
        portrait (str): 用户头像portrait值
        nick_name (str): 发帖人昵称

        level (int): 等级
        gender (int): 性别 (1男2女0未知)
        is_vip (bool): 是否vip
        is_god (bool): 是否大神
        priv_like (int): 是否公开关注贴吧 (1完全可见2好友可见3完全隐藏)
        priv_reply (int): 帖子评论权限 (1所有人5我的粉丝6我的关注)
    """

    __slots__ = ['level', 'gender', 'is_vip', 'is_god', 'priv_like', 'priv_reply']

    def __init__(self, _id: Union[str, int, None] = None, _raw_data: Optional[User_pb2.User] = None) -> None:
        super(UserInfo, self).__init__(_id, _raw_data)

        if _raw_data:
            self.level: int = _raw_data.level_id
            self.gender: int = _raw_data.gender or _raw_data.sex
            self.is_vip: bool = True if _raw_data.new_tshow_icon else bool(_raw_data.vipInfo.v_status)
            self.is_god: bool = bool(_raw_data.new_god_data.status)
            priv_raw_data = _raw_data.priv_sets
            self.priv_like: int = priv_raw_data.like
            self.priv_reply: int = priv_raw_data.reply

        else:
            self.level = 0
            self.gender = 0
            self.is_vip = False
            self.is_god = False
            self.priv_like = 3
            self.priv_reply = 1

    def __eq__(self, obj: "UserInfo") -> bool:
        return super(UserInfo, self).__eq__(obj)


class _Fragment(_DataWrapper):
    """
    内容碎片基类
    """

    __slots__ = []

    def __init__(self, _raw_data: Optional[PbContent_pb2.PbContent] = None) -> None:
        super(_Fragment, self).__init__(_raw_data)

    def __bool__(self) -> bool:
        return bool(self._raw_data)


class FragmentUnknown(_Fragment):
    """
    未知碎片
    """

    __slots__ = []


class FragText(_Fragment):
    """
    纯文本碎片

    Fields:
        text (str): 文本内容
    """

    __slots__ = ['text']

    def __init__(self, _raw_data: PbContent_pb2.PbContent) -> None:
        super(FragText, self).__init__(_raw_data)

        self.text: str = self._raw_data.text

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [text:{self.text}]"


class FragEmoji(_Fragment):
    """
    表情碎片

    Fields:
        desc (str): 表情描述
    """

    __slots__ = ['desc']

    def __init__(self, _raw_data: PbContent_pb2.PbContent) -> None:
        super(FragEmoji, self).__init__(_raw_data)

        self.desc: str = self._raw_data.c

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [desc:{self.desc}]"


class FragImage(_Fragment):
    """
    图像碎片

    Fields:
        src (str): 压缩图像cdn_url
        big_src (str): 大图cdn_url
        origin_src (str): 图像源url
    """

    __slots__ = ['src', 'big_src', 'origin_src', 'origin_size', '_hash', '_show_width', '_show_height']

    def __init__(self, _raw_data: PbContent_pb2.PbContent) -> None:
        super(FragImage, self).__init__(_raw_data)

        self.src: str = self._raw_data.cdn_src or self._raw_data.src
        self.big_src: str = self._raw_data.big_cdn_src or self._raw_data.big_src
        self.origin_src: str = self._raw_data.origin_src
        self.origin_size: int = self._raw_data.origin_size
        self._hash: str = None
        self._show_width: int = None
        self._show_height: int = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [src:{self.src}]"

    @property
    def hash(self) -> str:

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

        show_width, _, show_height = self._raw_data.bsize.partition(',')

        if show_width and show_height:
            self._show_width = int(show_width)
            self._show_height = int(show_height)

        else:
            self._show_width = 0
            self._show_height = 0

    @property
    def show_width(self) -> int:
        if self._show_width is None:
            self._init_wh()
        return self._show_width

    @property
    def show_height(self) -> int:
        if self._show_height is None:
            self._init_wh()
        return self._show_height


class FragAt(FragText):
    """
    @碎片

    Fields:
        text (str): 被@用户的昵称
        user_id (int): 被@用户的user_id
    """

    __slots__ = ['text', 'user_id']

    def __init__(self, _raw_data: PbContent_pb2.PbContent) -> None:
        super(FragAt, self).__init__(_raw_data)

        self.text: str = self._raw_data.text + " "
        self.user_id: int = self._raw_data.uid

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [text:{self.text} / user_id:{self.user_id}]"


class FragLink(FragText):
    """
    链接碎片

    Fields:
        text (str): 链接标题
        link (str): 链接url
        is_external (bool): 是否外部链接
    """

    __slots__ = ['text', 'link', '_is_external']

    external_perfix = "http://tieba.baidu.com/mo/q/checkurl"

    def __init__(self, _raw_data: PbContent_pb2.PbContent) -> None:
        super(FragLink, self).__init__(_raw_data)

        self.text: str = self._raw_data.text
        self.link: str = self._raw_data.link
        self._is_external = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [text:{self.text} / link:{self.link}]"

    @property
    def is_external(self) -> bool:
        if self._is_external is None:
            self._is_external = self.link.startswith(self.external_perfix)
        return self._is_external


class FragVoice(_Fragment):
    """
    音频碎片

    Fields:
        voice_md5 (str): 声音md5
    """

    __slots__ = ['voice_md5']

    def __init__(self, _raw_data: Optional[PbContent_pb2.PbContent] = None) -> None:
        super(FragVoice, self).__init__(_raw_data)
        self.voice_md5: str = self._raw_data.voice_md5 if _raw_data else ''

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [voice_md5:{self.voice_md5}]"


class FragTiebaPlus(FragText):
    """
    贴吧+碎片

    Fields:
        text (str): 描述
        url (str): 跳转链接
    """

    __slots__ = ['text', 'url']

    def __init__(self, _raw_data: PbContent_pb2.PbContent) -> None:
        super(FragTiebaPlus, self).__init__(_raw_data)

        self.text: str = self._raw_data.tiebaplus_info.desc
        self.url: str = self._raw_data.tiebaplus_info.jump_url

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [text:{self.text} / url:{self.url}]"


class FragItem(FragText):
    """
    item碎片

    Fields:
        text (str): item名称
        item_name (str): item名称
    """

    __slots__ = ['text', 'item_name']

    def __init__(self, _raw_data: PbContent_pb2.PbContent) -> None:
        super(FragItem, self).__init__(_raw_data)

        self.text: str = self._raw_data.item.item_name
        self.item_name: str = self._raw_data.item.item_name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [item_name:{self.item_name}]"


class Fragments(object):
    """
    内容碎片列表

    Fields:
        _frags (list[_Fragment]): 所有碎片的混合列表

        text (str): 文本内容

        texts (list[FragText]): 纯文本碎片列表
        emojis (list[FragEmoji]): 表情碎片列表
        imgs (list[FragImage]): 图像碎片列表
        ats (list[FragAt]): @碎片列表
        links (list[FragLink]): 链接碎片列表
        voice (FragVoice): 音频碎片
        tiebapluses (list[FragTiebaPlus]): 贴吧+碎片列表
    """

    __slots__ = ['_frags', '_text', '_texts', '_emojis', '_imgs', '_ats', '_links', '_voice', '_tiebapluses']

    def __init__(self, _raw_datas: Optional[Iterable[PbContent_pb2.PbContent]] = None) -> None:
        def _init_by_type(_raw_data) -> _Fragment:
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
                LOG.warning(f"Unknown fragment type:{_raw_data.type}")

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
            self._frags: List[_Fragment] = [_init_by_type(frag_proto) for frag_proto in _raw_datas]
        else:
            self._frags = []

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = ''.join([frag.text for frag in self.texts])
        return self._text

    @property
    def texts(self) -> List[FragText]:
        if self._texts is None:
            self._texts = [frag for frag in self._frags if isinstance(frag, FragText)]

        return self._texts

    @property
    def emojis(self) -> List[FragEmoji]:
        return self._emojis

    @property
    def imgs(self) -> List[FragImage]:
        return self._imgs

    @property
    def ats(self) -> List[FragAt]:
        return self._ats

    @property
    def voice(self) -> FragVoice:
        if self._voice is None:
            self._voice = FragVoice()
        return self._voice

    @property
    def links(self) -> List[FragLink]:
        return self._links

    @property
    def tiebapluses(self) -> List[FragTiebaPlus]:
        return self._tiebapluses

    def __iter__(self) -> Iterator[_Fragment]:
        return iter(self._frags)

    def __getitem__(self, idx: int) -> Union[_Fragment, List[_Fragment]]:
        return self._frags[idx]

    def __setitem__(self, idx, val) -> None:
        raise NotImplementedError

    def __delitem__(self, idx) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        return len(self._frags)

    def __bool__(self) -> bool:
        return bool(self._frags)


class Forum(_DataWrapper):
    """
    吧信息

    Fields:
        fid (int): 吧id
        name (str): 吧名
    """

    __slots__ = ['_raw_data', 'fid', 'name']

    def __init__(
        self,
        _raw_data: Union[SimpleForum_pb2.SimpleForum, FrsPageResIdl_pb2.FrsPageResIdl.DataRes.ForumInfo, None] = None,
    ) -> None:
        super(Forum, self).__init__(_raw_data)

        if _raw_data:
            self.fid: int = _raw_data.id
            self.name: str = _raw_data.name

        else:
            self.fid = 0
            self.name = ''

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [fid:{self.fid} / name:{self.name}]"


class Page(_DataWrapper):
    """
    页信息

    Fields:
        page_size (int): 页大小
        current_page (int): 当前页码
        total_page (int): 总页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = ['_raw_data', 'page_size', 'current_page', 'total_page', 'total_count', 'has_more', 'has_prev']

    def __init__(self, _raw_data: Optional[Page_pb2.Page] = None) -> None:
        super(Page, self).__init__(_raw_data)

        if _raw_data:
            self.page_size: int = _raw_data.page_size
            self.current_page: int = _raw_data.current_page
            self.total_page: int = _raw_data.total_page

            if self.current_page and self.total_page:
                self.has_more = self.current_page < self.total_page
                self.has_prev = self.current_page > self.total_page
            else:
                self.has_more = bool(_raw_data.has_more)
                self.has_prev = bool(_raw_data.has_prev)

            self.total_count: int = _raw_data.total_count

        else:
            self.page_size = 0
            self.current_page = 0
            self.total_page = 0

            self.has_more = False
            self.has_prev = False

            self.total_count = 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [current_page:{self.current_page} / total_page:{self.total_page} / has_more:{self.has_more} / has_prev:{self.has_prev}]"


class _BasicContainer(_DataWrapper):
    """
    基本的内容容器

    Fields:
        text (str): 文本内容

        fid (int): 所在吧id
        tid (int): 主题帖tid
        pid (int): 回复pid
        user (UserInfo): 发布者信息
        author_id (int): 发布者user_id
    """

    __slots__ = ['_text', 'fid', 'tid', 'pid', '_user', '_author_id']

    def __init__(self, _raw_data) -> None:
        super(_BasicContainer, self).__init__(_raw_data)

        self._text: str = None
        self.fid: int = 0
        self.tid: int = 0
        self.pid: int = 0
        self._user: UserInfo = None
        self._author_id: int = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} [tid:{self.tid} / pid:{self.pid} / user:{self.user.log_name} / text:{self.text}]"

    @property
    def text(self) -> str:
        if self._text is None:
            raise NotImplementedError
        return self._text

    @property
    def user(self) -> UserInfo:
        if self._user is None:
            self._user = UserInfo()
        return self._user

    @property
    def author_id(self) -> int:
        if not self._author_id:
            self._author_id = self.user.user_id
        return self._author_id


_TContainer = TypeVar('_TContainer', bound=_BasicContainer)


class _Containers(_DataWrapper, Generic[_TContainer]):
    """
    内容列表的泛型基类
    约定取内容的通用接口

    Fields:
        _objs (list[TContainer]): 内容列表
        page (Page): 页码信息
    """

    __slots__ = ['_objs', '_page']

    def __init__(self, _raw_data) -> None:
        _DataWrapper.__init__(self, _raw_data)

        self._objs: List[_TContainer] = None
        self._page: Page = None

    @property
    def objs(self) -> List[_TContainer]:
        raise NotImplementedError

    def __iter__(self) -> Iterator[_TContainer]:
        return iter(self.objs)

    def __getitem__(self, idx) -> Union[_TContainer, List[_TContainer]]:
        return self.objs[idx]

    def __setitem__(self, idx, val):
        raise NotImplementedError

    def __delitem__(self, idx):
        raise NotImplementedError

    def __len__(self) -> int:
        return len(self.objs)

    def __bool__(self) -> bool:
        return bool(self.objs)

    @property
    def page(self) -> Page:

        if self._page is None:

            if self._raw_data:
                self._page = Page(self._raw_data.page)
            else:
                self._page = Page()

        return self._page


class VoteInfo(_DataWrapper):
    """
    投票信息

    Fields:
        title (str): 得票数
        options (list[VoteOption]): 选项列表
        is_multi (bool): 是否多选
        total_vote (int): 总投票数
        total_user (int): 总投票人数
    """

    __slots__ = ['title', '_options', 'is_multi', 'total_vote', 'total_user']

    class VoteOption(object):
        """
        投票选项信息

        Fields:
            vote_num (int): 得票数
            text (str): 选项描述文字
            image (str): 选项描述图像链接
        """

        __slots__ = ['vote_num', 'text', 'image']

        def __init__(self, _raw_data: PollInfo_pb2.PollInfo.PollOption) -> None:

            self.vote_num: int = _raw_data.num
            self.text: str = _raw_data.text
            self.image: str = _raw_data.image

    def __init__(self, _raw_data: Optional[PollInfo_pb2.PollInfo] = None) -> None:
        super(VoteInfo, self).__init__(_raw_data)

        if _raw_data:
            self.title: str = _raw_data.title
            self._options: List[self.VoteOption] = None
            self.is_multi = bool(_raw_data.is_multi)
            self.total_vote: int = _raw_data.total_poll
            self.total_user: int = _raw_data.total_num

        else:
            self.title = ''
            self.options = []
            self.is_multi = False
            self.total_vote = 0
            self.total_user = 0

    @property
    def options(self):
        if self._options is None:
            self._options = [self.VoteOption(option_proto) for option_proto in self._raw_data.options]
        return self._options


class ShareThread(_BasicContainer):
    """
    被分享的主题帖信息

    Fields:
        text (str): 文本内容
        contents (Fragments): 内容碎片列表

        fid (int): 所在吧id
        tid (int): 主题帖tid
        pid (int): 首楼的回复pid

        title (str): 标题内容
        vote_info (VoteInfo): 投票内容
    """

    __slots__ = ['_contents', 'title', '_vote_info']

    def __init__(self, _raw_data: Optional[ThreadInfo_pb2.ThreadInfo.OriginThreadInfo] = None) -> None:
        super(ShareThread, self).__init__(_raw_data)

        self._contents: Fragments = None
        self._vote_info: VoteInfo = None

        if _raw_data:
            self.fid: int = _raw_data.fid
            self.tid: int = _raw_data.tid
            self.pid: int = _raw_data.pid

            self.title: str = _raw_data.title

        else:
            self.title = ''

    @property
    def contents(self) -> Fragments:

        if self._contents is None:

            if self._raw_data:
                self._contents = Fragments(self._raw_data.first_post_content)
            else:
                self._contents = Fragments()

        return self._contents

    @property
    def vote_info(self) -> VoteInfo:

        if self._vote_info is None:

            if self._raw_data:
                self._vote_info = (
                    VoteInfo(poll_info_raw_data)
                    if (poll_info_raw_data := self._raw_data.poll_info).options
                    else VoteInfo()
                )

            else:
                self._vote_info = VoteInfo()

        return self._vote_info


class Thread(_BasicContainer):
    """
    主题帖信息
    用于c/f/frs/page接口

    Fields:
        text (str): 文本内容
        contents (Fragments): 内容碎片列表

        fid (int): 所在吧id
        tid (int): 主题帖tid
        pid (int): 首楼的回复pid
        user (UserInfo): 发布者信息
        author_id (int): int 发布者user_id

        tab_id (int): 分区编号
        is_good (bool): 是否精品帖
        is_top (bool): 是否置顶帖
        is_share (bool): 是否分享帖
        is_hide (bool): 是否被屏蔽
        is_livepost (bool): 是否为置顶话题

        title (str): 标题内容
        vote_info (VoteInfo): 投票内容
        share_origin (Thread | None): 转发来的原帖内容
        view_num (int): 浏览量
        reply_num (int): 回复数
        share_num (int): 分享数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 10位时间戳 创建时间
        last_time (int): 10位时间戳 最后回复时间
    """

    __slots__ = [
        '_contents',
        'tab_id',
        'is_good',
        'is_top',
        'is_share',
        'is_hide',
        'is_livepost',
        'title',
        '_vote_info',
        '_share_origin',
        'view_num',
        'reply_num',
        'share_num',
        'agree',
        'disagree',
        'create_time',
        'last_time',
    ]

    def __init__(self, _raw_data: Optional[ThreadInfo_pb2.ThreadInfo] = None) -> None:
        super(Thread, self).__init__(_raw_data)

        self._contents: Fragments = None
        self._vote_info: VoteInfo = None
        self._share_origin: ShareThread = None

        if _raw_data:
            self.fid: int = _raw_data.fid
            self.tid: int = _raw_data.id
            self.pid: int = _raw_data.first_post_id
            self._user = UserInfo(_raw_data=_raw_data.author) if _raw_data.author.id else None
            self._author_id: int = _raw_data.author_id

            self.tab_id: int = _raw_data.tab_id
            self.is_good = bool(_raw_data.is_good)
            self.is_top = bool(_raw_data.is_top)
            self.is_share = bool(_raw_data.is_share_thread)
            self.is_hide = bool(_raw_data.is_frs_mask)
            self.is_livepost = bool(_raw_data.is_livepost)

            self.title: str = _raw_data.title
            self.view_num: int = _raw_data.view_num
            self.reply_num: int = _raw_data.reply_num
            self.share_num: int = _raw_data.share_num
            self.agree: int = _raw_data.agree.agree_num
            self.disagree: int = _raw_data.agree.disagree_num
            self.create_time: int = _raw_data.create_time
            self.last_time: int = _raw_data.last_time_int

        else:
            self.tab_id = 0
            self.is_good = False
            self.is_top = False
            self.is_share = False
            self.is_hide = False
            self.is_livepost = False

            self.title = ''
            self.view_num = 0
            self.reply_num = 0
            self.share_num = 0
            self.agree = 0
            self.disagree = 0
            self.create_time = 0
            self.last_time = 0

    @property
    def text(self) -> str:

        if self._text is None:

            if self.title:
                self._text = f"{self.title}\n{self.contents.text}"
            else:
                self._text = self.contents.text

        return self._text

    @property
    def contents(self) -> Fragments:

        if self._contents is None:

            if self._raw_data:
                self._contents = Fragments(self._raw_data.first_post_content)
            else:
                self._contents = Fragments()

        return self._contents

    @property
    def vote_info(self) -> VoteInfo:

        if self._vote_info is None:

            if self._raw_data:
                self._vote_info = (
                    VoteInfo(poll_info_raw_data)
                    if (poll_info_raw_data := self._raw_data.poll_info).options
                    else VoteInfo()
                )

            else:
                self._vote_info = VoteInfo()

        return self._vote_info

    @property
    def share_origin(self) -> ShareThread:

        if self._share_origin is None:

            if self._raw_data.origin_thread_info.tid:
                self._share_origin = ShareThread(self._raw_data.origin_thread_info)
            else:
                self._share_origin = ShareThread()

        return self._share_origin


class Threads(_Containers[Thread]):
    """
    Thread列表

    Fields:
        _objs (list[Thread])
        page (Page): 页码信息

        forum (Forum): 所在吧信息
        tab_map (dict[str, int]): {分区名:分区id}
    """

    __slots__ = ['_forum', '_tab_map']

    def __init__(self, _raw_data: Optional[FrsPageResIdl_pb2.FrsPageResIdl.DataRes] = None) -> None:
        super(Threads, self).__init__(_raw_data)

        self._forum: Forum = None
        self._tab_map: dict[str, int] = None

        if _raw_data:
            self._raw_data = _raw_data

        else:
            self._raw_data = None

    @property
    def objs(self) -> List[Thread]:

        if self._objs is None:

            if self._raw_data:

                users = {
                    user.user_id: user
                    for user_raw_data in self._raw_data.user_list
                    if (user := UserInfo(_raw_data=user_raw_data)).user_id
                }
                self._objs = [Thread(thread_proto) for thread_proto in self._raw_data.thread_list]

                for thread in self._objs:
                    thread._user = users[thread.author_id]

            else:
                self._objs = []

        return self._objs

    @property
    def forum(self) -> Forum:

        if self._forum is None:

            if self._raw_data:
                self._forum = Forum(self._raw_data.forum)
            else:
                self._forum = Forum()

        return self._forum

    @property
    def tab_map(self) -> Forum:

        if self._tab_map is None:

            if self._raw_data:
                self._tab_map = {tab_proto.tab_name: tab_proto.tab_id for tab_proto in self._raw_data.nav_tab_info.tab}
            else:
                self._tab_map = {}

        return self._tab_map


class Post(_BasicContainer):
    """
    楼层信息

    Fields:
        text (str): 文本内容
        contents (Fragments): 内容碎片列表
        sign (str): 小尾巴文本内容
        comments (list[Comment]): 高赞楼中楼

        fid (int): 所在吧id
        tid (int): 所在主题帖tid
        pid (int): 回复pid
        user (UserInfo): 发布者信息
        author_id (int): int 发布者user_id

        floor (int): 楼层数
        reply_num (int): 楼中楼数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 10位时间戳，创建时间
        is_thread_author (bool): 是否楼主
    """

    __slots__ = [
        '_contents',
        '_sign',
        '_comments',
        'floor',
        'reply_num',
        'agree',
        'disagree',
        'create_time',
        'is_thread_author',
    ]

    def __init__(self, _raw_data: Optional[Post_pb2.Post] = None) -> None:
        super(Post, self).__init__(_raw_data)

        self._contents: Fragments = None
        self._sign: str = None
        self._comments: List[Comment] = None
        self.is_thread_author = False

        if _raw_data:
            self.pid: int = _raw_data.id
            self._user = UserInfo(_raw_data=_raw_data.author) if _raw_data.author.id else None
            self._author_id: int = _raw_data.author_id

            self.floor: int = _raw_data.floor
            self.reply_num: int = _raw_data.sub_post_number
            self.agree: int = _raw_data.agree.agree_num
            self.disagree: int = _raw_data.agree.disagree_num
            self.create_time: int = _raw_data.time

        else:
            self._floor = 0
            self._reply_num = 0
            self._agree = 0
            self._disagree = 0
            self._create_time = 0

    @property
    def text(self) -> str:
        if self._text is None:

            if self.sign:
                self._text = f'{self.contents.text}\n{self.sign}'
            else:
                self._text = self.contents.text

        return self._text

    @property
    def contents(self) -> Fragments:
        if self._contents is None:

            if self._raw_data:
                self._contents = Fragments(self._raw_data.content)
            else:
                self._contents = Fragments()

        return self._contents

    @property
    def sign(self) -> Fragments:
        if self._sign is None:

            if self._raw_data:
                self._sign = ''.join([sign.text for sign in self._raw_data.signature.content if sign.type == 0])
            else:
                self._sign = ''

        return self._sign

    @property
    def comments(self) -> List["Comment"]:
        if self._comments is None:

            if self._raw_data:
                self._comments = [
                    Comment(comment_proto) for comment_proto in self._raw_data.sub_post_list.sub_post_list
                ]
            else:
                self._comments = []

        return self._comments


class Posts(_Containers[Post]):
    """
    Post列表

    Fields:
        _objs (list[Post])
        page (Page): 页码信息

        forum (Forum): 所在吧信息
        thread (Thread): 所在主题帖信息

        has_fold (bool): 是否存在折叠楼层
    """

    __slots__ = ['_forum', '_thread', 'has_fold']

    def __init__(self, _raw_data: Optional[PbPageResIdl_pb2.PbPageResIdl.DataRes] = None) -> None:
        super(Posts, self).__init__(_raw_data)

        if _raw_data:
            self._forum: Forum = None
            self._thread: Thread = None

            self.has_fold = bool(self._raw_data.has_fold_comment)

        else:
            self._forum = None
            self._thread = None

            self.has_fold = False

    @property
    def objs(self) -> List[Post]:

        if self._objs is None:

            if self._raw_data:
                users = {
                    user.user_id: user
                    for user_raw_data in self._raw_data.user_list
                    if (user := UserInfo(_raw_data=user_raw_data)).user_id
                }

                self._objs = [Post(post_proto) for post_proto in self._raw_data.post_list]

                for post in self._objs:

                    post.fid = self.forum.fid
                    post.tid = self.thread.tid
                    post._user = users.get(post.author_id, None)
                    post.is_thread_author = self.thread.author_id == post.author_id

                    for comment in post.comments:
                        comment.fid = post.fid
                        comment.tid = post.tid
                        comment._user = users.get(comment.author_id, None)

            else:
                self._objs = []

        return self._objs

    @property
    def forum(self) -> Forum:
        if self._forum is None:

            if self._raw_data:
                self._forum = Forum(self._raw_data.forum)
            else:
                self._forum = Forum()

        return self._forum

    @property
    def thread(self) -> Thread:
        if self._thread is None:

            if self._raw_data:
                self._thread = Thread(self._raw_data.thread)
                self._thread.fid = self.forum.fid

            else:
                self._thread = Thread()

        return self._thread


class Comment(_BasicContainer):
    """
    楼中楼信息

    Fields:
        text (str): 文本内容
        contents (Fragments): 内容碎片列表

        fid (int): 所在吧id
        tid (int): 所在主题帖tid
        pid (int): 回复pid
        user (UserInfo): 发布者信息
        author_id (int): int 发布者user_id

        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 10位时间戳，创建时间
    """

    __slots__ = ['_contents', 'agree', 'disagree', 'create_time']

    def __init__(self, _raw_data: Optional[SubPostList_pb2.SubPostList] = None) -> None:
        super(Comment, self).__init__(_raw_data)

        self._contents: Fragments = None

        if _raw_data:
            self.pid: int = _raw_data.id
            self._user = UserInfo(_raw_data=_raw_data.author)
            self._author_id = _raw_data.author_id

            self.agree: int = _raw_data.agree.agree_num
            self.disagree: int = _raw_data.agree.disagree_num
            self.create_time: int = _raw_data.time

        else:
            self.agree = 0
            self.disagree = 0
            self.create_time = 0

    @property
    def text(self) -> str:
        if not self._text:
            self._text = self.contents.text
        return self._text

    @property
    def contents(self) -> Fragments:
        if self._contents is None:

            if self._raw_data:
                self._contents = Fragments(self._raw_data.content)

            else:
                self._contents = Fragments()

        return self._contents


class Comments(_Containers[Comment]):
    """
    Comment列表

    Fields:
        _objs (list[Comment])
        page (Page): 页码信息

        forum (Forum): 所在吧信息
        thread (Thread): 所在主题帖信息
        post (Post): 所在回复信息
    """

    __slots__ = ['_forum', '_thread', '_post']

    def __init__(self, _raw_data: Optional[PbFloorResIdl_pb2.PbFloorResIdl.DataRes] = None) -> None:
        super(Comments, self).__init__(_raw_data)

        self._forum: Forum = None
        self._thread: Thread = None
        self._post: Post = None

    @property
    def objs(self) -> List[Comment]:

        if self._objs is None:

            if self._raw_data:
                self._objs = [Comment(comment_proto) for comment_proto in self._raw_data.subpost_list]

                for comment in self._objs:
                    comment.fid = self.forum.fid
                    comment.tid = self.thread.tid

            else:
                self._objs = []

        return self._objs

    @property
    def forum(self) -> Forum:
        if self._forum is None:

            if self._raw_data:
                self._forum = Forum(self._raw_data.forum)
            else:
                self._forum = Forum()

        return self._forum

    @property
    def thread(self) -> Thread:
        if self._thread is None:

            if self._raw_data:
                self._thread = Thread(self._raw_data.thread)
                self._thread.fid = self.forum.fid

            else:
                self._thread = Thread()

        return self._thread

    @property
    def post(self) -> Post:
        if self._post is None:

            if self._raw_data:
                self._post = Post(self._raw_data.post)
                self._post.fid = self.forum.fid
                self._post.tid = self.thread.tid

            else:
                self._post = Post()

        return self._post


class Reply(_BasicContainer):
    """
    回复信息
    Fields:
        text (str): 文本内容

        fname (str): 所在贴吧名
        tid (int): 所在主题帖tid
        pid (int): 回复pid
        user (UserInfo): 发布者信息
        author_id (int): int 发布者user_id
        post_pid (int): 楼层pid
        post_user (BasicUserInfo): 楼层用户信息
        thread_user (BasicUserInfo): 楼主用户信息

        is_floor (bool): 是否楼中楼
        create_time (int): 10位时间戳，创建时间
    """

    __slots__ = ['fname', 'post_pid', '_post_user', '_thread_user', 'is_floor', 'create_time']

    def __init__(self, _raw_data: Optional[ReplyMeResIdl_pb2.ReplyMeResIdl.DataRes.ReplyList] = None) -> None:
        super(Reply, self).__init__(_raw_data)

        self._post_user: UserInfo = None
        self._thread_user: UserInfo = None

        if _raw_data:
            self._text: str = _raw_data.content

            self.fname: str = _raw_data.fname
            self.tid: int = _raw_data.thread_id
            self.pid: int = _raw_data.post_id
            self.post_pid: int = _raw_data.quote_pid

            self.is_floor = bool(_raw_data.is_floor)
            self.create_time = _raw_data.time

        else:
            self.is_floor: bool = False
            self.create_time: int = 0

    @property
    def text(self) -> str:
        return self._text

    @property
    def user(self) -> UserInfo:
        if self._user is None:

            if self._raw_data:
                self._user = (
                    UserInfo(_raw_data=user_raw_data) if (user_raw_data := self._raw_data.replyer).id else UserInfo()
                )
            else:
                self._user = UserInfo()

        return self._user

    @property
    def post_user(self) -> BasicUserInfo:
        if self._post_user is None:

            if self._raw_data:
                self._post_user = (
                    BasicUserInfo(_raw_data=user_raw_data)
                    if (user_raw_data := self._raw_data.quote_user).id
                    else BasicUserInfo()
                )
            else:
                self._post_user = BasicUserInfo()

        return self._post_user

    @property
    def thread_user(self) -> BasicUserInfo:
        if self._thread_user is None:

            if self._raw_data:
                self._thread_user = (
                    BasicUserInfo(_raw_data=user_raw_data)
                    if (user_raw_data := self._raw_data.thread_author_user).id
                    else BasicUserInfo()
                )
            else:
                self._thread_user = BasicUserInfo()

        return self._thread_user


class Replys(_Containers[Reply]):
    """
    Reply列表

    Fields:
        _objs (list[Reply])
        page (Page): 页码信息
    """

    __slots__ = []

    def __init__(self, _raw_data: Optional[ReplyMeResIdl_pb2.ReplyMeResIdl] = None) -> None:
        super(Replys, self).__init__(_raw_data)

    @property
    def objs(self) -> List[Reply]:

        if self._objs is None:

            if self._raw_data:
                self._objs = [Reply(reply_proto) for reply_proto in self._raw_data.reply_list]
            else:
                self._objs = []

        return self._objs


class At(_BasicContainer):
    """
    @信息

    Fields:
        text (str): 文本内容

        fname (str): 所在贴吧名
        tid (int): 所在主题帖tid
        pid (int): 回复pid
        user (UserInfo): 发布者信息
        author_id (int): 发布者user_id

        is_floor (bool): 是否楼中楼
        is_thread (bool): 是否主题帖

        create_time (int): 10位时间戳，创建时间
    """

    __slots__ = ['fname', 'is_floor', 'is_thread', 'create_time']

    def __init__(self, _raw_data: Optional[Dict] = None) -> None:
        super(At, self).__init__(_raw_data)

        if _raw_data:
            self._text: str = _raw_data['content']

            self.fname: str = _raw_data['fname']
            self.tid = int(_raw_data['thread_id'])
            self.pid = int(_raw_data['post_id'])

            self.is_floor = bool(int(_raw_data['is_floor']))
            self.is_thread = bool(int(_raw_data['is_first_post']))
            self.create_time = int(_raw_data['time'])

        else:
            self._text = ''

            self.fname = ''
            self.tid = 0
            self.pid = 0

            self.is_floor = False
            self.is_thread = False
            self.create_time = 0

    @property
    def user(self) -> UserInfo:
        if self._user is None:

            if self._raw_data:
                user_proto = ParseDict(self._raw_data['replyer'], User_pb2.User(), ignore_unknown_fields=True)
                self._user = UserInfo(_raw_data=user_proto) if user_proto.id else UserInfo()
            else:
                self._user = UserInfo()

        return self._user


class Ats(_Containers[At]):
    """
    At列表

    Fields:
        _objs (list[At])
        page (Page): 页码信息
    """

    __slots__ = []

    def __init__(self, _raw_data: Optional[Dict] = None) -> None:
        super(Ats, self).__init__(_raw_data)

    @property
    def objs(self) -> List[At]:

        if self._objs is None:

            if self._raw_data and (at_dicts := self._raw_data['at_list']):
                self._objs = [At(_raw_data=at_dict) for at_dict in at_dicts]
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        if self._page is None:

            if self._raw_data:
                page_proto = ParseDict(self._raw_data['page'], Page_pb2.Page(), ignore_unknown_fields=True)
                self._page = Page(page_proto)

            else:
                self._page = Page()

        return self._page


class Search(_BasicContainer):
    """
    搜索结果

    Fields:
        text (str): 文本内容
        title (str): 标题

        fname (str): 所在贴吧名
        tid (int): 所在主题帖tid
        pid (int): 回复pid

        is_floor (bool): 是否楼中楼

        create_time (int): 10位时间戳，创建时间
    """

    __slots__ = ['fname', 'title', 'is_floor', 'create_time']

    def __init__(self, _raw_data: Optional[Dict] = None) -> None:
        super(Search, self).__init__(_raw_data)

        if _raw_data:
            self._text = _raw_data['content']
            self.title = _raw_data['title']

            self.fname = _raw_data['fname']
            self.tid = int(_raw_data['tid'])
            self.pid = int(_raw_data['pid'])

            self.is_floor = bool(int(_raw_data['is_floor']))
            self.create_time = int(_raw_data['time'])

        else:
            self._text = ''
            self.title = ''

            self.fname = ''
            self._tid = 0
            self._pid = 0

            self._is_floor = False
            self._create_time = 0

    @property
    def user(self) -> UserInfo:
        if self._user is None:

            if self._raw_data:
                user_proto = ParseDict(self._raw_data['author'], User_pb2.User(), ignore_unknown_fields=True)
                self._user = UserInfo(_raw_data=user_proto) if user_proto.id else UserInfo()

            else:
                self._user = UserInfo()

        return self._user


class Searches(_Containers[Search]):
    """
    搜索结果列表

    Fields:
        _objs (list[Search])
        page (Page): 页码信息
    """

    __slots__ = []

    def __init__(self, _raw_data: Optional[Dict] = None) -> None:
        super(Searches, self).__init__(_raw_data)

    @property
    def objs(self) -> List[Search]:

        if self._objs is None:

            if self._raw_data and (search_dicts := self._raw_data['post_list']):
                self._objs = [Search(_raw_data=search_dict) for search_dict in search_dicts]
            else:
                self._objs = []

        return self._objs

    @property
    def page(self) -> Page:
        if self._page is None:

            if self._raw_data:
                page_proto = ParseDict(self._raw_data['page'], Page_pb2.Page(), ignore_unknown_fields=True)
                self._page = Page(page_proto)

            else:
                self._page = Page()

        return self._page


class NewThread(_BasicContainer):
    """
    新版主题帖信息
    删除无用字段并适配新版字段名

    Fields:
        text (str): 文本内容
        contents (Fragments): 内容碎片列表

        fid (int): 所在吧id
        tid (int): 主题帖tid
        pid (int): 首楼的回复pid
        user (UserInfo): 发布者信息
        author_id (int): int 发布者user_id

        title (str): 标题内容
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
        'title',
        '_vote_info',
        'view_num',
        'reply_num',
        'share_num',
        'agree',
        'disagree',
        'create_time',
    ]

    def __init__(self, _raw_data: Optional[NewThreadInfo_pb2.NewThreadInfo] = None) -> None:
        super(NewThread, self).__init__(_raw_data)

        self._contents: Fragments = None
        self._vote_info: VoteInfo = None

        if _raw_data:
            self.fid: int = _raw_data.forum_id
            self.tid: int = _raw_data.thread_id
            self.pid: int = _raw_data.post_id
            self._author_id: int = _raw_data.user_id

            self.title: str = _raw_data.title
            self.view_num: int = _raw_data.freq_num
            self.reply_num: int = _raw_data.reply_num
            self.share_num: int = _raw_data.share_num
            self.agree: int = _raw_data.agree.agree_num
            self.disagree: int = _raw_data.agree.disagree_num
            self.create_time: int = _raw_data.create_time

        else:
            self.title = ''
            self.view_num = 0
            self.reply_num = 0
            self.share_num = 0
            self.agree = 0
            self.disagree = 0
            self.create_time = 0

    @property
    def text(self) -> str:

        if self._text is None:

            if self.title:
                self._text = f"{self.title}\n{self.contents.text}"
            else:
                self._text = self.contents.text

        return self._text

    @property
    def contents(self) -> Fragments:

        if self._contents is None:

            if self._raw_data:
                self._contents = Fragments(self._raw_data.first_post_content)
            else:
                self._contents = Fragments()

        return self._contents

    @property
    def vote_info(self) -> VoteInfo:

        if self._vote_info is None:

            if self._raw_data:
                self._vote_info = (
                    VoteInfo(poll_info_raw_data)
                    if (poll_info_raw_data := self._raw_data.poll_info).options
                    else VoteInfo()
                )

            else:
                self._vote_info = VoteInfo()

        return self._vote_info


class UserPost(_BasicContainer):
    """
    用户历史回复信息

    Fields:
        text (str): 文本内容
        contents (Fragments): 内容碎片列表

        fid (int): 所在吧id
        tid (int): 所在主题帖tid
        pid (int): 回复pid
        user (UserInfo): 发布者信息
        author_id (int): int 发布者user_id

        create_time (int): 10位时间戳，创建时间
    """

    __slots__ = ['_contents', 'create_time']

    def __init__(
        self, _raw_data: Optional[UserPostResIdl_pb2.UserPostResIdl.DataRes.PostInfoList.PostInfoContent] = None
    ) -> None:
        super(UserPost, self).__init__(_raw_data)

        self._contents: Fragments = None

        if _raw_data:
            self.pid: int = _raw_data.post_id

            self.create_time: int = _raw_data.create_time

        else:
            self._create_time = 0

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = self.contents.text
        return self._text

    @property
    def contents(self) -> Fragments:
        if self._contents is None:

            if self._raw_data:
                self._contents = Fragments(self._raw_data.post_content)
            else:
                self._contents = Fragments()

        return self._contents


class UserPosts(_Containers[UserPost]):
    """
    UserPost列表

    Fields:
        _objs (list[UserPost])
    """

    __slots__ = ['fid', 'tid']

    def __init__(self, _raw_data: Optional[UserPostResIdl_pb2.UserPostResIdl.DataRes.PostInfoList] = None) -> None:
        super(UserPosts, self).__init__(_raw_data)

        self.fid: int = self._raw_data.forum_id
        self.tid: int = self._raw_data.thread_id

    @property
    def objs(self) -> List[UserPost]:

        if self._objs is None:

            if self._raw_data:
                self._objs = [UserPost(userpost_proto) for userpost_proto in self._raw_data.content]

                for post in self._objs:

                    post.fid = self.fid
                    post.tid = self.tid

            else:
                self._objs = []

        return self._objs
