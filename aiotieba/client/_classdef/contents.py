import urllib.parse
from typing import Protocol, TypeVar

import yarl

from .._helper import CHECK_URL_PERFIX, removeprefix
from .common import TypeMessage

TypeFragment = TypeVar('TypeFragment')


class FragText(object):
    """
    纯文本碎片

    Attributes:
        text (str): 文本内容
    """

    __slots__ = ['_text']

    def __init__(self, data_proto: TypeMessage) -> None:
        self._text = data_proto.text

    def __repr__(self) -> str:
        return str({'text': self._text})

    @property
    def text(self) -> str:
        """
        文本内容
        """

        return self._text


class TypeFragText(Protocol):
    @property
    def text(self) -> str:
        """
        文本内容
        """
        pass


class FragEmoji(object):
    """
    表情碎片

    Attributes:
        desc (str): 表情描述
    """

    __slots__ = ['_desc']

    def __init__(self, data_proto: TypeMessage) -> None:
        self._desc = data_proto.c

    def __repr__(self) -> str:
        return str({'desc': self.desc})

    @property
    def desc(self) -> str:
        """
        表情描述
        """

        return self._desc


class TypeFragEmoji(Protocol):
    @property
    def desc(self) -> str:
        """
        表情描述
        """
        pass


class FragImage(object):
    """
    图像碎片

    Attributes:
        src (str): 小图链接
        big_src (str): 大图链接
        origin_src (str): 原图链接
        origin_size (int): 原图大小
        show_width (int): 图像在客户端预览显示的宽度
        show_height (int): 图像在客户端预览显示的高度
        hash (str): 百度图床hash
    """

    __slots__ = [
        '_src',
        '_big_src',
        '_origin_src',
        '_origin_size',
        '_show_width',
        '_show_height',
        '_hash',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._src = data_proto.cdn_src
        self._big_src = data_proto.big_cdn_src
        self._origin_src = data_proto.origin_src
        self._origin_size = data_proto.origin_size

        show_width, _, show_height = data_proto.bsize.partition(',')
        self._show_width = int(show_width)
        self._show_height = int(show_height)

        self._hash = None

    def __repr__(self) -> str:
        return str(
            {
                'src': self.src,
                'show_width': self._show_width,
                'show_height': self._show_height,
            }
        )

    @property
    def src(self) -> str:
        """
        小图链接

        Note:
            宽720px
        """

        return self._src

    @property
    def big_src(self) -> str:
        """
        大图链接

        Note:
            宽960px
        """

        return self._big_src

    @property
    def origin_src(self) -> str:
        """
        原图链接
        """

        return self._origin_src

    @property
    def origin_size(self) -> int:
        """
        原图大小

        Note:
            以字节为单位
        """

        return self._origin_size

    @property
    def show_width(self) -> int:
        """
        图像在客户端显示的宽度
        """

        return self._show_width

    @property
    def show_height(self) -> int:
        """
        图像在客户端显示的高度
        """

        return self._show_height

    @property
    def hash(self) -> str:
        """
        图像的百度图床hash
        """

        if self._hash is None:
            first_qmark_idx = self._src.find('?')
            end_idx = self._src.rfind('.', 0, first_qmark_idx)

            if end_idx == -1:
                self._hash = ''
            else:
                start_idx = self._src.rfind('/', 0, end_idx)
                self._hash = self._src[start_idx + 1 : end_idx]

        return self._hash


class TypeFragImage(Protocol):
    @property
    def src(self) -> str:
        """
        小图链接
        """
        pass

    @property
    def origin_src(self) -> str:
        """
        原图链接
        """
        pass

    @property
    def hash(self) -> str:
        """
        图像的百度图床hash
        """
        pass


class FragAt(object):
    """
    @碎片

    Attributes:
        text (str): 被@用户的昵称 含@
        user_id (int): 被@用户的user_id
    """

    __slots__ = [
        '_text',
        '_user_id',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._text = data_proto.text
        self._user_id = data_proto.uid

    def __repr__(self) -> str:
        return str(
            {
                'text': self._text,
                'user_id': self._user_id,
            }
        )

    @property
    def text(self) -> str:
        """
        被@用户的昵称 含@
        """

        return self._text

    @property
    def user_id(self) -> int:
        """
        被@用户的user_id
        """

        return self._user_id


class TypeFragAt(Protocol):
    @property
    def text(self) -> str:
        """
        被@用户的昵称 含@
        """
        pass

    @property
    def user_id(self) -> int:
        """
        被@用户的user_id
        """
        pass


class FragLink(object):
    """
    链接碎片

    Attributes:
        text (str): 原链接
        title (str): 链接标题
        raw_url (str): 原链接
        url (yarl.URL): 解析后的链接
        is_external (bool): 是否外部链接
    """

    __slots__ = [
        '_title',
        '_raw_url',
        '_url',
        '_is_external',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._title = data_proto.text

        self._raw_url = data_proto.link
        self._is_external = self._raw_url.startswith(CHECK_URL_PERFIX)
        if self._is_external:
            self._raw_url = urllib.parse.unquote(removeprefix(self._raw_url, CHECK_URL_PERFIX))

        self._url = None

    def __repr__(self) -> str:
        return str(
            {
                'title': self._title,
                'raw_url': self._raw_url,
                'is_external': self._is_external,
            }
        )

    @property
    def text(self) -> str:
        """
        原链接

        Note:
            外链会在解析前先去除CHECK_URL_PERFIX前缀
        """

        return self._raw_url

    @property
    def title(self) -> str:
        """
        链接标题
        """

        return self._title

    @property
    def url(self) -> yarl.URL:
        """
        yarl解析后的链接

        Note:
            外链会在解析前先去除CHECK_URL_PERFIX前缀
        """

        if self._url is None:
            self._url = yarl.URL(self._raw_url)
        return self._url

    @property
    def raw_url(self) -> str:
        """
        原链接

        Note:
            外链会在解析前先去除CHECK_URL_PERFIX前缀
        """

        return self._raw_url

    @property
    def is_external(self) -> bool:
        """
        是否外部链接
        """

        return self._is_external


class TypeFragLink(Protocol):
    @property
    def text(self) -> str:
        """
        原链接
        """
        pass

    @property
    def title(self) -> str:
        """
        链接标题
        """
        pass

    @property
    def url(self) -> yarl.URL:
        """
        yarl解析后的链接

        Note:
            外链会在解析前先去除external_perfix前缀
        """
        pass

    @property
    def raw_url(self) -> str:
        """
        原链接
        """
        pass

    @property
    def is_external(self) -> bool:
        """
        是否外部链接
        """
        pass


class FragTiebaPlus(object):
    """
    贴吧plus广告碎片

    Attributes:
        text (str): 贴吧plus广告描述
        url (str): 贴吧plus广告跳转链接
    """

    __slots__ = [
        '_text',
        '_url',
    ]

    def __init__(self, data_proto: TypeMessage) -> None:
        self._text = data_proto.tiebaplus_info.desc
        self._url = data_proto.tiebaplus_info.jump_url

    def __repr__(self) -> str:
        return str(
            {
                'text': self._text,
                'url': self._url,
            }
        )

    @property
    def text(self) -> str:
        """
        贴吧plus广告描述
        """

        return self._text

    @property
    def url(self) -> str:
        """
        贴吧plus广告跳转链接
        """

        return self._url


class TypeFragTiebaPlus(Protocol):
    @property
    def text(self) -> str:
        """
        贴吧plus广告描述
        """
        pass

    @property
    def url(self) -> str:
        """
        贴吧plus广告跳转链接
        """
        pass


class FragItem(object):
    """
    item碎片

    Attributes:
        text (str): item名称
    """

    __slots__ = ['_text']

    def __init__(self, data_proto: TypeMessage) -> None:
        self._text = data_proto.item.item_name

    def __repr__(self) -> str:
        return str({'text': self._text})

    @property
    def text(self) -> str:
        """
        item名称
        """

        return self._text


class TypeFragItem(Protocol):
    @property
    def text(self) -> str:
        """
        item名称
        """
        pass


class FragmentUnknown(object):
    """
    未知碎片
    """

    __slots__ = ['_data']

    def __init__(self, data=None) -> None:
        self._data = data

    def __repr__(self) -> str:
        return str({'data': self._data})

    @property
    def data(self):
        """
        原始数据
        """

        return self._data


class TypeFragmentUnknown(Protocol):
    @property
    def data(self):
        """
        原始数据
        """
        pass
