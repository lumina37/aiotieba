import dataclasses as dcs
from functools import cached_property
from typing import List

from ...enums import Gender, PrivLike, PrivReply
from ...exception import TbErrorExt
from ...helper import removeprefix
from .._classdef import Containers, TypeMessage
from .._classdef.contents import (
    FragAt,
    FragEmoji,
    FragLink,
    FragText,
    FragTiebaPlus,
    FragVoice,
    TypeFragment,
    TypeFragText,
)

FragText_c = FragText_cp = FragText
FragEmoji_c = FragEmoji_cp = FragEmoji
FragAt_c = FragAt_cp = FragAt
FragLink_c = FragLink_cp = FragLink
FragTiebaPlus_c = FragTiebaPlus_cp = FragTiebaPlus
FragVoice_c = FragVoice_cp = FragVoice


@dcs.dataclass
class Contents_c(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_c]): 表情碎片列表
        ats (list[FragAt_c]): @碎片列表
        links (list[FragLink_c]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_c]): 贴吧plus碎片列表
        voice (FragVoice_c): 音频碎片
    """

    texts: List[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: List[FragEmoji_c] = dcs.field(default_factory=list, repr=False)
    ats: List[FragAt_c] = dcs.field(default_factory=list, repr=False)
    links: List[FragLink_c] = dcs.field(default_factory=list, repr=False)
    tiebapluses: List[FragTiebaPlus_c] = dcs.field(default_factory=list, repr=False)
    voice: FragVoice_c = dcs.field(default_factory=FragVoice_c, repr=False)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Contents_c":
        content_protos = data_proto.content

        texts = []
        emojis = []
        ats = []
        links = []
        tiebapluses = []
        voice = FragVoice_c()

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_c.from_tbdata(proto)
                    texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_c.from_tbdata(proto)
                    emojis.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_c.from_tbdata(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_c.from_tbdata(proto)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 10:  # voice
                    frag = FragVoice_c.from_tbdata(proto)
                    nonlocal voice
                    voice = frag
                    yield frag
                # 35|36:tid=7769728331 / 37:tid=7760184147
                elif _type in [35, 36, 37]:
                    frag = FragTiebaPlus_c.from_tbdata(proto)
                    tiebapluses.append(frag)
                    texts.append(frag)
                    yield frag
                # outdated tiebaplus
                elif _type == 34:
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning(f"Unknown fragment type. type={_type} proto={proto}")

        objs = list(_frags())

        return Contents_c(objs, texts, emojis, ats, links, tiebapluses, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class UserInfo_c:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        level (int): 等级
        gender (Gender): 性别
        icons (list[str]): 印记信息

        is_bawu (bool): 是否吧务
        is_vip (bool): 是否超级会员
        is_god (bool): 是否大神
        priv_like (PrivLike): 关注吧列表的公开状态
        priv_reply (PrivReply): 帖子评论权限

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name_new: str = ''

    level: int = 0
    gender: Gender = Gender.UNKNOWN
    icons: List[str] = dcs.field(default_factory=list)

    is_bawu: bool = False
    is_vip: bool = False
    is_god: bool = False
    priv_like: PrivLike = PrivLike.PUBLIC
    priv_reply: PrivReply = PrivReply.ALL

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_c":
        user_id = data_proto.id
        portrait = data_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.name
        nick_name_new = data_proto.name_show
        level = data_proto.level_id
        gender = Gender(data_proto.gender)
        icons = [name for i in data_proto.iconinfo if (name := i.name)]
        is_bawu = bool(data_proto.is_bawu)
        is_vip = bool(data_proto.new_tshow_icon)
        is_god = bool(data_proto.new_god_data.status)
        priv_like = PrivLike(priv_like) if (priv_like := data_proto.priv_sets.like) else PrivLike.PUBLIC
        priv_reply = PrivReply(priv_reply) if (priv_reply := data_proto.priv_sets.reply) else PrivReply.ALL
        return UserInfo_c(
            user_id,
            portrait,
            user_name,
            nick_name_new,
            level,
            gender,
            icons,
            is_bawu,
            is_vip,
            is_god,
            priv_like,
            priv_reply,
        )

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_c") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_new}/{self.portrait}"
        else:
            return str(self.user_id)


@dcs.dataclass
class Comment:
    """
    楼中楼信息

    Attributes:
        text (str): 文本内容
        contents (Contents_c): 正文内容碎片列表

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        ppid (int): 所在楼层id
        pid (int): 楼中楼id
        user (UserInfo_c): 发布者的用户信息
        author_id (int): 发布者的user_id
        reply_to_id (int): 被回复者的user_id

        floor (int): 所在楼层数
        agree (int): 点赞数
        disagree (int): 点踩数
        create_time (int): 创建时间 10位时间戳 以秒为单位
        is_thread_author (bool): 是否楼主
    """

    contents: Contents_c = dcs.field(default_factory=Contents_c)

    fid: int = 0
    fname: str = ''
    tid: int = 0
    ppid: int = 0
    pid: int = 0
    user: UserInfo_c = dcs.field(default_factory=UserInfo_c)
    reply_to_id: int = 0

    floor: int = 0
    agree: int = 0
    disagree: int = 0
    create_time: int = 0
    is_thread_author: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> None:
        contents = Contents_c.from_tbdata(data_proto)

        reply_to_id = 0
        if contents:
            first_frag = contents[0]
            if (
                isinstance(first_frag, FragText_c)
                and first_frag.text == '回复 '
                and (reply_to_id := data_proto.content[1].uid)
            ):
                reply_to_id = reply_to_id
                if isinstance(contents[1], FragAt_c):
                    del contents.ats[0]
                contents.objs = contents.objs[2:]
                contents.texts = contents.texts[2:]
                if contents.texts:
                    first_text_frag = contents.texts[0]
                    first_text_frag.text = removeprefix(first_text_frag.text, ' :')

        pid = data_proto.id
        user = UserInfo_c.from_tbdata(data_proto.author)
        agree = data_proto.agree.agree_num
        disagree = data_proto.agree.disagree_num
        create_time = data_proto.time

        return Comment(contents, 0, '', 0, 0, pid, user, reply_to_id, 0, agree, disagree, create_time, False)

    def __eq__(self, obj: "Comment") -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @property
    def text(self) -> str:
        return self.contents.text

    @property
    def author_id(self) -> int:
        return self.user.user_id


@dcs.dataclass
class Page_c:
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
    def from_tbdata(data_proto: TypeMessage) -> "Page_c":
        page_size = data_proto.page_size
        current_page = data_proto.current_page
        total_page = data_proto.total_page
        total_count = data_proto.total_count
        has_more = current_page < total_page
        has_prev = current_page > 1
        return Page_c(page_size, current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class Forum_c:
    """
    吧信息

    Attributes:
        fid (int): 贴吧id
        fname (str): 贴吧名
    """

    fid: int = 0
    fname: str = ''

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Forum_c":
        fid = data_proto.id
        fname = data_proto.name
        return Forum_c(fid, fname)


@dcs.dataclass
class UserInfo_ct:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        level (int): 等级

        is_god (bool): 是否大神

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name_new: str = ''

    level: int = 0
    is_god: bool = False

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_ct":
        user_id = data_proto.id
        portrait = data_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.name
        nick_name_new = data_proto.name_show
        level = data_proto.level_id
        is_god = bool(data_proto.new_god_data.status)
        return UserInfo_ct(user_id, portrait, user_name, nick_name_new, level, is_god)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_ct") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_new}/{self.portrait}"
        else:
            return str(self.user_id)


@dcs.dataclass
class Thread_c:
    """
    主题帖信息

    Attributes:
        title (str): 标题

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 主题帖tid
        user (UserInfo_ct): 发布者的用户信息
        author_id (int): 发布者的user_id

        type (int): 帖子类型
        is_help (bool): 是否为求助帖

        reply_num (int): 回复数
    """

    title: str = ''

    fid: int = 0
    fname: str = ''
    tid: int = 0
    user: UserInfo_ct = dcs.field(default_factory=UserInfo_ct)

    type: int = 0

    reply_num: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Thread_c":
        title = data_proto.title
        tid = data_proto.id
        user = UserInfo_ct.from_tbdata(data_proto.author)
        type_ = data_proto.thread_type
        reply_num = data_proto.reply_num
        return Thread_c(title, 0, '', tid, user, type_, reply_num)

    def __eq__(self, obj: "Thread_c") -> bool:
        return self.tid == obj.tid

    def __hash__(self) -> int:
        return self.tid

    @property
    def author_id(self) -> int:
        return self.user.user_id

    @property
    def is_help(self) -> bool:
        return self.type == 71


@dcs.dataclass
class FragImage_cp:
    """
    图像碎片

    Attributes:
        src (str): 小图链接 宽720px 一定是静态图
        big_src (str): 大图链接 宽960px
        origin_src (str): 原图链接
        origin_size (int): 原图大小
        show_width (int): 图像在客户端预览显示的宽度
        show_height (int): 图像在客户端预览显示的高度
        hash (str): 百度图床hash
    """

    src: str = ""
    big_src: str = ""
    origin_src: str = ""
    origin_size: int = 0
    show_width: int = 0
    show_height: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "FragImage_cp":
        src = data_proto.cdn_src
        big_src = data_proto.big_cdn_src
        origin_src = data_proto.origin_src
        origin_size = data_proto.origin_size

        show_width, _, show_height = data_proto.bsize.partition(',')
        show_width = int(show_width)
        show_height = int(show_height)

        return FragImage_cp(src, big_src, origin_src, origin_size, show_width, show_height)

    @property
    def hash(self) -> str:
        first_qmark_idx = self.src.find('?')
        end_idx = self.src.rfind('.', 0, first_qmark_idx)

        if end_idx == -1:
            hash_ = ''
        else:
            start_idx = self.src.rfind('/', 0, end_idx)
            hash_ = self.src[start_idx + 1 : end_idx]

        return hash_


@dcs.dataclass
class Contents_cp(Containers[TypeFragment]):
    """
    内容碎片列表

    Attributes:
        objs (list[TypeFragment]): 所有内容碎片的混合列表

        text (str): 文本内容

        texts (list[TypeFragText]): 纯文本碎片列表
        emojis (list[FragEmoji_cp]): 表情碎片列表
        imgs (list[FragImage_cp]): 图像碎片列表
        ats (list[FragAt_cp]): @碎片列表
        links (list[FragLink_cp]): 链接碎片列表
        tiebapluses (list[FragTiebaPlus_cp]): 贴吧plus碎片列表
        voice (FragVoice_cp): 音频碎片
    """

    texts: List[TypeFragText] = dcs.field(default_factory=list, repr=False)
    emojis: List[FragEmoji_cp] = dcs.field(default_factory=list, repr=False)
    imgs: List[FragImage_cp] = dcs.field(default_factory=list, repr=False)
    ats: List[FragAt_cp] = dcs.field(default_factory=list, repr=False)
    links: List[FragLink_cp] = dcs.field(default_factory=list, repr=False)
    tiebapluses: List[FragTiebaPlus_cp] = dcs.field(default_factory=list, repr=False)
    voice: FragVoice_cp = dcs.field(default_factory=FragVoice_cp, repr=False)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Contents_cp":
        content_protos = data_proto.content

        texts = []
        emojis = []
        imgs = []
        ats = []
        links = []
        tiebapluses = []
        voice = FragVoice_cp()

        def _frags():
            for proto in content_protos:
                _type = proto.type
                # 0纯文本 9电话号 18话题 27百科词条
                if _type in [0, 9, 18, 27]:
                    frag = FragText_cp.from_tbdata(proto)
                    texts.append(frag)
                    yield frag
                # 11:tid=5047676428
                elif _type in [2, 11]:
                    frag = FragEmoji_cp.from_tbdata(proto)
                    emojis.append(frag)
                    yield frag
                # 20:tid=5470214675
                elif _type in [3, 20]:
                    frag = FragImage_cp.from_tbdata(proto)
                    imgs.append(frag)
                    yield frag
                elif _type == 4:
                    frag = FragAt_cp.from_tbdata(proto)
                    ats.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 1:
                    frag = FragLink_cp.from_tbdata(proto)
                    links.append(frag)
                    texts.append(frag)
                    yield frag
                elif _type == 10:  # voice
                    frag = FragVoice_cp.from_tbdata(proto)
                    nonlocal voice
                    voice = frag
                    yield frag
                # 35|36:tid=7769728331 / 37:tid=7760184147
                elif _type in [35, 36, 37]:
                    frag = FragTiebaPlus_cp.from_tbdata(proto)
                    tiebapluses.append(frag)
                    texts.append(frag)
                    yield frag
                # outdated tiebaplus
                elif _type == 34:
                    continue
                else:
                    from ...logging import get_logger as LOG

                    LOG().warning(f"Unknown fragment type. type={_type} proto={proto}")

        objs = list(_frags())

        return Contents_cp(objs, texts, emojis, imgs, ats, links, tiebapluses, voice)

    @cached_property
    def text(self) -> str:
        text = "".join(frag.text for frag in self.texts)
        return text


@dcs.dataclass
class UserInfo_cp:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        level (int): 等级
        gender (Gender): 性别

        is_bawu (bool): 是否吧务
        is_vip (bool): 是否超级会员
        is_god (bool): 是否大神
        priv_like (PrivLike): 关注吧列表的公开状态
        priv_reply (PrivReply): 帖子评论权限

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ''
    user_name: str = ''
    nick_name_new: str = ''

    level: int = 0
    gender: Gender = Gender.UNKNOWN

    is_bawu: bool = False
    is_vip: bool = False
    is_god: bool = False
    priv_like: PrivLike = PrivLike.PUBLIC
    priv_reply: PrivReply = PrivReply.ALL

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "UserInfo_cp":
        user_id = data_proto.id
        portrait = data_proto.portrait
        if '?' in portrait:
            portrait = portrait[:-13]
        user_name = data_proto.name
        nick_name_new = data_proto.name_show
        level = data_proto.level_id
        gender = Gender(data_proto.gender)
        is_bawu = bool(data_proto.is_bawu)
        is_vip = bool(data_proto.new_tshow_icon)
        is_god = bool(data_proto.new_god_data.status)
        priv_like = PrivLike(priv_like) if (priv_like := data_proto.priv_sets.like) else PrivLike.PUBLIC
        priv_reply = PrivReply(priv_reply) if (priv_reply := data_proto.priv_sets.reply) else PrivReply.ALL
        return UserInfo_cp(
            user_id, portrait, user_name, nick_name_new, level, gender, is_bawu, is_vip, is_god, priv_like, priv_reply
        )

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: "UserInfo_cp") -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_new}/{self.portrait}"
        else:
            return str(self.user_id)


@dcs.dataclass
class Post_c:
    """
    楼层信息

    Attributes:
        text (str): 文本内容
        contents (Contents_cp): 正文内容碎片列表
        sign (str): 小尾巴文本内容

        fid (int): 所在吧id
        fname (str): 所在贴吧名
        tid (int): 所在主题帖id
        pid (int): 回复id
        user (UserInfo_cp): 发布者的用户信息
        author_id (int): 发布者的user_id

        floor (int): 楼层数
        create_time (int): 创建时间 10位时间戳 以秒为单位
    """

    contents: Contents_cp = dcs.field(default_factory=Contents_cp)
    sign: str = ""

    fid: int = 0
    fname: str = ''
    tid: int = 0
    pid: int = 0
    user: UserInfo_cp = dcs.field(default_factory=UserInfo_cp)

    floor: int = 0
    create_time: int = 0

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Post_c":
        contents = Contents_cp.from_tbdata(data_proto)
        sign = "".join(p.text for p in data_proto.signature.content if p.type == 0)
        pid = data_proto.id
        user = UserInfo_cp.from_tbdata(data_proto.author)
        floor = data_proto.floor
        create_time = data_proto.time
        return Post_c(contents, sign, 0, '', 0, pid, user, floor, create_time)

    def __eq__(self, obj: "Post_c") -> bool:
        return self.pid == obj.pid

    def __hash__(self) -> int:
        return self.pid

    @cached_property
    def text(self) -> str:
        if self.sign:
            text = f'{self.contents.text}\n{self.sign}'
        else:
            text = self.contents.text
        return text

    @property
    def author_id(self) -> int:
        return self.user.user_id


@dcs.dataclass
class Comments(TbErrorExt, Containers[Comment]):
    """
    楼中楼列表

    Attributes:
        objs (list[Comment]): 楼中楼列表
        err (Exception | None): 捕获的异常

        page (Page_c): 页信息
        has_more (bool): 是否还有下一页

        forum (Forum_c): 所在吧信息
        thread (Thread_c): 所在主题帖信息
        post (Post_c): 所在楼层信息
    """

    page: Page_c = dcs.field(default_factory=Page_c)
    forum: Forum_c = dcs.field(default_factory=Forum_c)
    thread: Thread_c = dcs.field(default_factory=Thread_c)
    post: Post_c = dcs.field(default_factory=Post_c)

    @staticmethod
    def from_tbdata(data_proto: TypeMessage) -> "Comments":
        page = Page_c.from_tbdata(data_proto.page)
        forum = Forum_c.from_tbdata(data_proto.forum)
        thread = Thread_c.from_tbdata(data_proto.thread)
        thread.fid = forum.fid
        thread.fname = forum.fname
        post = Post_c.from_tbdata(data_proto.post)
        post.fid = thread.fid
        post.fname = thread.fname
        post.tid = thread.tid

        objs = [Comment.from_tbdata(p) for p in data_proto.subpost_list]
        for comment in objs:
            comment.fid = forum.fid
            comment.fname = forum.fname
            comment.tid = thread.tid
            comment.ppid = post.pid
            comment.floor = post.floor
            comment.is_thread_author = thread.author_id == comment.author_id

        return Comments(objs, page, forum, thread, post)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
