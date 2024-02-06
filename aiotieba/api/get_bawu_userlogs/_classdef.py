import dataclasses as dcs
from datetime import datetime

import bs4

from ...exception import TbErrorExt
from ...helper import default_datetime
from .._classdef import Containers


@dcs.dataclass
class Userlog:
    """
    吧务用户管理日志

    Attributes:
        op_type (str): 操作类型
        op_duration (int): 操作作用时长
        user_portrait (str): 被操作用户的portrait
        op_user_name (str): 操作人用户名
        op_time (datetime.datetime): 操作时间
    """

    op_type: str = ''
    op_duration: int = 0
    user_portrait: str = ''
    op_user_name: str = ''
    op_time: datetime = dcs.field(default_factory=default_datetime)

    @staticmethod
    def from_tbdata(data_tag: bs4.element.Tag) -> "Userlog":
        left_cell_item = data_tag.td

        post_user_item = left_cell_item.a
        user_portrait = post_user_item['href'][14:-17]

        op_type_item = left_cell_item.next_sibling.next_sibling
        op_type = op_type_item.string

        op_duration_item = op_type_item.next_sibling
        op_duration = op_duration_item.string.replace(' ', '')
        op_duration = 0 if '天' not in op_duration else int(op_duration[:-1])

        op_user_name_item = op_duration_item.next_sibling
        op_user_name = op_user_name_item.string

        op_time_item = op_user_name_item.next_sibling
        op_time = datetime.strptime(op_time_item.text, '%Y-%m-%d %H:%M')

        return Userlog(op_type, op_duration, user_portrait, op_user_name, op_time)


@dcs.dataclass
class Page_userlog:
    """
    页信息

    Attributes:
        current_page (int): 当前页码
        total_page (int): 总页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    current_page: int = 0
    total_page: int = 0
    total_count: int = 0

    has_more: bool = False
    has_prev: bool = False

    @staticmethod
    def from_tbdata(data_soup: bs4.BeautifulSoup) -> "Page_userlog":
        page_tag = data_soup.find('div', class_='tbui_pagination').find('li', class_='active')
        current_page = int(page_tag.text)
        total_page_item = page_tag.parent.next_sibling
        total_page = int(total_page_item.text[1:-1])
        has_more = current_page < total_page
        has_prev = current_page > 1

        total_count_tag = data_soup.find('div', class_='breadcrumbs')
        total_count = int(total_count_tag.em.text)

        return Page_userlog(current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class Userlogs(TbErrorExt, Containers[Userlog]):
    """
    吧务用户管理日志表

    Attributes:
        objs (list[Postlog]): 吧务用户管理日志表
        err (Exception | None): 捕获的异常

        page (Page_userlog): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_userlog = dcs.field(default_factory=Page_userlog)

    @staticmethod
    def from_tbdata(data_soup: bs4.BeautifulSoup) -> "Userlogs":
        objs = [Userlog.from_tbdata(t) for t in data_soup.find('tbody').find_all('tr')]
        page = Page_userlog.from_tbdata(data_soup)
        return Userlogs(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
