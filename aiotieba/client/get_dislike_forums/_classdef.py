from .._classdef import Containers, TypeMessage


class DislikeForum(object):
    """
    吧广场贴吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名

        member_num (int): 吧会员数
        post_num (int): 发帖量
        thread_num (int): 主题帖数

        is_followed (bool): 是否已关注
    """

    __slots__ = [
        '_fid',
        '_fname',
        '_member_num',
        '_post_num',
        '_thread_num',
    ]

    def _init(self, data_proto: TypeMessage) -> "DislikeForum":
        self._fid = data_proto.forum_id
        self._fname = data_proto.forum_name
        self._member_num = data_proto.member_count
        self._post_num = data_proto.post_num
        self._thread_num = data_proto.thread_num
        return self

    def __repr__(self) -> str:
        return str(
            {
                'fid': self._fid,
                'fname': self._fname,
                'member_num': self._member_num,
                'post_num': self._post_num,
                'thread_num': self._thread_num,
            }
        )

    def __eq__(self, obj: "DislikeForum") -> bool:
        return self._fid == obj._fid

    def __hash__(self) -> int:
        return self._fid

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

    @property
    def member_num(self) -> int:
        """
        吧会员数
        """

        return self._member_num

    @property
    def post_num(self) -> int:
        """
        发帖量
        """

        return self._post_num

    @property
    def thread_num(self) -> int:
        """
        主题帖数
        """

        return self._thread_num


class DislikeForums(Containers[DislikeForum]):
    """
    首页推荐屏蔽的贴吧列表

    Attributes:
        _objs (list[DislikeForum]): 首页推荐屏蔽的贴吧列表

        has_more (bool): 是否还有下一页
    """

    __slots__ = ['_has_more']

    def _init(self, data_proto: TypeMessage) -> "DislikeForums":
        self._objs = [DislikeForum()._init(p) for p in data_proto.forum_list]
        self._has_more = bool(data_proto.has_more)
        return self

    def _init_null(self) -> "DislikeForums":
        self._objs = []
        self._has_more = False
        return self

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._has_more
