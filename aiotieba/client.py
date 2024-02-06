import asyncio
import logging
import socket
from typing import TYPE_CHECKING, List, Literal, Optional, Union

import aiohttp
import yarl

from .api import (
    add_bawu_blacklist,
    add_blacklist_old,
    add_post,
    agree,
    agree_vimage,
    block,
    del_bawu_blacklist,
    del_blacklist_old,
    del_post,
    del_posts,
    del_thread,
    del_threads,
    dislike_forum,
    follow_forum,
    follow_user,
    get_ats,
    get_bawu_blacklist,
    get_bawu_info,
    get_bawu_postlogs,
    get_bawu_userlogs,
    get_blacklist,
    get_blacklist_old,
    get_blocks,
    get_cid,
    get_comments,
    get_dislike_forums,
    get_fans,
    get_fid,
    get_follow_forums,
    get_follows,
    get_forum_detail,
    get_god_threads,
    get_group_msg,
    get_images,
    get_member_users,
    get_posts,
    get_rank_users,
    get_recom_status,
    get_recovers,
    get_replys,
    get_self_follow_forums,
    get_selfinfo_initNickname,
    get_square_forums,
    get_statistics,
    get_tab_map,
    get_threads,
    get_uinfo_getuserinfo_app,
    get_uinfo_getUserInfo_web,
    get_uinfo_panel,
    get_uinfo_user_json,
    get_unblock_appeals,
    get_user_contents,
    good,
    handle_unblock_appeals,
    init_z_id,
    login,
    move,
    profile,
    recommend,
    recover,
    remove_fan,
    search_post,
    send_msg,
    set_blacklist,
    set_msg_readed,
    set_nickname_old,
    set_profile,
    set_thread_privacy,
    sign_forum,
    sign_growth,
    sync,
    tieba_uid2user_info,
    top,
    unblock,
    undislike_forum,
    unfollow_forum,
    unfollow_user,
    ungood,
)
from .api._classdef import UserInfo
from .config import ProxyConfig, TimeoutConfig
from .core import Account, HttpCore, NetCore, WsCore
from .enums import BawuSearchType, BlacklistType, Gender, GroupType, PostSortType, ReqUInfo, ThreadSortType, WsStatus
from .exception import BoolResponse, IntResponse, StrResponse
from .helper.cache import ForumInfoCache
from .helper.utils import handle_exception, is_portrait
from .logging import get_logger as LOG
from .typing import TypeUserInfo

if TYPE_CHECKING:
    import datetime


def _try_websocket(func):
    async def awrapper(self: "Client", *args, **kwargs):
        if self._try_ws:
            await self.init_websocket()
        return await func(self, *args, **kwargs)

    awrapper.__name__ = func.__name__

    return awrapper


def _force_websocket(func):
    async def awrapper(self: "Client", *args, **kwargs):
        await self.init_websocket()
        return await func(self, *args, **kwargs)

    awrapper.__name__ = func.__name__

    return awrapper


