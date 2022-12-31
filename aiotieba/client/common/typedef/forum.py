__all__ = [
    'BasicForum',
    'Forum',
    'SquareForum',
    'SquareForums',
    'FollowForums',
    'SelfFollowForums',
    'DislikeForums',
]

from collections.abc import Iterable
from typing import Dict, List, Optional

from google.protobuf.json_format import ParseDict

from ..protobuf import ForumList_pb2, Page_pb2
from .common import Page, TypeMessage
from .container import Containers


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

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:

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

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
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

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
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


class SquareForums(Containers[SquareForum]):
    """
    吧广场列表

    Attributes:
        objs (list[SquareForum]): 吧广场列表

        page (Page): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_page']

    def __init__(self, _raw_data: Optional[Iterable[TypeMessage]] = None) -> None:
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


class FollowForums(Containers[Forum]):
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


class SelfFollowForums(Containers[Forum]):
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
                    Forum(ParseDict(_dict, ForumList_pb2.ForumList(), ignore_unknown_fields=True))
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


class DislikeForums(Containers[Forum]):
    """
    首页推荐屏蔽的贴吧列表

    Attributes:
        objs (list[Forum]): 首页推荐屏蔽的贴吧列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_has_more']

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
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
