import dataclasses as dcs

import bs4

from ...exception import TbErrorExt
from .._classdef import Containers


@dcs.dataclass
class RankForum:
    """
    吧签到排名

    Attributes:
        fname (str): 吧名

        sign_num (int): 签到用户数
        member_num (int): 总用户数

        has_bawu (bool): 是否有吧务
    """

    fname: str = ""

    sign_num: int = 0
    member_num: int = 0

    has_bawu: bool = False

    @staticmethod
    def from_tbdata(data_tag: bs4.element.Tag) -> "RankForum":
        rank_idx_item = data_tag.td
        fname_item = rank_idx_item.find_next_sibling('td')
        fname = fname_item.text
        sign_num_item = fname_item.find_next_sibling('td')
        sign_num = int(sign_num_item.text)
        member_num_item = sign_num_item.find_next_sibling('td')
        member_num = int(member_num_item.text)
        manager_item = member_num_item.find_next_sibling('td', class_='clearfix')
        manager_status_item = manager_item.div
        has_bawu = manager_status_item['class'][0] != 'no_bawu'
        return RankForum(fname, sign_num, member_num, has_bawu)


@dcs.dataclass
class Page_rankforum:
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

    @staticmethod
    def from_tbdata(data_soup: bs4.BeautifulSoup) -> "Page_rankforum":
        pages_item = data_soup.find('div', class_='pagination')
        current_page_item = pages_item.span
        current_page = int(current_page_item.text)
        total_page_item = pages_item.find_all('a')[-1]
        total_page_url: str = total_page_item['href']
        total_page_str = total_page_url[total_page_url.rfind('pn=') + 3 :]
        total_page = int(total_page_str)
        has_more = current_page < total_page
        has_prev = current_page > 1

        return Page_rankforum(current_page, total_page, has_more, has_prev)


@dcs.dataclass
class RankForums(TbErrorExt, Containers[RankForum]):
    """
    吧签到排名表

    Attributes:
        objs (list[RankForum]): 吧签到排名表
        err (Exception | None): 捕获的异常

        page (Page_rankforum): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_rankforum = dcs.field(default_factory=Page_rankforum)

    @staticmethod
    def from_tbdata(data_soup: bs4.BeautifulSoup) -> "RankForums":
        dbgtbody = data_soup.find('table')
        objs = [RankForum.from_tbdata(t) for t in dbgtbody.find_all('tr', class_='j_rank_row')]
        page = Page_rankforum.from_tbdata(data_soup)
        return RankForums(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
