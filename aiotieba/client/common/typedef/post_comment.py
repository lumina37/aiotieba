__all__ = [
    'Comment',
    'Comments',
    'Post',
    'Posts',
]

from typing import List, Optional

from .common import Page, TypeMessage, UserInfo, VirtualImage
from .container import Container, Containers
from .forum import BasicForum
from .frags import FragAt, Fragments, FragText
from .thread import Thread


class Comment(Container):
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

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
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


class Post(Container):
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
        vimage (VirtualImage): 虚拟形象信息

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
        '_vimage',
        '_floor',
        '_reply_num',
        '_agree',
        '_disagree',
        '_create_time',
        '_is_thread_author',
    ]

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
        super(Post, self).__init__()

        self._is_thread_author = False

        if _raw_data:
            self._contents = _raw_data.content
            self._sign = _raw_data.signature.content
            self._comments = _raw_data.sub_post_list.sub_post_list

            self._pid = _raw_data.id
            self._user = UserInfo(_raw_data=_raw_data.author) if _raw_data.author.id else None
            self._author_id = _raw_data.author_id
            self._vimage = VirtualImage(bool(_raw_data.custom_figure.background_value), _raw_data.custom_state.content)

            self._floor = _raw_data.floor
            self._reply_num = _raw_data.sub_post_number
            self._agree = _raw_data.agree.agree_num
            self._disagree = _raw_data.agree.disagree_num
            self._create_time = _raw_data.time

        else:
            self._contents = None
            self._sign = None
            self._comments = None

            self._vimage = VirtualImage()

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

        Note:
            不包含用户等级和ip属地信息
        """

        if not isinstance(self._comments, list):
            if self._comments is not None:
                self._comments = [Comment(_proto) for _proto in self._comments]
            else:
                self._comments = []

        return self._comments

    @property
    def vimage(self) -> VirtualImage:
        """
        虚拟形象信息
        """

        return self._vimage

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


class Comments(Containers[Comment]):
    """
    楼中楼列表

    Attributes:
        objs (list[Comment]): 楼中楼列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页

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

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
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


class Posts(Containers[Post]):
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

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
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

                if not self._users:

                    for post in self._objs:

                        post._fid = self.forum.fid
                        post._fname = self.forum.fname
                        post._tid = self.thread.tid
                        post._is_thread_author = self.thread.author_id == post.author_id

                        for comment in post.comments:
                            comment._fid = post.fid
                            comment._fname = post.fname
                            comment._tid = post.tid

                else:
                    users = {
                        user.user_id: user for _proto in self._users if (user := UserInfo(_raw_data=_proto)).user_id
                    }
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
