__all__ = [
    'FragText',
    'FragEmoji',
    'FragImage',
    'FragAt',
    'FragLink',
    'FragTiebaPlus',
    'FragItem',
    'FragmentUnknown',
    'Fragments',
]

import urllib.parse
from collections.abc import Iterable, Iterator
from typing import List, Optional, Protocol, SupportsIndex, TypeVar, overload

import httpx

from ...._logger import LOG
from ..helper import WEB_BASE_HOST
from .common import TypeMessage


class _Fragment(object):
    """
    内容碎片基类
    """

    __slots__ = ['_raw_data']

    def __init__(self, _raw_data: Optional[TypeMessage] = None) -> None:
        self._raw_data = _raw_data


TypeFragment = TypeVar('TypeFragment', bound=_Fragment)


class FragText(_Fragment):
    """
    纯文本碎片

    Attributes:
        text (str): 文本内容
    """

    __slots__ = ['_text']

    def __init__(self, _raw_data: TypeMessage) -> None:
        super(FragText, self).__init__(_raw_data)
        self._text = _raw_data.text

    def __repr__(self) -> str:
        return str({'text': self.text})

    @property
    def text(self) -> str:
        """
        文本内容
        """

        return self._text


class ProtocolText(Protocol):
    @property
    def text(self) -> str:
        pass


class FragEmoji(_Fragment):
    """
    表情碎片

    Attributes:
        desc (str): 表情描述
    """

    __slots__ = ['_desc']

    def __init__(self, _raw_data: TypeMessage) -> None:
        super(FragEmoji, self).__init__(_raw_data)
        self._desc: str = _raw_data.c

    def __repr__(self) -> str:
        return str({'desc': self.desc})

    @property
    def desc(self) -> str:
        """
        表情描述
        """

        return self._desc


