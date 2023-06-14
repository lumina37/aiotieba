import datetime
from typing import List, Optional

import bs4

from .._classdef import Containers


class Media_postlog(object):
    """
    媒体信息

    Attributes:
        src (str): 小图链接
        origin_src (str): 原图链接
        hash (str): 百度图床hash
    """

    __slots__ = [
        '_src',
        '_origin_src',
        '_hash',
    ]

    def __init__(self, data_tag: bs4.element.Tag) -> None:
        self._src = data_tag.img['original']
        self._origin_src = data_tag['href']

        self._hash = None

    def __repr__(self) -> str:
        return str({'src': self._src})

    @property
    def src(self) -> str:
        """
        小图链接

        Note:
            宽720px
        """

        return self._src

    @property
    def origin_src(self) -> str:
        """
        原图链接
        """

        return self._origin_src

    @property
    def hash(self) -> str:
        """
        图像的百度图床hash
        """

        if self._hash is None:
            end_idx = self._src.rfind('.')

            if end_idx == -1:
                self._hash = ''
            else:
                start_idx = self._src.rfind('/', 0, end_idx)
                self._hash = self._src[start_idx + 1 : end_idx]

        return self._hash


class Postlog(object):
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
        post_time (datetime.datetime): 发帖时间
        op_user_name (str): 操作人用户名
        op_time (datetime.datetime): 操作时间
    """

    __slots__ = [
        '_text',
        '_title',
        '_medias',
        '_tid',
        '_pid',
        '_op_type',
        '_post_portrait',
        '_post_time',
        '_op_user_name',
        '_op_time',
    ]

    def __init__(self, data_tag: bs4.element.Tag) -> None:
        left_cell_item = data_tag.td

        post_meta_item = left_cell_item.find('div', class_='post_meta')
        post_user_item = post_meta_item.div
        self._post_portrait = post_user_item.a['href'][14:-17]
        post_time_item = post_meta_item.time
        self._post_time = datetime.datetime.strptime(post_time_item.text, '%m月%d日 %H:%M')

        post_content_item = post_meta_item.next_sibling
        title_item = post_content_item.h1.a
        url: str = title_item['href']
        self._tid = int(url[3 : url.find('?')])
        pid = int(url[url.rfind('#') + 1 :])
        self._pid = pid if pid != self._tid else 0
        self._title = title_item.string

        text_item = post_content_item.div
        self._text = text_item.string[12:]
        self._medias = [Media_postlog(tag) for tag in text_item.next_sibling('a')]

        op_type_item = left_cell_item.next_sibling
        self._op_type = op_type_item.string

        op_user_name_item = op_type_item.next_sibling
        self._op_user_name = op_user_name_item.string

        op_time_item = op_user_name_item.next_sibling
        self._op_time = datetime.datetime.strptime(op_time_item.text, '%Y-%m-%d%H:%M')

    def __repr__(self) -> str:
        return str(
            {
                'tid': self._tid,
                'pid': self._pid,
                'title': self._title,
                'text': self._text,
                'op_type': self._op_type,
            }
        )

    @property
    def text(self) -> str:
        """
        文本内容
        """

        return self._text

    @property
    def title(self) -> str:
        """
        所在主题帖标题
        """

        return self._title

    @property
    def medias(self) -> List[Media_postlog]:
        """
        媒体列表
        """

        return self._medias

    @property
    def tid(self) -> int:
        """
        所在主题帖id
        """

        return self._tid

    @property
    def pid(self) -> int:
        """
        回复id
        """

        return self._pid

    @property
    def op_type(self) -> str:
        """
        操作类型
        """

        return self._op_type

    @property
    def post_portrait(self) -> str:
        """
        发帖用户的portrait
        """

        return self._post_portrait

    @property
    def post_time(self) -> datetime.datetime:
        """
        发帖时间

        Note:
            不包含年份信息
        """

        return self._post_time

    @property
    def op_user_name(self) -> str:
        """
        操作人用户名
        """

        return self._op_user_name

    @property
    def op_time(self) -> datetime.datetime:
        """
        操作时间
        """

        return self._op_time


class Page_postlog(object):
    """
    页信息

    Attributes:
        current_page (int): 当前页码
        total_page (int): 总页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    __slots__ = [
        '_current_page',
        '_total_page',
        '_total_count',
        '_has_more',
        '_has_prev',
    ]

    def _init(self, data_soup: bs4.BeautifulSoup) -> "Page_postlog":
        page_tag = data_soup.find('div', class_='tbui_pagination').find('li', class_='active')
        self._current_page = int(page_tag.text)
        total_page_item = page_tag.parent.next_sibling
        self._total_page = int(total_page_item.text[1:-1])
        self._has_more = self._current_page < self._total_page
        self._has_prev = self._current_page > 1

        total_count_tag = data_soup.find('div', class_='breadcrumbs')
        self._total_count = int(total_count_tag.em.text)

        return self

    def _init_null(self) -> "Page_postlog":
        self._current_page = 0
        self._total_page = 0
        self._total_count = 0
        self._has_more = False
        self._has_prev = False
        return self

    def __repr__(self) -> str:
        return str(
            {
                'current_page': self._current_page,
                'has_more': self._has_more,
                'has_prev': self._has_prev,
            }
        )

    @property
    def current_page(self) -> int:
        """
        当前页码
        """

        return self._current_page

    @property
    def total_page(self) -> int:
        """
        总页码
        """

        return self._total_page

    @property
    def total_count(self) -> int:
        """
        总计数
        """

        return self._total_count

    @property
    def has_more(self) -> bool:
        """
        是否有后继页
        """

        return self._has_more

    @property
    def has_prev(self) -> bool:
        """
        是否有前驱页
        """

        return self._has_prev


class Postlogs(Containers[Postlog]):
    """
    吧务帖子管理日志表

    Attributes:
        _objs (list[Postlog]): 吧务帖子管理日志表

        page (Page_postlog): 页信息
        has_more (bool): 是否还有下一页
    """

    __slots__ = [
        '_raw_objs',
        '_page',
    ]

    def __init__(self, data_soup: Optional[bs4.BeautifulSoup] = None) -> None:
        if data_soup:
            self._objs = [Postlog(_tag) for _tag in data_soup.find('tbody').find_all('tr')]
            self._page = Page_postlog()._init(data_soup)
        else:
            self._objs = []
            self._page = Page_postlog()._init_null()

    @property
    def page(self) -> Page_postlog:
        """
        页信息
        """

        return self._page

    @property
    def has_more(self) -> bool:
        """
        是否还有下一页
        """

        return self._page._has_more
