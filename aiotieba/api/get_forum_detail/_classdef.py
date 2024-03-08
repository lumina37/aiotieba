import dataclasses as dcs

from ...exception import TbErrorExt
from .._classdef import TypeMessage


@dcs.dataclass
class Forum_detail(TbErrorExt):
    """
    贴吧信息

    Attributes:
        err (Exception | None): 捕获的异常

        fid (int): 贴吧id
        fname (str): 贴吧名

        category (str): 一级分类

        small_avatar (str): 吧头像(小)
        origin_avatar (str): 吧头像(原图)
        slogan (str): 吧标语
        member_num (int): 吧会员数
        post_num (int): 发帖量

        has_bawu (bool): 是否有吧务
    """

    fid: int = 0
    fname: str = ''

    category: str = ''

    small_avatar: str = ""
    origin_avatar: str = ""
    slogan: str = ""
    member_num: int = 0
    post_num: int = 0

    has_bawu: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Forum_detail":
        forum_proto = data_proto.forum_info
        fid = forum_proto.forum_id
        fname = forum_proto.forum_name
        category = forum_proto.lv1_name
        small_avatar = forum_proto.avatar
        origin_avatar = forum_proto.avatar_origin
        slogan = forum_proto.slogan
        member_num = forum_proto.member_count
        post_num = forum_proto.thread_count
        has_bawu = data_proto.election_tab.new_strategy_text == "已有吧主"
        return Forum_detail(fid, fname, category, small_avatar, origin_avatar, slogan, member_num, post_num, has_bawu)
