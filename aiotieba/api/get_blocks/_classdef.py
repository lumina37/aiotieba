import dataclasses as dcs
from typing import Mapping

import bs4

from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class Block:
    """
    待解封用户信息

    Attributes:
        user_id (int): user_id
        user_name (str): 用户名
        nick_name_old (str): 旧版昵称
        day (int): 封禁天数
    """

    user_id: int = 0
    user_name: str = ''
    nick_name_old: str = ''
    day: int = 0

    @staticmethod
    def from_tbdata(data_tag: bs4.element.Tag) -> "Block":
        id_tag = data_tag.a
        user_id = int(id_tag['attr-uid'])
        user_name = id_tag['attr-un']
        nick_name_old = id_tag['attr-nn']
        day = int(id_tag['attr-blockday'])
        return Block(user_id, user_name, nick_name_old, day)


@dcs.dataclass
class Page_block:
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

    page_size: int = 0
    current_page: int = 0
    total_page: int = 0
    total_count: int = 0

    has_more: bool = False
    has_prev: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> "Page_block":
        page_size = data_map['size']
        current_page = data_map['pn']
        total_page = data_map['total_page']
        total_count = data_map['total_count']
        has_more = data_map['have_next']
        has_prev = current_page > 1
        return Page_block(page_size, current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class Blocks(TbErrorExt, Containers[Block]):
    """
    待恢复帖子列表

    Attributes:
        objs (list[Block]): 待恢复帖子列表
        err (Exception | None): 捕获的异常

        page (Page_block): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_block = dcs.field(default_factory=Page_block)

    def from_tbdata(data_map: Mapping) -> "Blocks":
        data_soup = bs4.BeautifulSoup(data_map['data']['content'], 'lxml')
        objs = [Block.from_tbdata(t) for t in data_soup('li')]
        page = Page_block.from_tbdata(data_map['data']['page'])
        return Blocks(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
