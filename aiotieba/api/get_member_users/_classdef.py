import dataclasses as dcs

import bs4

from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class MemberUser:
    """
    最新关注用户信息

    Attributes:
        user_name (str): 用户名
        portrait (str): portrait
        level (int): 等级
    """

    user_name: str = ''
    portrait: str = ''
    level: int = 0

    @staticmethod
    def from_tbdata(data_tag: bs4.element.Tag) -> "MemberUser":
        user_item = data_tag.a
        user_name = user_item['title']
        portrait = user_item['href'][14:]
        level_item = data_tag.span
        level = int(level_item['class'][1][12:])
        return MemberUser(user_name, portrait, level)


@dcs.dataclass
class Page_member:
    """
    页信息

    Attributes:
        current_page (int): 当前页码
        total_page (int): 总页码

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    current_page: int = 0
    total_page: int = 0

    has_more: bool = False
    has_prev: int = False

    @staticmethod
    def from_tbdata(data_tag: bs4.element.Tag) -> "Page_member":
        current_page = int(data_tag.text)
        total_page_item = data_tag.parent.next_sibling
        total_page = int(total_page_item.text[1:-1])
        has_more = current_page < total_page
        has_prev = current_page > 1
        return Page_member(current_page, total_page, has_more, has_prev)


@dcs.dataclass
class MemberUsers(TbErrorExt, Containers[MemberUser]):
    """
    最新关注用户列表

    Attributes:
        objs (list[MemberUser]): 最新关注用户列表
        err (Exception | None): 捕获的异常

        page (Page_member): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_member = dcs.field(default_factory=Page_member)

    @staticmethod
    def from_tbdata(data_soup: bs4.BeautifulSoup) -> "MemberUsers":
        objs = [MemberUser.from_tbdata(t) for t in data_soup('div', class_='name_wrap')]
        page = Page_member.from_tbdata(data_soup.find('div', class_='tbui_pagination').find('li', class_='active'))
        return MemberUsers(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
