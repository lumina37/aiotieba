from typing import List, Optional, Sequence


class Statistics(object):
    """
    吧务后台统计信息
    时间从旧到新

    Attributes:
        view (list[int]): 浏览量
        thread (list[int]): 主题帖数
        new_member (list[int]): 新增吧会员数
        post (list[int]): 回复数
        sign_ratio (list[int]): 签到率
        avg_time (list[int]): 人均浏览时长
        avg_times (list[int]): 人均进吧次数
        recommend (list[int]): 首页推荐数
    """

    __slots__ = [
        '_view',
        '_thread',
        '_new_member',
        '_post',
        '_sign_ratio',
        '_avg_time',
        '_avg_times',
        '_recommend',
    ]

    def __init__(self, data_seq: Optional[Sequence] = None) -> None:
        if data_seq:

            def extract(i: int) -> List[int]:
                seq: list = data_seq[i]['group'][1]['values']
                seq = [int(item['value']) for item in seq]
                return seq

            self._view = extract(0)
            self._thread = extract(1)
            self._new_member = extract(2)
            self._post = extract(3)
            self._sign_ratio = extract(4)
            self._avg_time = extract(5)
            self._avg_times = extract(6)
            self._recommend = extract(7)

        else:
            self._view = []
            self._thread = []
            self._new_member = []
            self._post = []
            self._sign_ratio = []
            self._avg_time = []
            self._avg_times = []
            self._recommend = []

    def __repr__(self) -> str:
        return str(
            {
                'view': self._view,
                'thread': self._thread,
                'new_member': self._new_member,
                'post': self._post,
                'sign_ratio': self._sign_ratio,
                'avg_time': self._avg_time,
                'avg_times': self._avg_times,
                'recommend': self._recommend,
            }
        )

    @property
    def view(self) -> List[int]:
        """
        浏览量
        """

        return self._view

    @property
    def thread(self) -> List[int]:
        """
        主题帖数
        """

        return self._thread

    @property
    def new_member(self) -> List[int]:
        """
        新增吧会员数
        """

        return self._new_member

    @property
    def post(self) -> List[int]:
        """
        回复数
        """

        return self._post

    @property
    def sign_ratio(self) -> List[int]:
        """
        签到率
        """

        return self._sign_ratio

    @property
    def avg_time(self) -> List[int]:
        """
        人均浏览时长
        """

        return self._avg_time

    @property
    def avg_times(self) -> List[int]:
        """
        人均进吧次数
        """

        return self._avg_times

    @property
    def recommend(self) -> List[int]:
        """
        首页推荐数
        """

        return self._recommend
