import dataclasses as dcs
from typing import Mapping

from ...exception import TbErrorExt


@dcs.dataclass
class Forum(TbErrorExt):
    """
    贴吧信息

    Attributes:
        err (Exception | None): 捕获的异常

        fid (int): 贴吧id
        fname (str): 贴吧名

        category (str): 一级分类
        subcategory (str): 二级分类

        small_avatar (str): 吧头像(小)
        slogan (str): 吧标语
        member_num (int): 吧会员数
        post_num (int): 发帖量
        thread_num (int): 主题帖数

        has_bawu (bool): 是否有吧务
    """

    fid: int = 0
    fname: str = ''

    category: str = ''
    subcategory: str = ''

    small_avatar: str = ""
    slogan: str = ""
    member_num: int = 0
    post_num: int = 0
    thread_num: int = 0

    has_bawu: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Forum":
        fid = data_map['id']
        fname = data_map['name']
        category = data_map['first_class']
        subcategory = data_map['second_class']
        small_avatar = data_map['avatar']
        slogan = data_map['slogan']
        member_num = data_map['member_num']
        post_num = data_map['post_num']
        thread_num = data_map['thread_num']
        has_bawu = 'managers' in data_map
        return Forum(
            fid, fname, category, subcategory, small_avatar, slogan, member_num, post_num, thread_num, has_bawu
        )
