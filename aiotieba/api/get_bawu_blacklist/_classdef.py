import dataclasses as dcs

import bs4

from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class BawuBlacklistUser:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名

        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''

    @staticmethod
    def from_tbdata(data_tag: bs4.element.Tag) -> "BawuBlacklistUser":
        user_info_item = data_tag.previous_sibling.input
        user_name = user_info_item['data-user-name']
        user_id = int(user_info_item['data-user-id'])
        portrait = data_tag.a['href'][14:-17]
        return BawuBlacklistUser(user_id, portrait, user_name)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "BawuBlacklistUser") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def log_name(self) -> str:
        return str(self)


@dcs.dataclass
class Page_bwblacklist:
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
    has_prev: bool = False

    def from_tbdata(data_tag: bs4.element.Tag) -> "Page_bwblacklist":
        current_page = int(data_tag.text)
        total_page_item = data_tag.parent.next_sibling
        total_page = int(total_page_item.text[1:-1])
        has_more = current_page < total_page
        has_prev = current_page > 1
        return Page_bwblacklist(current_page, total_page, has_more, has_prev)


@dcs.dataclass
class BawuBlacklistUsers(TbErrorExt, Containers[BawuBlacklistUser]):
    """
    吧务黑名单列表

    Attributes:
        objs (list[BawuBlacklistUser]): 吧务黑名单列表
        err (Exception | None): 捕获的异常

        page (Page_bwblacklist): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_bwblacklist = dcs.field(default_factory=Page_bwblacklist)

    @staticmethod
    def from_tbdata(data_soup: bs4.BeautifulSoup) -> "BawuBlacklistUsers":
        objs = [BawuBlacklistUser.from_tbdata(t) for t in data_soup('td', class_='left_cell')]
        page_tag = data_soup.find('div', class_='tbui_pagination').find('li', class_='active')
        page = Page_bwblacklist.from_tbdata(page_tag)
        return BawuBlacklistUsers(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
