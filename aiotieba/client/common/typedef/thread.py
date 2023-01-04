__all__ = [
    'ShareThread',
    'Thread',
    'Threads',
    'NewThread',
    'RecomThreads',
]

from typing import Dict, List, Optional

from google.protobuf.json_format import ParseDict

from ..protobuf import ThreadInfo_pb2
from .common import Page, TypeMessage, UserInfo, VirtualImage, VoteInfo
from .container import Container, Containers
from .forum import BasicForum
from .frags import FragImage, Fragments


class ShareThread(Container):
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
        '_has_voice',
        '_title',
        '_vote_info',
    ]

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
        super(ShareThread, self).__init__()

        if _raw_data:
            self._contents = _raw_data.content
            self._medias = _raw_data.media
            self._has_voice = bool(_raw_data.voice)
            self._title = _raw_data.title

            self._fid = _raw_data.fid
            self._fname = _raw_data.fname
            self._tid = int(_raw_data.tid)
            self._pid = _raw_data.pid

            self._vote_info = _raw_data.poll_info

        else:
            self._contents = None
            self._medias = None
            self._has_voice = False
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
                self._contents._has_voice = self._has_voice

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


class Thread(Container):
    """
    主题帖信息

    Attributes:
        text (str): 文本内容
        contents (Fragments): 正文内容碎片列表
        title (str): 标题

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        pid (int): 首楼回复pid
        user (UserInfo): 发布者的用户信息
        author_id (int): 发布者的user_id
        vimage (VirtualImage): 虚拟形象信息

        type (int): 帖子类型
        tab_id (int): 分区编号
        is_good (bool): 是否精品帖
        is_top (bool): 是否置顶帖
        is_share (bool): 是否分享帖
        is_hide (bool): 是否被屏蔽
        is_livepost (bool): 是否为置顶话题
        is_help (bool): 是否为求助帖

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
        '_vimage',
        '_tab_id',
        '_type',
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

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
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
            self._vimage = VirtualImage(bool(_raw_data.custom_figure.background_value), _raw_data.custom_state.content)

            self._type = _raw_data.thread_type
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

            self._vimage = VirtualImage()

            self._type = 0
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
    def vimage(self) -> VirtualImage:
        """
        虚拟形象信息
        """

        return self._vimage

    @property
    def type(self) -> int:
        """
        帖子类型
        """

        return self._type

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
    def is_help(self) -> bool:
        """
        是否为求助帖
        """

        return self._type == 71

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


class Threads(Containers[Thread]):
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

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
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

                if self._users:

                    self._objs = [Thread(_proto) for _proto in self._objs]
                    users = {
                        user.user_id: user for _proto in self._users if (user := UserInfo(_raw_data=_proto)).user_id
                    }
                    self._users = None

                    for thread in self._objs:
                        thread._fname = self.forum.fname
                        thread._user = users[thread.author_id]

                else:
                    self._objs = [Thread(_proto) for _proto in self._objs]
                    for thread in self._objs:
                        thread._fname = self.forum.fname

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


class NewThread(Container):
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

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
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


class RecomThreads(Containers[Thread]):
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