class FragImage(_Fragment):
    """
    图像碎片

    Attributes:
        src (str): 压缩图像链接 宽720px
        origin_src (str): 原图链接
        hash (str): 百度图床hash
        show_width (int): 图像在客户端预览显示的宽度
        show_height (int): 图像在客户端预览显示的高度
    """

    __slots__ = [
        '_src',
        '_origin_src',
        '_origin_size',
        '_hash',
        '_show_width',
        '_show_height',
    ]

    def __init__(self, _raw_data: TypeMessage) -> None:
        super(FragImage, self).__init__(_raw_data)

        self._src = _raw_data.cdn_src or _raw_data.src
        self._origin_src = _raw_data.origin_src
        self._origin_size = _raw_data.origin_size

        self._hash = None
        self._show_width = None
        self._show_height = None

    def __repr__(self) -> str:
        return str({'src': self.src})

    @property
    def src(self) -> str:
        """
        压缩图像链接
        """

        return self._src

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
        """

        return self._origin_size

    @property
    def hash(self) -> str:
        """
        图像的百度图床hash
        """

        if self._hash is None:
            first_qmark_idx = self.src.find('?')
            end_idx = self.src.rfind('.', 0, first_qmark_idx)

            if end_idx == -1:
                self._hash = ''
            else:
                start_idx = self.src.rfind('/', 0, end_idx)
                self._hash = self.src[start_idx + 1 : end_idx]

        return self._hash

    def _init_wh(self) -> None:

        bsize: str = self._raw_data.bsize
        show_width, _, show_height = bsize.partition(',')

        if show_width and show_height:
            self._show_width = int(show_width)
            self._show_height = int(show_height)

        else:
            self._show_width = 0
            self._show_height = 0

    @property
    def show_width(self) -> int:
        """
        图像在客户端显示的宽度
        """

        if self._show_width is None:
            self._init_wh()
        return self._show_width

    @property
    def show_height(self) -> int:
        """
        图像在客户端显示的高度
        """

        if self._show_height is None:
            self._init_wh()
        return self._show_height


class FragAt(_Fragment):
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

    def __init__(self, _raw_data: TypeMessage) -> None:
        super(FragAt, self).__init__(_raw_data)

        self._text = _raw_data.text
        self._user_id = _raw_data.uid

    def __repr__(self) -> str:
        return str(
            {
                'text': self.text,
                'user_id': self.user_id,
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


class FragLink(_Fragment):
    """
    链接碎片

    Attributes:
        text (str): 原链接
        title (str): 链接标题
        raw_url (str): 原链接
        url (httpx.URL): 解析后的链接
        is_external (bool): 是否外部链接
    """

    __slots__ = [
        '_text',
        '_raw_url',
        '_url',
        '_is_external',
    ]

    def __init__(self, _raw_data: TypeMessage) -> None:
        super(FragLink, self).__init__(_raw_data)

        self._text = _raw_data.text
        self._raw_url: str = urllib.parse.unquote(_raw_data.link)

        self._url = None
        self._is_external = None

    def __repr__(self) -> str:
        return str(
            {
                'title': self.title,
                'raw_url': self.raw_url,
            }
        )

    @property
    def text(self) -> str:
        """
        原链接
        """

        return self._raw_url

    @property
    def title(self) -> str:
        """
        链接标题
        """

        return self._text

    @property
    def url(self) -> httpx.URL:
        """
        yarl解析后的链接

        Note:
            外链会在解析前先去除external_perfix前缀
        """

        if self._url is None:
            self._url = httpx.URL(self._raw_url)
        return self._url

    @property
    def raw_url(self) -> str:
        """
        原链接
        """

        return self._raw_url

    @property
    def is_external(self) -> bool:
        """
        是否外部链接
        """

        if self._is_external is None:
            self._is_external = self.url.host != WEB_BASE_HOST
        return self._is_external


class FragTiebaPlus(_Fragment):
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

    def __init__(self, _raw_data: TypeMessage) -> None:
        super(FragTiebaPlus, self).__init__(_raw_data)

        self._text = _raw_data.tiebaplus_info.desc
        self._url = _raw_data.tiebaplus_info.jump_url

    def __repr__(self) -> str:
        return str(
            {
                'text': self.text,
                'url': self.url,
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


class FragItem(_Fragment):
    """
    item碎片

    Attributes:
        text (str): item名称
    """

    __slots__ = ['_text']

    def __init__(self, _raw_data: TypeMessage) -> None:
        super(FragItem, self).__init__(_raw_data)
        self._text = _raw_data.item.item_name

    def __repr__(self) -> str:
        return str({'text': self.text})

    @property
    def text(self) -> str:
        """
        item名称
        """

        return self._text


class FragmentUnknown(_Fragment):
    """
    未知碎片
    """

    __slots__ = []


class Fragments(object):
    """
    内容碎片列表

    Attributes:
        _frags (list[TypeFragment]): 所有碎片的混合列表

        text (str): 文本内容

        texts (list[ProtocolText]): 纯文本碎片列表
        emojis (list[FragEmoji]): 表情碎片列表
        imgs (list[FragImage]): 图像碎片列表
        ats (list[FragAt]): @碎片列表
        links (list[FragLink]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus]): 贴吧plus碎片列表

        has_voice (bool): 是否包含音频
        has_video (bool): 是否包含视频
    """

    __slots__ = [
        '_frags',
        '_text',
        '_texts',
        '_emojis',
        '_imgs',
        '_ats',
        '_links',
        '_tiebapluses',
        '_has_voice',
        '_has_video',
    ]

    def __init__(self, _raw_datas: Optional[Iterable[TypeMessage]] = None) -> None:
        def _init_by_type(_raw_data) -> TypeFragment:
            frag_type: int = _raw_data.type
            # 0纯文本 9电话号 18话题 27百科词条
            if frag_type in [0, 9, 18, 27]:
                fragment = FragText(_raw_data)
            # 11:tid=5047676428
            elif frag_type in [2, 11]:
                fragment = FragEmoji(_raw_data)
                self._emojis.append(fragment)
            # 20:tid=5470214675
            elif frag_type in [3, 20]:
                fragment = FragImage(_raw_data)
                self._imgs.append(fragment)
            elif frag_type == 4:
                fragment = FragAt(_raw_data)
                self._ats.append(fragment)
            elif frag_type == 1:
                fragment = FragLink(_raw_data)
                self._links.append(fragment)
            elif frag_type == 5:  # video
                fragment = FragmentUnknown()
                self._has_video = True
            elif frag_type == 10:
                fragment = FragmentUnknown()
                self._has_voice = True
            # 35|36:tid=7769728331 / 37:tid=7760184147
            elif frag_type in [35, 36, 37]:
                fragment = FragTiebaPlus(_raw_data)
                self._tiebapluses.append(fragment)
            else:
                fragment = FragmentUnknown(_raw_data)
                LOG.warning(f"Unknown fragment type. type={_raw_data.type}")

            return fragment

        self._text: str = None
        self._texts: List[FragText] = None
        self._links: List[FragLink] = []
        self._imgs: List[FragImage] = []
        self._emojis: List[FragEmoji] = []
        self._ats: List[FragAt] = []
        self._tiebapluses: List[FragTiebaPlus] = []

        self._has_video = True
        self._has_voice = True

        if _raw_datas:
            self._frags: List[TypeFragment] = [_init_by_type(frag_proto) for frag_proto in _raw_datas]
        else:
            self._frags = []

    def __repr__(self) -> str:
        return str(self._frags)

    @property
    def text(self) -> str:
        """
        文本内容
        """

        if self._text is None:
            self._text = ''.join([frag.text for frag in self.texts])
        return self._text

    @property
    def texts(self) -> List[ProtocolText]:
        """
        纯文本碎片列表
        """

        if self._texts is None:
            self._texts = [frag for frag in self._frags if hasattr(frag, 'text')]
        return self._texts

    @property
    def emojis(self) -> List[FragEmoji]:
        """
        表情碎片列表
        """

        return self._emojis

    @property
    def imgs(self) -> List[FragImage]:
        """
        图像碎片列表
        """

        return self._imgs

    @property
    def ats(self) -> List[FragAt]:
        """
        @碎片列表
        """

        return self._ats

    @property
    def links(self) -> List[FragLink]:
        """
        链接碎片列表
        """

        return self._links

    @property
    def tiebapluses(self) -> List[FragTiebaPlus]:
        """
        贴吧plus碎片列表
        """

        return self._tiebapluses

    @property
    def has_voice(self) -> bool:
        """
        是否包含音频
        """

        return self._has_voice

    @property
    def has_video(self) -> bool:
        """
        是否包含视频
        """

        return self._has_video

    def __iter__(self) -> Iterator[TypeFragment]:
        return self._frags.__iter__()

    @overload
    def __getitem__(self, idx: SupportsIndex) -> TypeFragment:
        ...

    @overload
    def __getitem__(self, idx: slice) -> List[TypeFragment]:
        ...

    def __getitem__(self, idx):
        return self._frags.__getitem__(idx)

    def __setitem__(self, idx, val) -> None:
        raise NotImplementedError

    def __delitem__(self, idx) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        return self._frags.__len__()

    def __bool__(self) -> bool:
        return bool(self._frags)
