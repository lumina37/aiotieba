import dataclasses as dcs
from datetime import datetime
from functools import cached_property
from typing import List

import bs4

from ...exception import TbErrorExt
from ...helper import default_datetime
from .._classdef import Containers


@dcs.dataclass
class Media_postlog:
    """
    媒体信息

    Attributes:
        src (str): 小图链接
        origin_src (str): 原图链接
        hash (str): 百度图床hash
    """

    src: str = ''
    origin_src: str = ''

    @staticmethod
    def from_tbdata(data_tag: bs4.element.Tag) -> "Media_postlog":
        src = data_tag.img['original']
        origin_src = data_tag['href']
        return Media_postlog(src, origin_src)

    @cached_property
    def hash(self) -> str:
        end_idx = self.src.rfind('.')

        if end_idx == -1:
            hash_ = ''
        else:
            start_idx = self.src.rfind('/', 0, end_idx)
            hash_ = self.src[start_idx + 1 : end_idx]

        return hash_


@dcs.dataclass
class Postlog:
    """
    吧务帖子管理日志

    Attributes:
        text (str): 文本内容
        title (str): 所在主题帖标题
        medias (list[Media_postlog]): 媒体列表

        tid (int): 所在主题帖id
        pid (int): 回复id

        op_type (str): 操作类型
        post_portrait (str): 发帖用户的portrait
        post_time (datetime): 发帖时间 不含年份
        op_user_name (str): 操作人用户名
        op_time (datetime): 操作时间
    """

    text: str = ""
    title: str = ""
    medias: List[Media_postlog] = dcs.field(default_factory=list)

    tid: int = 0
    pid: int = 0

    op_type: str = ''
    post_portrait: str = ''
    post_time: datetime = dcs.field(default_factory=default_datetime)
    op_user_name: str = ''
    op_time: datetime = dcs.field(default_factory=default_datetime)

    @staticmethod
    def from_tbdata(data_tag: bs4.element.Tag) -> "Postlog":
        left_cell_item = data_tag.td

        post_meta_item = left_cell_item.find('div', class_='post_meta')
        post_user_item = post_meta_item.div
        post_portrait = post_user_item.a['href'][14:-17]
        post_time_item = post_meta_item.time
        post_time = datetime.strptime(post_time_item.text, '%m月%d日 %H:%M')

        post_content_item = post_meta_item.next_sibling
        title_item = post_content_item.h1.a
        url: str = title_item['href']
        tid = int(url[3 : url.find('?')])
        pid = int(url[url.rfind('#') + 1 :])
        pid = pid if pid != tid else 0
        title = title_item.string

        text_item = post_content_item.div
        text = text_item.string[12:]
        medias = [Media_postlog(tag) for tag in text_item.next_sibling('a', class_=None)]

        op_type_item = left_cell_item.next_sibling
        op_type = op_type_item.string

        op_user_name_item = op_type_item.next_sibling
        op_user_name = op_user_name_item.string

        op_time_item = op_user_name_item.next_sibling
        op_time = datetime.strptime(op_time_item.text, '%Y-%m-%d%H:%M')

        return Postlog(text, title, medias, tid, pid, op_type, post_portrait, post_time, op_user_name, op_time)


@dcs.dataclass
class Page_postlog:
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
    def from_tbdata(data_soup: bs4.BeautifulSoup) -> "Page_postlog":
        page_tag = data_soup.find('div', class_='tbui_pagination').find('li', class_='active')
        current_page = int(page_tag.text)
        total_page_item = page_tag.parent.next_sibling
        total_page = int(total_page_item.text[1:-1])
        has_more = current_page < total_page
        has_prev = current_page > 1

        total_count_tag = data_soup.find('div', class_='breadcrumbs')
        total_count = int(total_count_tag.em.text)

        return Page_postlog(current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class Postlogs(TbErrorExt, Containers[Postlog]):
    """
    吧务帖子管理日志表

    Attributes:
        objs (list[Postlog]): 吧务帖子管理日志表
        err (Exception | None): 捕获的异常

        page (Page_postlog): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_postlog = dcs.field(default_factory=Page_postlog)

    @staticmethod
    def from_tbdata(data_soup: bs4.BeautifulSoup) -> "Postlogs":
        objs = [Postlog.from_tbdata(t) for t in data_soup.find('tbody').find_all('tr')]
        page = Page_postlog.from_tbdata(data_soup)
        return Postlogs(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