class Client(object):
    """
    贴吧客户端

    Args:
        BDUSS (str, optional): BDUSS. Defaults to ''.
        STOKEN (str, optional): STOKEN. Defaults to ''.
        account (Account, optional): Account实例 该字段会覆盖前两个参数. Defaults to None.
        try_ws (bool, optional): 尝试使用websocket接口. Defaults to False.
        proxy (bool | ProxyConfig, optional): True则使用环境变量代理 False则禁用代理 输入ProxyConfig实例以手动配置代理. Defaults to False.
        timeout (TimeoutConfig, optional): 超时配置. Defaults to TimeoutConfig().
        loop (asyncio.AbstractEventLoop, optional): 事件循环. Defaults to None.
    """

    __slots__ = [
        '_connector',
        'account',
        '_http_core',
        '_ws_core',
        '_try_ws',
        '_user',
    ]

    def __init__(
        self,
        BDUSS: str = '',
        STOKEN: str = '',
        *,
        account: Optional[Account] = None,
        try_ws: bool = False,
        proxy: Union[bool, ProxyConfig] = False,
        timeout: TimeoutConfig = TimeoutConfig,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        if loop is None:
            loop = asyncio.get_running_loop()

        if not isinstance(timeout, TimeoutConfig):
            timeout = TimeoutConfig()

        connector = aiohttp.TCPConnector(
            ttl_dns_cache=timeout.dns_ttl,
            family=socket.AF_INET,
            keepalive_timeout=timeout.http_keepalive,
            limit=0,
            ssl=False,
            loop=loop,
        )
        self._connector = connector

        if proxy is True:
            proxy = ProxyConfig.from_env()
        else:
            proxy = ProxyConfig()

        if isinstance(account, Account):
            account = account
        else:
            account = Account(BDUSS, STOKEN)

        self.account = account
        net_core = NetCore(connector, timeout, proxy)
        self._http_core = HttpCore(account, net_core, loop)
        self._ws_core = WsCore(account, net_core, loop)

        self._try_ws = try_ws

        self._user = profile.UserInfo_pf()

    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(self, exc_type=None, exc_val=None, exc_tb=None) -> None:
        await self._ws_core.close()
        await self._connector.close()

    def __hash__(self) -> int:
        return hash(self.account.BDUSS)

    def __eq__(self, obj: "Client") -> bool:
        return self.account.BDUSS == obj.account.BDUSS

    @handle_exception(BoolResponse)
    async def init_websocket(self) -> BoolResponse:
        """
        初始化websocket

        Returns:
            BoolResponse: True无须执行 False失败
        """

        if self._ws_core.status == WsStatus.CLOSED:
            try:
                await self._ws_core.connect()
                await self.__upload_sec_key()
            except BaseException:
                self._ws_core._status = WsStatus.CLOSED
                raise

        return BoolResponse()

    async def __upload_sec_key(self) -> None:
        from .api import init_websocket
        from .core.websocket import MsgIDPair

        groups = await init_websocket.request(self._ws_core)

        mid_manager = self._ws_core.mid_manager
        for group in groups:
            if group.group_type == GroupType.PRIVATE_MSG:
                mid_manager.priv_gid = group.group_id
        mid_manager.gid2mid = {g.group_id: MsgIDPair(g.last_msg_id, g.last_msg_id) for g in groups}

        self._ws_core._status = WsStatus.OPEN

    async def __init_tbs(self) -> None:
        if self.account.tbs:
            return
        await self.__login()

    @handle_exception(profile.UserInfo_pf)
    async def get_self_info(self, require: ReqUInfo = ReqUInfo.ALL) -> profile.UserInfo_pf:
        """
        获取本账号信息

        Args:
            require (ReqUInfo): 指示需要获取的字段

        Returns:
            TypeUserInfo: 用户信息
        """

        if not self._user.user_id:
            if require & ReqUInfo.BASIC:
                await self.__login()
        if not self._user.tieba_uid:
            if require & (ReqUInfo.TIEBA_UID | ReqUInfo.NICK_NAME):
                await self.__get_selfinfo_initNickname()

        return self._user

    async def __login(self) -> None:
        user, tbs = await login.request(self._http_core)

        self._user.user_id = user.user_id
        self._user.portrait = user.portrait
        self._user.user_name = user.user_name
        self.account.tbs = tbs

    async def __init_client_id(self) -> None:
        if self.account.client_id:
            return
        await self.__sync()

    async def __init_sample_id(self) -> None:
        if self.account.sample_id:
            return
        await self.__sync()

    async def __sync(self) -> None:
        client_id, sample_id = await sync.request(self._http_core)
        self.account.client_id = client_id
        self.account.sample_id = sample_id

    async def __init_z_id(self) -> None:
        if self.account.z_id:
            return

        z_id = await init_z_id.request(self._http_core)
        self.account.z_id = z_id

    @handle_exception(get_forum_detail.Forum_detail)
    @_try_websocket
    async def get_forum_detail(self, fname_or_fid: Union[str, int]) -> get_forum_detail.Forum_detail:
        """
        通过forum_id获取贴吧信息

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            Forum_detail: 贴吧信息
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        if self._ws_core.status == WsStatus.OPEN:
            return await get_forum_detail.request_ws(self._ws_core, fid)

        return await get_forum_detail.request_http(self._http_core, fid)

    async def __get_fid(self, fname: str) -> int:
        if fid := ForumInfoCache.get_fid(fname):
            return fid

        fid = await get_fid.request(self._http_core, fname)
        ForumInfoCache.add_forum(fname, fid)

        return fid

    @handle_exception(IntResponse)
    async def get_fid(self, fname: str) -> IntResponse:
        """
        通过贴吧名获取forum_id

        Args:
            fname (str): 贴吧名

        Returns:
            IntResponse: forum_id
        """

        fid = await self.__get_fid(fname)
        return IntResponse(fid)

    async def __get_fname(self, fid: int) -> str:
        if fname := ForumInfoCache.get_fname(fid):
            return fname

        fdetail = await self.get_forum_detail(fid)
        fname = fdetail.fname

        if fname:
            ForumInfoCache.add_forum(fname, fid)

        return fname

    @handle_exception(StrResponse)
    async def get_fname(self, fid: int) -> StrResponse:
        """
        通过forum_id获取贴吧名

        Args:
            fid (int): forum_id

        Returns:
            StrResponse: 贴吧名
        """

        fname = await self.__get_fname(fid)
        return StrResponse(fname)

    @handle_exception(get_threads.Threads)
    @_try_websocket
    async def get_threads(
        self,
        fname_or_fid: Union[str, int],
        /,
        pn: int = 1,
        *,
        rn: int = 30,
        sort: ThreadSortType = ThreadSortType.REPLY,
        is_good: bool = False,
    ) -> get_threads.Threads:
        """
        获取首页帖子

        Args:
            fname_or_fid (str | int): 贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30. Max to 100.
            sort (ThreadSortType, optional): HOT热门排序 REPLY按回复时间 CREATE按发布时间 FOLLOW关注的人. Defaults to ThreadSortType.REPLY.
            is_good (bool, optional): True则获取精品区帖子 False则获取普通区帖子. Defaults to False.

        Returns:
            Threads: 帖子列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)

        if self._ws_core.status == WsStatus.OPEN:
            return await get_threads.request_ws(self._ws_core, fname, pn, rn, sort, is_good)

        return await get_threads.request_http(self._http_core, fname, pn, rn, sort, is_good)

    @handle_exception(get_posts.Posts)
    @_try_websocket
    async def get_posts(
        self,
        tid: int,
        /,
        pn: int = 1,
        *,
        rn: int = 30,
        sort: PostSortType = PostSortType.ASC,
        only_thread_author: bool = False,
        with_comments: bool = False,
        comment_sort_by_agree: bool = True,
        comment_rn: int = 4,
    ) -> get_posts.Posts:
        """
        获取主题帖内回复

        Args:
            tid (int): 所在主题帖tid
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30.
            sort (PostSortType, optional): ASC时间顺序 DESC时间倒序 HOT热门序. Defaults to PostSortType.ASC.
            only_thread_author (bool, optional): True则只看楼主 False则请求全部. Defaults to False.
            with_comments (bool, optional): True则同时请求高赞楼中楼 False则返回的Post.comments字段为空. Defaults to False.
            comment_sort_by_agree (bool, optional): True则楼中楼按点赞数顺序 False则楼中楼按时间顺序. Defaults to True.
            comment_rn (int, optional): 请求的楼中楼数量. Defaults to 4. Max to 50.

        Returns:
            Posts: 回复列表
        """

        if self._ws_core.status == WsStatus.OPEN:
            return await get_posts.request_ws(
                self._ws_core, tid, pn, rn, sort, only_thread_author, with_comments, comment_sort_by_agree, comment_rn
            )

        return await get_posts.request_http(
            self._http_core, tid, pn, rn, sort, only_thread_author, with_comments, comment_sort_by_agree, comment_rn
        )

    @handle_exception(get_comments.Comments)
    @_try_websocket
    async def get_comments(
        self, tid: int, pid: int, /, pn: int = 1, *, is_comment: bool = False
    ) -> get_comments.Comments:
        """
        获取楼中楼回复

        Args:
            tid (int): 所在主题帖tid
            pid (int): 所在楼层的pid或楼中楼的pid
            pn (int, optional): 页码. Defaults to 1.
            is_comment (bool, optional): pid是否指向楼中楼 若指向楼中楼则获取其附近的楼中楼列表. Defaults to False.

        Returns:
            Comments: 楼中楼列表
        """

        if self._ws_core.status == WsStatus.OPEN:
            return await get_comments.request_ws(self._ws_core, tid, pid, pn, is_comment)

        return await get_comments.request_http(self._http_core, tid, pid, pn, is_comment)

    @handle_exception(search_post.Searches)
    async def search_post(
        self,
        fname_or_fid: Union[str, int],
        query: str,
        /,
        pn: int = 1,
        *,
        rn: int = 30,
        query_type: int = 0,
        only_thread: bool = False,
    ) -> search_post.Searches:
        """
        贴吧搜索

        Args:
            fname_or_fid (str | int): 查询的贴吧名或fid 优先贴吧名
            query (str): 查询文本
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30.
            query_type (int, optional): 查询模式 0为全部搜索结果并且app似乎不提供这一模式 1为app时间倒序 2为app相关性排序. Defaults to 0.
            only_thread (bool, optional): 是否仅查询主题帖. Defaults to False.

        Returns:
            Searches: 搜索结果列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)

        return await search_post.request(self._http_core, fname, query, pn, rn, query_type, only_thread)

    @handle_exception(profile.UserInfo_pf)
    @_try_websocket
    async def _get_uinfo_profile(self, uid_or_portrait: Union[str, int]) -> profile.UserInfo_pf:
        """
        接口 https://tiebac.baidu.com/c/u/user/profile

        Args:
            uid_or_portrait (str | int): 用户id user_id / portrait

        Returns:
            UserInfo_pf: 包含最全面的用户信息
        """

        if self._ws_core.status == WsStatus.OPEN:
            return await profile.get_uinfo_profile.request_ws(self._ws_core, uid_or_portrait)

        return await profile.get_uinfo_profile.request_http(self._http_core, uid_or_portrait)

    @handle_exception(get_uinfo_getuserinfo_app.UserInfo_guinfo_app)
    @_try_websocket
    async def _get_uinfo_getuserinfo(self, user_id: int) -> get_uinfo_getuserinfo_app.UserInfo_guinfo_app:
        """
        接口 https://tiebac.baidu.com/c/u/user/getuserinfo

        Args:
            user_id (int): 用户id user_id

        Returns:
            UserInfo_guinfo_app: 包含 user_id / portrait / user_name / nick_name_old / 性别 /
                是否大神 / 是否超级会员
        """

        if self._ws_core.status == WsStatus.OPEN:
            user = await get_uinfo_getuserinfo_app.request_ws(self._ws_core, user_id)

        else:
            user = await get_uinfo_getuserinfo_app.request_http(self._http_core, user_id)
            if (user_id := user.user_id) < 0:
                user.user_id = 0xFFFFFFFF + user_id

        return user

    @handle_exception(get_uinfo_getUserInfo_web.UserInfo_guinfo_web)
    async def _get_uinfo_getUserInfo(self, user_id: int) -> get_uinfo_getUserInfo_web.UserInfo_guinfo_web:
        """
        接口 http://tieba.baidu.com/im/pcmsg/query/getUserInfo

        Args:
            user_id (int): 用户id user_id

        Returns:
            UserInfo_guinfo_web: 包含 user_id / portrait / user_name / nick_name_new

        Note:
            该接口需要BDUSS
        """

        user = await get_uinfo_getUserInfo_web.request(self._http_core, user_id)
        user.user_id = user_id

        return user

    @handle_exception(get_uinfo_user_json.UserInfo_json)
    async def _get_uinfo_user_json(self, user_name: str) -> get_uinfo_user_json.UserInfo_json:
        """
        接口 http://tieba.baidu.com/i/sys/user_json

        Args:
            user_name (str): 用户id user_name

        Returns:
            UserInfo_json: 包含 user_id / portrait / user_name
        """

        user = await get_uinfo_user_json.request(self._http_core, user_name)
        user.user_name = user_name

        return user

    @handle_exception(get_uinfo_panel.UserInfo_panel)
    async def _get_uinfo_panel(self, name_or_portrait: str) -> get_uinfo_panel.UserInfo_panel:
        """
        接口 https://tieba.baidu.com/home/get/panel

        Args:
            name_or_portrait (str): 用户id user_name / portrait

        Returns:
            UserInfo_panel: 包含较全面的用户信息

        Note:
            从2022.08.30开始服务端不再返回user_id字段 请谨慎使用\n
            该接口可判断用户是否被屏蔽\n
            该接口rps阈值较低
        """

        return await get_uinfo_panel.request(self._http_core, name_or_portrait)

    async def get_user_info(self, id_: Union[str, int], /, require: ReqUInfo = ReqUInfo.ALL) -> TypeUserInfo:
        """
        获取用户信息

        Args:
            id_ (str | int): 用户id user_id / portrait / user_name
            require (ReqUInfo): 指示需要获取的字段

        Returns:
            TypeUserInfo: 用户信息
        """

        if not id_:
            LOG().warning("Null input")
            return UserInfo(id_)

        if isinstance(id_, int):
            if require <= ReqUInfo.NICK_NAME:
                # 仅有NICK_NAME以下的需求
                return await self._get_uinfo_getuserinfo(id_)
            else:
                return await self._get_uinfo_profile(id_)
        elif is_portrait(id_):
            if (require | ReqUInfo.BASIC) == ReqUInfo.BASIC:
                # 仅有BASIC需求
                if not require & ReqUInfo.USER_ID:
                    # 无USER_ID需求
                    return await self._get_uinfo_panel(id_)
            return await self._get_uinfo_profile(id_)
        else:
            if (require | ReqUInfo.BASIC) == ReqUInfo.BASIC:
                return await self._get_uinfo_user_json(id_)
            elif require & ReqUInfo.NICK_NAME and not require & ReqUInfo.USER_ID:
                # 有NICK_NAME需求但无USER_ID需求
                return await self._get_uinfo_panel(id_)
            else:
                user = await self._get_uinfo_user_json(id_)
                return await self._get_uinfo_profile(user.portrait)

    @handle_exception(tieba_uid2user_info.UserInfo_TUid)
    @_try_websocket
    async def tieba_uid2user_info(self, tieba_uid: int) -> tieba_uid2user_info.UserInfo_TUid:
        """
        通过tieba_uid获取用户信息

        Args:
            tieba_uid (int): 用户id tieba_uid

        Returns:
            UserInfo_TUid: 包含较全面的用户信息

        Note:
            请注意tieba_uid与旧版user_id的区别
        """

        if self._ws_core.status == WsStatus.OPEN:
            return await tieba_uid2user_info.request_ws(self._ws_core, tieba_uid)

        return await tieba_uid2user_info.request_http(self._http_core, tieba_uid)

    @handle_exception(profile.Homepage)
    @_try_websocket
    async def get_homepage(self, id_: Union[str, int], /, pn: int = 1) -> profile.Homepage:
        """
        获取用户个人页信息

        Args:
            id_ (str | int): 用户id user_id / user_name / portrait 优先user_id
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            Homepage: 用户个人页信息
        """

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        if self._ws_core.status == WsStatus.OPEN:
            return await profile.get_homepage.request_ws(self._ws_core, user_id, pn)

        return await profile.get_homepage.request_http(self._http_core, user_id, pn)

    @handle_exception(get_follows.Follows)
    async def get_follows(self, id_: Union[str, int, None] = None, /, pn: int = 1) -> get_follows.Follows:
        """
        获取关注列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            id_ (str | int | None): 用户id user_id / user_name / portrait 优先user_id
                默认为None即获取本账号信息. Defaults to None.

        Returns:
            Follows: 关注列表
        """

        if id_ is None:
            user = await self.get_self_info(ReqUInfo.USER_ID)
            user_id = user.user_id
        elif not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        return await get_follows.request(self._http_core, user_id, pn)

    @handle_exception(get_fans.Fans)
    async def get_fans(self, id_: Union[str, int, None] = None, /, pn: int = 1) -> get_fans.Fans:
        """
        获取粉丝列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            id_ (str | int | None): 用户id user_id / user_name / portrait 优先user_id
                默认为None即获取本账号信息. Defaults to None.

        Returns:
            Fans: 粉丝列表
        """

        if id_ is None:
            user = await self.get_self_info(ReqUInfo.USER_ID)
            user_id = user.user_id
        elif not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        return await get_fans.request(self._http_core, user_id, pn)

    @handle_exception(get_blacklist.BlacklistUsers)
    async def get_blacklist(self) -> get_blacklist.BlacklistUsers:
        """
        获取新版用户黑名单列表

        Returns:
            BlacklistUsers: 新版用户黑名单列表
        """

        return await get_blacklist.request(self._http_core)

    @handle_exception(get_blacklist_old.BlacklistOldUsers)
    @_try_websocket
    async def get_blacklist_old(self, pn: int = 1, /, *, rn: int = 10) -> get_blacklist_old.BlacklistOldUsers:
        """
        获取旧版用户黑名单列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 10. Max to Inf.

        Returns:
            BlacklistOldUsers: 旧版用户黑名单列表
        """

        if self._ws_core.status == WsStatus.OPEN:
            return await get_blacklist_old.request_ws(self._ws_core, pn, rn)

        return await get_blacklist_old.request_http(self._http_core, pn, rn)

    @handle_exception(get_follow_forums.FollowForums)
    async def get_follow_forums(
        self, id_: Union[str, int], /, pn: int = 1, *, rn: int = 50
    ) -> get_follow_forums.FollowForums:
        """
        获取用户关注贴吧列表

        Args:
            id_ (str | int): 用户id user_id / user_name / portrait 优先user_id
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 50. Max to Inf.

        Returns:
            FollowForums: 用户关注贴吧列表
        """

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        return await get_follow_forums.request(self._http_core, user_id, pn, rn)

    @handle_exception(get_self_follow_forums.SelfFollowForums)
    async def get_self_follow_forums(self, pn: int = 1) -> get_self_follow_forums.SelfFollowForums:
        """
        获取本账号关注贴吧列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            SelfFollowForums: 本账号关注贴吧列表

        Note:
            本接口需要STOKEN
        """

        return await get_self_follow_forums.request(self._http_core, pn)

    @handle_exception(get_dislike_forums.DislikeForums)
    @_try_websocket
    async def get_dislike_forums(self, pn: int = 1, /, *, rn: int = 20) -> get_dislike_forums.DislikeForums:
        """
        获取首页推荐屏蔽的贴吧列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 20. Max to 20.

        Returns:
            DislikeForums: 首页推荐屏蔽的贴吧列表
        """

        if self._ws_core.status == WsStatus.OPEN:
            return await get_dislike_forums.request_ws(self._ws_core, pn, rn)

        return await get_dislike_forums.request_http(self._http_core, pn, rn)

    @handle_exception(get_user_contents.UserThreads)
    @_try_websocket
    async def get_self_public_threads(self, pn: int = 1) -> get_user_contents.UserThreads:
        """
        获取本人发布的公开状态的主题帖列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            UserThreads: 主题帖列表
        """

        user = await self.get_self_info(ReqUInfo.USER_ID)

        if self._ws_core.status == WsStatus.OPEN:
            return await get_user_contents.get_threads.request_ws(self._ws_core, user.user_id, pn, public_only=True)

        return await get_user_contents.get_threads.request_http(self._http_core, user.user_id, pn, public_only=True)

    @handle_exception(get_user_contents.UserThreads)
    @_try_websocket
    async def get_self_threads(self, pn: int = 1) -> get_user_contents.UserThreads:
        """
        获取本人发布的主题帖列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            UserThreads: 主题帖列表
        """

        user = await self.get_self_info(ReqUInfo.USER_ID)

        if self._ws_core.status == WsStatus.OPEN:
            return await get_user_contents.get_threads.request_ws(self._ws_core, user.user_id, pn, public_only=False)

        return await get_user_contents.get_threads.request_http(self._http_core, user.user_id, pn, public_only=False)

    @handle_exception(get_user_contents.UserPostss)
    @_try_websocket
    async def get_self_posts(self, pn: int = 1) -> get_user_contents.UserPostss:
        """
        获取本人发布的回复列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            UserPostss: 回复列表
        """

        user = await self.get_self_info(ReqUInfo.USER_ID)

        if self._ws_core.status == WsStatus.OPEN:
            return await get_user_contents.get_posts.request_ws(self._ws_core, user.user_id, pn)

        return await get_user_contents.get_posts.request_http(self._http_core, user.user_id, pn)

    @handle_exception(get_user_contents.UserThreads)
    @_try_websocket
    async def get_user_threads(self, id_: Union[str, int], pn: int = 1) -> get_user_contents.UserThreads:
        """
        获取用户发布的主题帖列表

        Args:
            id_ (str | int): 用户id user_id / user_name / portrait 优先user_id
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            UserThreads: 主题帖列表
        """

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        if self._ws_core.status == WsStatus.OPEN:
            return await get_user_contents.get_threads.request_ws(self._ws_core, user_id, pn, public_only=True)

        return await get_user_contents.get_threads.request_http(self._http_core, user_id, pn, public_only=True)

    @handle_exception(get_replys.Replys)
    @_try_websocket
    async def get_replys(self, pn: int = 1) -> get_replys.Replys:
        """
        获取回复信息

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            Replys: 回复列表
        """

        if self._ws_core.status == WsStatus.OPEN:
            return await get_replys.request_ws(self._ws_core, pn)

        return await get_replys.request_http(self._http_core, pn)

    @handle_exception(get_ats.Ats)
    async def get_ats(self, pn: int = 1) -> get_ats.Ats:
        """
        获取@信息

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            Ats: at列表
        """

        return await get_ats.request(self._http_core, pn)

    @handle_exception(get_images.ImageBytes)
    async def get_image_bytes(self, img_url: str) -> get_images.ImageBytes:
        """
        从链接获取静态图像的原始字节流

        Args:
            img_url (str): 图像链接

        Returns:
            ImageBytes: 未解码的原始字节流
        """

        return await get_images.request_bytes(self._http_core, yarl.URL(img_url))

    @handle_exception(get_images.Image)
    async def get_image(self, img_url: str) -> get_images.Image:
        """
        从链接获取静态图像

        Args:
            img_url (str): 图像链接

        Returns:
            Image: 图像
        """

        return await get_images.request(self._http_core, yarl.URL(img_url))

    @handle_exception(get_images.Image)
    async def hash2image(self, raw_hash: str, /, size: Literal['s', 'm', 'l'] = 's') -> get_images.Image:
        """
        通过百度图库hash获取静态图像

        Args:
            raw_hash (str): 百度图库hash
            size (Literal['s', 'm', 'l'], optional): 获取图像的大小 s为宽720 m为宽960 l为原图. Defaults to 's'.

        Returns:
            Image: 图像
        """

        if size == 's':
            img_url = yarl.URL.build(
                scheme="http", host="imgsrc.baidu.com", path=f"/forum/w=720;q=60;g=0/sign=__/{raw_hash}.jpg"
            )
        elif size == 'm':
            img_url = yarl.URL.build(
                scheme="http", host="imgsrc.baidu.com", path=f"/forum/w=960;q=60;g=0/sign=__/{raw_hash}.jpg"
            )
        elif size == 'l':
            img_url = yarl.URL.build(scheme="http", host="imgsrc.baidu.com", path=f"/forum/pic/item/{raw_hash}.jpg")
        else:
            LOG().warning(f"Invalid size={size}")
            return get_images.Image()

        return await get_images.request(self._http_core, img_url)

    @handle_exception(get_images.Image)
    async def get_portrait(self, id_: Union[str, int], /, size: Literal['s', 'm', 'l'] = 's') -> get_images.Image:
        """
        获取用户头像

        Args:
            id_ (str | int): 用户id user_id / user_name / portrait 优先portrait
            size (Literal['s', 'm', 'l'], optional): 获取头像的大小 s为55x55 m为110x110 l为原图. Defaults to 's'.

        Returns:
            Image: 头像
        """

        if not is_portrait(id_):
            user = await self.get_user_info(id_, ReqUInfo.PORTRAIT)
            portrait = user.portrait
        else:
            portrait = id_

        if size == 's':
            path = 'n'
        elif size == 'm':
            path = ''
        elif size == 'l':
            path = 'h'
        else:
            LOG().warning(f"Invalid size={size}")
            return get_images.Image()

        img_url = yarl.URL.build(scheme="http", host="tb.himg.baidu.com", path=f"/sys/portrait{path}/item/{portrait}")

        return await get_images.request(self._http_core, img_url)

    async def __get_selfinfo_initNickname(self) -> None:
        user = await get_selfinfo_initNickname.request(self._http_core)
        self._user.user_name = user.user_name
        self._user.tieba_uid = user.tieba_uid

    @handle_exception(get_square_forums.SquareForums)
    @_try_websocket
    async def get_square_forums(self, cname: str, /, pn: int = 1, *, rn: int = 20) -> get_square_forums.SquareForums:
        """
        获取吧广场列表

        Args:
            cname (str): 类别名
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 20. Max to Inf.

        Returns:
            SquareForums: 吧广场列表
        """

        if self._ws_core.status == WsStatus.OPEN:
            return await get_square_forums.request_ws(self._ws_core, cname, pn, rn)

        return await get_square_forums.request_http(self._http_core, cname, pn, rn)

    @handle_exception(get_bawu_info.BawuInfo)
    @_try_websocket
    async def get_bawu_info(self, fname_or_fid: Union[str, int]) -> get_bawu_info.BawuInfo:
        """
        获取吧务团队信息

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            BawuInfo: 吧务团队信息
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        if self._ws_core.status == WsStatus.OPEN:
            return await get_bawu_info.request_ws(self._ws_core, fid)

        return await get_bawu_info.request_http(self._http_core, fid)

    @handle_exception(get_tab_map.TabMap)
    @_try_websocket
    async def get_tab_map(self, fname_or_fid: Union[str, int]) -> get_tab_map.TabMap:
        """
        获取分区名到分区id的映射

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先贴吧名

        Returns:
            TabMap: 分区名到分区id的映射
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)

        if self._ws_core.status == WsStatus.OPEN:
            return await get_tab_map.request_ws(self._ws_core, fname)

        return await get_tab_map.request_http(self._http_core, fname)

    @handle_exception(get_god_threads.GodThreads)
    async def get_god_threads(self, /, pn: int = 1, rn=10) -> get_god_threads.GodThreads:
        """
        获取pn页的精选神帖列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 10. Max to 100.

        Returns:
            GodThreads: 精选神帖列表
        """

        return await get_god_threads.request(self._http_core, pn, rn)

    @handle_exception(get_rank_users.RankUsers)
    async def get_rank_users(self, fname_or_fid: Union[str, int], /, pn: int = 1) -> get_rank_users.RankUsers:
        """
        获取pn页的等级排行榜用户列表

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            RankUsers: 等级排行榜用户列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)

        return await get_rank_users.request(self._http_core, fname, pn)

    @handle_exception(get_member_users.MemberUsers)
    async def get_member_users(self, fname_or_fid: Union[str, int], /, pn: int = 1) -> get_member_users.MemberUsers:
        """
        获取pn页的最新关注用户列表

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            MemberUsers: 最新关注用户列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)

        return await get_member_users.request(self._http_core, fname, pn)

    @handle_exception(get_blocks.Blocks)
    async def get_blocks(self, fname_or_fid: Union[str, int], /, name: str = '', pn: int = 1) -> get_blocks.Blocks:
        """
        获取pn页的待解封用户列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先fid
            name (str, optional): 通过被封禁用户的用户名/昵称查询 默认为空即查询全部. Defaults to ''.
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            Blocks: 待解封用户列表
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        return await get_blocks.request(self._http_core, fid, name, pn)

    @handle_exception(get_recovers.Recovers)
    async def get_recovers(
        self, fname_or_fid: Union[str, int], /, pn: int = 1, *, rn: int = 10, id_: Union[str, int, None] = None
    ) -> get_recovers.Recovers:
        """
        获取pn页的待恢复帖子列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先fid
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 10. Max to 50.
            id_ (str | int, optional): 用于查询的被删帖用户的id user_id / user_name / portrait 优先user_id. Defaults to None.

        Returns:
            Recovers: 待恢复帖子列表
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        if id_ and not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        return await get_recovers.request(self._http_core, fid, user_id, pn, rn)

    @handle_exception(get_bawu_userlogs.Userlogs)
    async def get_bawu_userlogs(
        self,
        fname_or_fid: Union[str, int],
        /,
        pn: int = 1,
        *,
        search_value: str = '',
        search_type: BawuSearchType = BawuSearchType.USER,
        start_dt: Optional["datetime.datetime"] = None,
        end_dt: Optional["datetime.datetime"] = None,
        op_type: int = 0,
    ) -> get_bawu_userlogs.Userlogs:
        """
        获取吧务用户管理日志表

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.
            search_value (str, optional): 搜索关键字. Defaults to ''.
            search_type (BawuSearchType, optional): 搜索类型. Defaults to BawuSearchType.USER.
            start_dt (datetime.datetime, optional): 搜索的起始时间(含). Defaults to None.
            end_dt (datetime.datetime, optional): 搜索的结束时间(含). Defaults to None.
            op_type (int, optional): 搜索操作类型. Defaults to 0.

        Returns:
            Userlogs: 吧务用户管理日志表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)

        return await get_bawu_userlogs.request(
            self._http_core, fname, pn, search_value, search_type, start_dt, end_dt, op_type
        )

    @handle_exception(get_bawu_postlogs.Postlogs)
    async def get_bawu_postlogs(
        self,
        fname_or_fid: Union[str, int],
        /,
        pn: int = 1,
        *,
        search_value: str = '',
        search_type: BawuSearchType = BawuSearchType.USER,
        start_dt: Optional["datetime.datetime"] = None,
        end_dt: Optional["datetime.datetime"] = None,
        op_type: int = 0,
    ) -> get_bawu_postlogs.Postlogs:
        """
        获取吧务帖子管理日志表

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.
            search_value (str, optional): 搜索关键字. Defaults to ''.
            search_type (BawuSearchType, optional): 搜索类型. Defaults to BawuSearchType.USER.
            start_dt (datetime.datetime, optional): 搜索的起始时间(含). Defaults to None.
            end_dt (datetime.datetime, optional): 搜索的结束时间(含). Defaults to None.
            op_type (int, optional): 搜索操作类型. Defaults to 0.

        Returns:
            Postlogs: 吧务帖子管理日志表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)

        return await get_bawu_postlogs.request(
            self._http_core, fname, pn, search_value, search_type, start_dt, end_dt, op_type
        )

    @handle_exception(get_unblock_appeals.Appeals)
    async def get_unblock_appeals(
        self, fname_or_fid: Union[str, int], /, pn: int = 1, *, rn: int = 5
    ) -> get_unblock_appeals.Appeals:
        """
        获取申诉请求列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先fid
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 5. Max to 50.

        Returns:
            Appeals: 申诉请求列表
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await get_unblock_appeals.request(self._http_core, fid, pn, rn)

    @handle_exception(get_bawu_blacklist.BawuBlacklistUsers)
    async def get_bawu_blacklist(
        self, fname_or_fid: Union[str, int], /, pn: int = 1
    ) -> get_bawu_blacklist.BawuBlacklistUsers:
        """
        获取pn页的吧务黑名单列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            BlacklistUsers: 吧务黑名单列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)

        return await get_bawu_blacklist.request(self._http_core, fname, pn)

    @handle_exception(get_statistics.Statistics)
    async def get_statistics(self, fname_or_fid: Union[str, int]) -> get_statistics.Statistics:
        """
        获取吧务后台中最近24天的统计数据

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            Statistics: 吧务后台统计信息
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        return await get_statistics.request(self._http_core, fid)

    @handle_exception(get_recom_status.RecomStatus)
    async def get_recom_status(self, fname_or_fid: Union[str, int]) -> get_recom_status.RecomStatus:
        """
        获取大吧主推荐功能的月度配额状态

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            RecomStatus: 大吧主推荐功能的月度配额状态
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        return await get_recom_status.request(self._http_core, fid)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def block(
        self, fname_or_fid: Union[str, int], /, id_: Union[str, int], *, day: int = 1, reason: str = ''
    ) -> BoolResponse:
        """
        封禁用户

        Args:
            fname_or_fid (str | int): 所在贴吧的贴吧名或fid 优先fid
            id_ (str | int): 用户id user_id / user_name / portrait 优先portrait
            day (int, optional): 封禁天数. Defaults to 1.
            reason (str, optional): 封禁理由. Defaults to ''.

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        if not is_portrait(id_):
            user = await self.get_user_info(id_, ReqUInfo.PORTRAIT)
            portrait = user.portrait
        else:
            portrait = id_

        await self.__init_tbs()

        return await block.request(self._http_core, fid, portrait, day, reason)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def unblock(self, fname_or_fid: Union[str, int], /, id_: Union[str, int]) -> BoolResponse:
        """
        解封用户

        Args:
            fname_or_fid (str | int): 所在贴吧的贴吧名或fid 优先fid
            id_ (str | int): 用户id user_id / user_name / portrait 优先user_id

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        await self.__init_tbs()

        return await unblock.request(self._http_core, fid, user_id)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def add_bawu_blacklist(self, fname_or_fid: Union[str, int], /, id_: Union[str, int]) -> BoolResponse:
        """
        添加贴吧黑名单

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先贴吧名
            id_ (str | int): 用户id user_id / user_name / portrait 优先user_id

        Returns:
            BoolResponse: True成功 False失败
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        await self.__init_tbs()

        return await add_bawu_blacklist.request(self._http_core, fname, user_id)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def del_bawu_blacklist(self, fname_or_fid: Union[str, int], /, id_: Union[str, int]) -> BoolResponse:
        """
        移出贴吧黑名单

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先贴吧名
            id_ (str | int): 用户id user_id / user_name / portrait 优先user_id

        Returns:
            BoolResponse: True成功 False失败
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        await self.__init_tbs()

        return await del_bawu_blacklist.request(self._http_core, fname, user_id)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def hide_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> BoolResponse:
        """
        屏蔽主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待屏蔽的主题帖tid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await del_thread.request(self._http_core, fid, tid, is_hide=True)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def del_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> BoolResponse:
        """
        删除主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待删除的主题帖tid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await del_thread.request(self._http_core, fid, tid, is_hide=False)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def del_threads(
        self, fname_or_fid: Union[str, int], /, tids: List[int], *, block: bool = False
    ) -> BoolResponse:
        """
        批量删除主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tids (list[int]): 待删除的主题帖tid列表. Length Max to 30.
            block (bool, optional): 是否同时封一天. Defaults to False.

        Returns:
            BoolResponse: True成功 False失败 部分成功返回True
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await del_threads.request(self._http_core, fid, tids, block)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def del_post(self, fname_or_fid: Union[str, int], /, tid: int, pid: int) -> BoolResponse:
        """
        删除回复

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 所在主题帖tid
            pid (int): 待删除的回复pid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await del_post.request(self._http_core, fid, tid, pid)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def del_posts(
        self, fname_or_fid: Union[str, int], /, tid: int, pids: List[int], *, block: bool = False
    ) -> BoolResponse:
        """
        批量删除回复

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 所在主题帖tid
            pids (list[int]): 待删除的回复pid列表. Length Max to 30.
            block (bool, optional): 是否同时封一天. Defaults to False.

        Returns:
            BoolResponse: True成功 False失败 部分成功返回True
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await del_posts.request(self._http_core, fid, tid, pids, block)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def unhide_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> BoolResponse:
        """
        解除主题帖屏蔽

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int, optional): 待解除屏蔽的主题帖tid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await recover.request(self._http_core, fid, tid, 0, is_hide=True)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def recover_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> BoolResponse:
        """
        恢复主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int, optional): 待恢复的主题帖tid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await recover.request(self._http_core, fid, tid, 0, is_hide=False)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def recover_post(self, fname_or_fid: Union[str, int], /, pid: int) -> BoolResponse:
        """
        恢复主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            pid (int, optional): 待恢复的回复pid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await recover.request(self._http_core, fid, 0, pid, is_hide=False)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def recover(
        self, fname_or_fid: Union[str, int], /, tid: int = 0, pid: int = 0, *, is_hide: bool = False
    ) -> BoolResponse:
        """
        帖子恢复相关操作

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int, optional): 待恢复的主题帖tid. Defaults to 0.
            pid (int, optional): 待恢复的回复pid. Defaults to 0.
            is_hide (bool, optional): True则取消屏蔽主题帖 False则恢复删帖. Defaults to False.

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await recover.request(self._http_core, fid, tid, pid, is_hide)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def good(self, fname_or_fid: Union[str, int], /, tid: int, *, cname: str = '') -> BoolResponse:
        """
        加精主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待加精的主题帖tid
            cname (str, optional): 待添加的精华分区名称 默认为''即不分区. Defaults to ''.

        Returns:
            BoolResponse: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.__get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.__get_fname(fid)

        await self.__init_tbs()

        cid = await self.__get_cid(fname_or_fid, cname)

        return await good.request(self._http_core, fname, fid, tid, cid)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def ungood(self, fname_or_fid: Union[str, int], /, tid: int) -> BoolResponse:
        """
        撤精主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待撤精的主题帖tid

        Returns:
            BoolResponse: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.__get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.__get_fname(fid)

        await self.__init_tbs()

        return await ungood.request(self._http_core, fname, fid, tid)

    async def __get_cid(self, fname_or_fid: Union[str, int], /, cname: str = '') -> int:
        if cname == '':
            return 0

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)

        cates = await get_cid.request(self._http_core, fname)

        cid = 0
        for item in cates:
            if cname == item['class_name']:
                cid = int(item['class_id'])
                break

        return cid

    @handle_exception(IntResponse)
    async def get_cid(self, fname_or_fid: Union[str, int], /, cname: str = '') -> IntResponse:
        """
        通过精华分区名获取精华分区id

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            cname (str, optional): 精华分区名. Defaults to ''.

        Returns:
            IntResponse: 精华分区id
        """

        cid = await self.__get_cid(fname_or_fid, cname)
        return IntResponse(cid)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def top(self, fname_or_fid: Union[str, int], /, tid: int) -> BoolResponse:
        """
        置顶主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待置顶的主题帖tid

        Returns:
            BoolResponse: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.__get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.__get_fname(fid)

        await self.__init_tbs()

        return await top.request(self._http_core, fname, fid, tid, is_set=True)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def untop(self, fname_or_fid: Union[str, int], /, tid: int) -> BoolResponse:
        """
        撤销置顶主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待撤销置顶的主题帖tid

        Returns:
            BoolResponse: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.__get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.__get_fname(fid)

        await self.__init_tbs()

        return await top.request(self._http_core, fname, fid, tid, is_set=False)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def move(
        self, fname_or_fid: Union[str, int], /, tid: int, *, to_tab_id: int, from_tab_id: int = 0
    ) -> BoolResponse:
        """
        将主题帖移动至另一分区

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待移动的主题帖tid
            to_tab_id (int): 目标分区id
            from_tab_id (int, optional): 来源分区id 默认为0即无分区. Defaults to 0.

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await move.request(self._http_core, fid, tid, to_tab_id, from_tab_id)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def recommend(self, fname_or_fid: Union[str, int], /, tid: int) -> BoolResponse:
        """
        大吧主首页推荐

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待推荐的主题帖tid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        return await recommend.request(self._http_core, fid, tid)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def handle_unblock_appeals(
        self, fname_or_fid: Union[str, int], /, appeal_ids: List[int], *, refuse: bool = True
    ) -> BoolResponse:
        """
        拒绝或通过解封申诉

        Args:
            fname_or_fid (str | int): 申诉所在贴吧的贴吧名或fid 优先fid
            appeal_ids (list[int]): 申诉请求的appeal_id列表. Length Max to 30.
            refuse (bool, optional): True则拒绝申诉 False则接受申诉. Defaults to True.

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await handle_unblock_appeals.request(self._http_core, fid, appeal_ids, refuse)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def agree(self, tid: int, pid: int = 0, is_comment: bool = False) -> BoolResponse:
        """
        点赞主题帖或回复

        Args:
            tid (int): 待点赞的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待点赞的回复pid. Defaults to 0.
            is_comment (bool, optional): pid是否指向楼中楼. Defaults to False.

        Returns:
            BoolResponse: True成功 False失败

        Note:
            本接口仍处于测试阶段\n
            高频率调用会导致<发帖秒删>！请谨慎使用！
        """

        await self.__init_tbs()

        return await agree.request(self._http_core, tid, pid, is_comment, is_disagree=False, is_undo=False)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def unagree(self, tid: int, pid: int = 0, is_comment: bool = False) -> BoolResponse:
        """
        取消点赞主题帖或回复

        Args:
            tid (int): 待取消点赞的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待取消点赞的回复pid. Defaults to 0.
            is_comment (bool, optional): pid是否指向楼中楼. Defaults to False.

        Returns:
            BoolResponse: True成功 False失败
        """

        await self.__init_tbs()

        return await agree.request(self._http_core, tid, pid, is_comment, is_disagree=False, is_undo=True)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def disagree(self, tid: int, pid: int = 0, is_comment: bool = False) -> BoolResponse:
        """
        点踩主题帖或回复

        Args:
            tid (int): 待点踩的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待点踩的回复pid. Defaults to 0.
            is_comment (bool, optional): pid是否指向楼中楼. Defaults to False.

        Returns:
            BoolResponse: True成功 False失败
        """

        await self.__init_tbs()

        return await agree.request(self._http_core, tid, pid, is_comment, is_disagree=True, is_undo=False)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def undisagree(self, tid: int, pid: int = 0, is_comment: bool = False) -> BoolResponse:
        """
        取消点踩主题帖或回复

        Args:
            tid (int): 待取消点踩的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待取消点踩的回复pid. Defaults to 0.
            is_comment (bool, optional): pid是否指向楼中楼. Defaults to False.

        Returns:
            BoolResponse: True成功 False失败
        """

        await self.__init_tbs()

        return await agree.request(self._http_core, tid, pid, is_comment, is_disagree=True, is_undo=True)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def agree_vimage(self, id_: Union[str, int]) -> BoolResponse:
        """
        虚拟形象点赞

        Args:
            id_ (str | int): 点赞对象的用户id user_id / user_name / portrait 优先user_id

        Returns:
            BoolResponse: True成功 False失败
        """

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        return await agree_vimage.request(self._http_core, user_id)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def follow_user(self, id_: Union[str, int]) -> BoolResponse:
        """
        关注用户

        Args:
            id_ (str | int): 用户id user_id / user_name / portrait 优先portrait

        Returns:
            BoolResponse: True成功 False失败
        """

        if not is_portrait(id_):
            user = await self.get_user_info(id_, ReqUInfo.PORTRAIT)
            portrait = user.portrait
        else:
            portrait = id_

        await self.__init_tbs()

        return await follow_user.request(self._http_core, portrait)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def unfollow_user(self, id_: Union[str, int]) -> BoolResponse:
        """
        取关用户

        Args:
            id_ (str | int): 用户id user_id / user_name / portrait 优先portrait

        Returns:
            BoolResponse: True成功 False失败
        """

        if not is_portrait(id_):
            user = await self.get_user_info(id_, ReqUInfo.PORTRAIT)
            portrait = user.portrait
        else:
            portrait = id_

        await self.__init_tbs()

        return await unfollow_user.request(self._http_core, portrait)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def remove_fan(self, id_: Union[str, int]) -> BoolResponse:
        """
        移除粉丝

        Args:
            id_ (str | int): 待移除粉丝的id user_id / user_name / portrait 优先user_id

        Returns:
            BoolResponse: True成功 False失败
        """

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        await self.__init_tbs()

        return await remove_fan.request(self._http_core, user_id)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    @_try_websocket
    async def set_blacklist(self, id_: Union[str, int], *, btype: BlacklistType = BlacklistType.ALL) -> BoolResponse:
        """
        设置新版用户黑名单

        Args:
            id_ (str | int): 待设置黑名单的用户id user_id / user_name / portrait 优先user_id
            btype (BlacklistType): 黑名单类型. 默认全屏蔽. Defaults to BlacklistType.ALL.

        Returns:
            BoolResponse: True成功 False失败
        """

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        if self._ws_core.status == WsStatus.OPEN:
            return await set_blacklist.request_ws(self._ws_core, user_id, btype)

        return await set_blacklist.request_http(self._http_core, user_id, btype)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def add_blacklist_old(self, id_: Union[str, int]) -> BoolResponse:
        """
        添加旧版用户黑名单

        Args:
            id_ (str | int): 待添加黑名单的用户id user_id / user_name / portrait 优先user_id

        Returns:
            BoolResponse: True成功 False失败
        """

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        return await add_blacklist_old.request(self._http_core, user_id)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def del_blacklist_old(self, id_: Union[str, int]) -> BoolResponse:
        """
        移除旧版用户黑名单

        Args:
            id_ (str | int): 待移除黑名单的用户id user_id / user_name / portrait 优先user_id

        Returns:
            BoolResponse: True成功 False失败
        """

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        return await del_blacklist_old.request(self._http_core, user_id)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def follow_forum(self, fname_or_fid: Union[str, int]) -> BoolResponse:
        """
        关注贴吧

        Args:
            fname_or_fid (str | int): 要关注贴吧的贴吧名或fid 优先fid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await follow_forum.request(self._http_core, fid)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def unfollow_forum(self, fname_or_fid: Union[str, int]) -> BoolResponse:
        """
        取关贴吧

        Args:
            fname_or_fid (str | int): 要取关贴吧的贴吧名或fid 优先fid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)
        await self.__init_tbs()

        return await unfollow_forum.request(self._http_core, fid)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def dislike_forum(self, fname_or_fid: Union[str, int]) -> BoolResponse:
        """
        屏蔽贴吧 使其不再出现在首页推荐列表中

        Args:
            fname_or_fid (str | int): 待屏蔽贴吧的贴吧名或fid 优先fid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        return await dislike_forum.request(self._http_core, fid)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def undislike_forum(self, fname_or_fid: Union[str, int]) -> BoolResponse:
        """
        解除贴吧的首页推荐屏蔽

        Args:
            fname_or_fid (str | int): 待屏蔽贴吧的贴吧名或fid 优先fid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        return await undislike_forum.request(self._http_core, fid)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def set_thread_private(self, fname_or_fid: Union[str, int], /, tid: int, pid: int) -> BoolResponse:
        """
        隐藏主题帖

        Args:
            fname_or_fid (str | int): 主题帖所在贴吧的贴吧名或fid 优先fid
            tid (int): 主题帖tid
            tid (int): 主题帖pid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        return await set_thread_privacy.request(self._http_core, fid, tid, pid, is_hide=True)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def set_thread_public(self, fname_or_fid: Union[str, int], /, tid: int, pid: int) -> BoolResponse:
        """
        公开主题帖

        Args:
            fname_or_fid (str | int): 主题帖所在贴吧的贴吧名或fid 优先fid
            tid (int): 主题帖tid
            tid (int): 主题帖pid

        Returns:
            BoolResponse: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.__get_fid(fname_or_fid)

        return await set_thread_privacy.request(self._http_core, fid, tid, pid, is_hide=False)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def set_profile(self, nick_name: str, sign: str = '', gender: Gender = Gender.UNKNOWN) -> BoolResponse:
        """
        设置主页信息

        Args:
            nick_name (str): 昵称
            sign (str): 个性签名. Defaults to ''.
            gender (Gender): 性别. Defaults to Gender.UNKNOWN.

        Returns:
            BoolResponse: True成功 False失败
        """

        return await set_profile.request(self._http_core, nick_name, sign, gender)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def set_nickname_old(self, nick_name: str) -> BoolResponse:
        """
        设置旧版昵称

        Args:
            nick_name (str): 昵称

        Returns:
            BoolResponse: True成功 False失败
        """

        return await set_nickname_old.request(self._http_core, nick_name)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def sign_forum(self, fname_or_fid: Union[str, int]) -> BoolResponse:
        """
        单个贴吧签到

        Args:
            fname_or_fid (str | int): 要签到贴吧的贴吧名或fid 优先贴吧名

        Returns:
            BoolResponse: True成功 False失败
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.__get_fname(fname_or_fid)
        await self.__init_tbs()

        return await sign_forum.request(self._http_core, fname)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def sign_growth(self) -> BoolResponse:
        """
        用户成长等级任务: 签到

        Returns:
            BoolResponse: True成功 False失败
        """

        await self.__init_tbs()

        return await sign_growth.request_web(self._http_core, act_type='page_sign')

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    async def sign_growth_share(self) -> BoolResponse:
        """
        用户成长等级任务: 分享主题帖

        Returns:
            bool: True成功 False失败
        """

        await self.__init_tbs()

        return await sign_growth.request_app(self._http_core, act_type='share_thread')

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    @_try_websocket
    async def add_post(self, fname_or_fid: Union[str, int], /, tid: int, content: str) -> BoolResponse:
        """
        回复主题帖

        Args:
            fname_or_fid (str | int): 要回复的主题帖所在贴吧的贴吧名或fid
            tid (int): 要回复的主题帖的tid
            content (str): 回复内容

        Returns:
            BoolResponse: 回帖是否成功

        Note:
            本接口仍处于测试阶段\n
            高频率调用会导致<永久封禁屏蔽>！请谨慎使用！
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.__get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.__get_fname(fid)

        await self.__init_z_id()
        await self.__init_tbs()
        await self.__init_client_id()
        await self.__init_sample_id()
        await self.__get_selfinfo_initNickname()

        show_name = self._user.show_name

        if self._ws_core.status == WsStatus.OPEN:
            return await add_post.request_ws(self._ws_core, fname, fid, tid, show_name, content)

        return await add_post.request_http(self._http_core, fname, fid, tid, show_name, content)

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    @_force_websocket
    async def send_msg(self, id_: Union[str, int], content: str) -> BoolResponse:
        """
        发送私信

        Args:
            id_ (str | int): 用户id user_id / user_name / portrait 优先user_id
            content (str): 发送内容

        Returns:
            BoolResponse: True成功 False失败
        """

        if not isinstance(id_, int):
            user = await self.get_user_info(id_, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = id_

        msg_id = await send_msg.request(self._ws_core, user_id, content)

        mid_manager = self._ws_core.mid_manager
        mid_manager.update_msg_id(mid_manager.priv_gid, msg_id)

        return BoolResponse()

    @handle_exception(BoolResponse, ok_log_level=logging.INFO)
    @_force_websocket
    async def set_msg_readed(self, message: get_group_msg.WsMessage) -> BoolResponse:
        """
        将一条私信设为已读

        Args:
            message (WsMessage): websocket私信消息

        Returns:
            BoolResponse: True成功 False失败
        """

        return await set_msg_readed.request(self._ws_core, message)

    @handle_exception(get_group_msg.WsMsgGroups)
    @_force_websocket
    async def get_group_msg(self, group_ids: List[int], *, get_type: int = 1) -> get_group_msg.WsMsgGroups:
        """
        获取分组信息

        Args:
            group_ids (List[int]): 待获取分组的group_id
            get_type (int, optional): 获取类型. Defaults to 1.

        Returns:
            WsMsgGroups: websocket消息组列表
        """

        return await get_group_msg.request(self._ws_core, group_ids, get_type)
