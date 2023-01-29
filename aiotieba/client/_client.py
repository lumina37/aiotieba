import asyncio
import binascii
import socket
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Tuple, Union

import aiohttp
import yarl
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from .._logging import get_logger as LOG
from ._classdef.enums import ReqUInfo
from ._classdef.user import UserInfo
from ._core import TbCore
from ._helper import ForumInfoCache, WebsocketResponse, is_portrait, pack_ws_bytes, parse_ws_bytes
from ._typing import TypeUserInfo
from .get_homepage._classdef import UserInfo_home

if TYPE_CHECKING:
    import numpy as np

    from . import (
        get_ats,
        get_bawu_info,
        get_blacklist_users,
        get_blocks,
        get_comments,
        get_dislike_forums,
        get_fans,
        get_follow_forums,
        get_follows,
        get_forum_detail,
        get_homepage,
        get_member_users,
        get_posts,
        get_rank_users,
        get_recom_status,
        get_recovers,
        get_replys,
        get_self_follow_forums,
        get_square_forums,
        get_threads,
        get_uinfo_getuserinfo_app,
        get_uinfo_getUserInfo_web,
        get_uinfo_panel,
        get_uinfo_user_json,
        get_unblock_appeals,
        get_user_contents,
        search_post,
        tieba_uid2user_info,
    )


class Client(object):
    """
    贴吧客户端

    Args:
        BDUSS_key (str, optional): 用于快捷调用BDUSS. Defaults to None.
        proxy (tuple[yarl.URL, aiohttp.BasicAuth] | bool, optional): True则使用环境变量代理 False则禁用代理
            输入一个 (http代理地址, 代理验证) 的元组以手动设置代理. Defaults to False.
        loop (asyncio.AbstractEventLoop, optional): 事件循环. Defaults to None.
    """

    __slots__ = [
        '_core',
        '_user',
        '_connector',
        '_client_ws',
        'websocket',
        '_ws_dispatcher',
    ]

    def __init__(
        self,
        BDUSS_key: Optional[str] = None,
        *,
        proxy: Union[Tuple[yarl.URL, aiohttp.BasicAuth], bool] = False,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:

        self._core = TbCore(BDUSS_key, proxy, loop)
        self._user = UserInfo_home()._init_null()

        timeout = aiohttp.ClientTimeout(connect=3.0, sock_read=12.0, sock_connect=3.2)

        connector = aiohttp.TCPConnector(
            ttl_dns_cache=600,
            family=socket.AF_INET,
            keepalive_timeout=15.0,
            limit=0,
            ssl=False,
            loop=loop,
        )
        self._connector = connector

        ws_headers = {
            aiohttp.hdrs.HOST: "im.tieba.baidu.com:8000",
            aiohttp.hdrs.SEC_WEBSOCKET_EXTENSIONS: "im_version=2.3",
        }
        self._client_ws = aiohttp.ClientSession(
            connector=connector,
            loop=loop,
            headers=ws_headers,
            connector_owner=False,
            raise_for_status=True,
            timeout=timeout,
            read_bufsize=1 << 18,  # 256KiB
        )

        self.websocket: aiohttp.ClientWebSocketResponse = None
        self._ws_dispatcher: asyncio.Task = None

    async def __aenter__(self) -> "Client":
        return self

    async def close(self) -> None:
        if self.is_ws_aviliable:
            await self.websocket.close()

        if self._ws_dispatcher is not None:
            self._ws_dispatcher.cancel()

        if self._connector is not None:
            await self._connector.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    def __hash__(self) -> int:
        return hash(self._core._BDUSS_key)

    def __eq__(self, obj: "Client") -> bool:
        return self._core._BDUSS_key == obj._core._BDUSS_key

    @property
    def core(self) -> TbCore:
        """
        贴吧核心参数容器

        Returns:
            TiebaCore
        """

        return self._core

    @property
    def client_ws(self) -> aiohttp.ClientSession:
        """
        用于websocket请求

        Returns:
            aiohttp.ClientSession
        """

        return self._client_ws

    async def __create_websocket(self, heartbeat: Optional[float] = None) -> None:
        """
        建立weboscket连接

        Args:
            heartbeat (float, optional): 是否定时ping. Defaults to None.

        Raises:
            aiohttp.WSServerHandshakeError: websocket握手失败
        """

        if self._ws_dispatcher is not None and not self._ws_dispatcher.done():
            self._ws_dispatcher.cancel()

        self.websocket = await self._client_ws._ws_connect(
            yarl.URL.build(scheme="ws", host="im.tieba.baidu.com", port=8000),
            heartbeat=heartbeat,
            proxy=self._core._proxy,
            proxy_auth=self._core._proxy_auth,
            ssl=False,
        )

        self._ws_dispatcher = asyncio.create_task(self.__ws_dispatch(), name="ws_dispatcher")

    @property
    def is_ws_aviliable(self) -> bool:
        """
        self.websocket是否可用

        Returns:
            bool: True则self.websocket可用 反之不可用
        """

        return not (self.websocket is None or self.websocket.closed or self.websocket._writer.transport.is_closing())

    async def send_ws_bytes(
        self, ws_bytes: bytes, /, cmd: int, *, timeout: float, need_gzip: bool = True, need_encrypt: bool = True
    ) -> bytes:
        """
        将ws_bytes通过贴吧websocket发送

        Args:
            ws_bytes (bytes): 待发送的websocket数据
            cmd (int): 请求的cmd类型
            timeout (float): 设置超时秒数
            need_gzip (bool, optional): 是否需要gzip压缩. Defaults to False.
            need_encrypt (bool, optional): 是否需要aes加密. Defaults to False.

        Returns:
            bytes: 从websocket接收到的数据
        """

        ws_res = WebsocketResponse()
        ws_bytes = pack_ws_bytes(
            self.core, ws_bytes, cmd, ws_res.req_id, need_gzip=need_gzip, need_encrypt=need_encrypt
        )

        WebsocketResponse.ws_res_wait_dict[ws_res.req_id] = ws_res
        await self.websocket.send_bytes(ws_bytes)

        try:
            data = await asyncio.wait_for(ws_res._data_future, timeout)
        except asyncio.TimeoutError:
            del WebsocketResponse.ws_res_wait_dict[ws_res.req_id]
            raise asyncio.TimeoutError("Timeout to read")

        del WebsocketResponse.ws_res_wait_dict[ws_res.req_id]
        return data

    async def __ws_dispatch(self) -> None:
        """
        分发从贴吧websocket接收到的数据
        """

        try:
            async for msg in self.websocket:
                res_bytes, _, req_id = parse_ws_bytes(msg.data)

                ws_res = WebsocketResponse.ws_res_wait_dict.get(req_id, None)
                if ws_res:
                    ws_res._data_future.set_result(res_bytes)

        except asyncio.CancelledError:
            return

    async def __init_websocket(self) -> None:
        """
        初始化weboscket连接对象并发送初始化信息

        Raises:
            TiebaServerError: 服务端返回错误
        """

        if not self.is_ws_aviliable:
            await self.__create_websocket()

            from . import init_websocket

            pub_key_bytes = binascii.a2b_base64(
                b"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwQpwBZxXJV/JVRF/uNfyMSdu7YWwRNLM8+2xbniGp2iIQHOikPpTYQjlQgMi1uvq1kZpJ32rHo3hkwjy2l0lFwr3u4Hk2Wk7vnsqYQjAlYlK0TCzjpmiI+OiPOUNVtbWHQiLiVqFtzvpvi4AU7C1iKGvc/4IS45WjHxeScHhnZZ7njS4S1UgNP/GflRIbzgbBhyZ9kEW5/OO5YfG1fy6r4KSlDJw4o/mw5XhftyIpL+5ZBVBC6E1EIiP/dd9AbK62VV1PByfPMHMixpxI3GM2qwcmFsXcCcgvUXJBa9k6zP8dDQ3csCM2QNT+CQAOxthjtp/TFWaD7MzOdsIYb3THwIDAQAB"
            )
            pub_key = RSA.import_key(pub_key_bytes)
            rsa_chiper = PKCS1_v1_5.new(pub_key)
            secret_key = rsa_chiper.encrypt(self.core.ws_password)

            proto = init_websocket.pack_proto(self.core, secret_key)

            body = await self.send_ws_bytes(proto, cmd=1001, timeout=5.0, need_gzip=False, need_encrypt=False)
            init_websocket.parse_body(body)

    async def __init_tbs(self) -> bool:
        """
        初始化反csrf校验码tbs
        """

        if self._core._tbs:
            return True

        return await self.__login()

    async def get_self_info(self, require: ReqUInfo = ReqUInfo.ALL) -> TypeUserInfo:
        """
        获取本账号信息

        Args:
            require (ReqUInfo): 指示需要获取的字段

        Returns:
            TypeUserInfo: 用户信息
        """

        if not self._user._user_id:
            if require & ReqUInfo.BASIC:
                await self.__login()
        if not self._user._tieba_uid:
            if require & (ReqUInfo.TIEBA_UID | ReqUInfo.NICK_NAME):
                await self.__get_selfinfo_initNickname()

        return self._user

    async def __login(self) -> bool:

        from . import login

        user, tbs = await login.request(self._connector, self._core)

        if tbs:
            self._user._user_id = user._user_id
            self._user._portrait = user._portrait
            self._user._user_name = user._user_name
            self._core._tbs = tbs
            return True
        else:
            return False

    async def __init_client_id(self) -> str:
        """
        初始化client_id

        Returns:
            str: client_id 例如 wappc_1653660000000_123
        """

        if self._core._client_id:
            return True

        return await self.__sync()

    async def __sync(self) -> bool:

        from . import sync

        client_id = await sync.request(self._connector, self._core)

        if client_id:
            self._core._client_id = client_id
            return True
        else:
            return False

    async def get_fid(self, fname: str) -> int:
        """
        通过贴吧名获取forum_id

        Args:
            fname (str): 贴吧名

        Returns:
            int: forum_id
        """

        if fid := ForumInfoCache.get_fid(fname):
            return fid

        from . import get_fid

        fid = await get_fid.request(self._connector, self._core, fname)

        if fid:
            ForumInfoCache.add_forum(fname, fid)

        return fid

    async def get_fname(self, fid: int) -> str:
        """
        通过forum_id获取贴吧名

        Args:
            fid (int): forum_id

        Returns:
            str: 贴吧名
        """

        if fname := ForumInfoCache.get_fname(fid):
            return fname

        fdetail = await self.get_forum_detail(fid)
        fname = fdetail._fname

        if fname:
            ForumInfoCache.add_forum(fname, fid)

        return fname

    async def get_user_info(self, _id: Union[str, int], /, require: ReqUInfo = ReqUInfo.ALL) -> TypeUserInfo:
        """
        获取用户信息

        Args:
            _id (str | int): 用户id user_id / portrait / user_name
            require (ReqUInfo): 指示需要获取的字段

        Returns:
            TypeUserInfo: 用户信息
        """

        if not _id:
            LOG().warning("Null input")
            return UserInfo(_id)

        if isinstance(_id, int):
            if (require | ReqUInfo.BASIC) == ReqUInfo.BASIC:
                # 仅有BASIC需求
                return await self._get_uinfo_getUserInfo(_id)
            elif require & ReqUInfo.TIEBA_UID:
                # 有TIEBA_UID需求
                user = await self._get_uinfo_getUserInfo(_id)
                user, _ = await self.get_homepage(user.portrait, with_threads=False)
                return user
            else:
                # 有除TIEBA_UID外的其他非BASIC需求
                return await self._get_uinfo_getuserinfo(_id)
        elif is_portrait(_id):
            if (require | ReqUInfo.BASIC) == ReqUInfo.BASIC:
                if not require & ReqUInfo.USER_ID:
                    # 无USER_ID需求
                    return await self._get_uinfo_panel(_id)
                else:
                    user, _ = await self.get_homepage(_id, with_threads=False)
                    return user
            else:
                user, _ = await self.get_homepage(_id, with_threads=False)
                return user
        else:
            if (require | ReqUInfo.BASIC) == ReqUInfo.BASIC:
                return await self._get_uinfo_user_json(_id)
            elif require & ReqUInfo.NICK_NAME and not require & ReqUInfo.USER_ID:
                # 有NICK_NAME需求但无USER_ID需求
                return await self._get_uinfo_panel(_id)
            else:
                user = await self._get_uinfo_user_json(_id)
                user, _ = await self.get_homepage(user.portrait, with_threads=False)
                return user

    async def _get_uinfo_panel(self, name_or_portrait: str) -> "get_uinfo_panel.UserInfo_panel":
        """
        接口 https://tieba.baidu.com/home/get/panel

        Args:
            name_or_portrait (str): 用户id user_name / portrait

        Returns:
            UserInfo_panel: 包含较全面的用户信息

        Note:
            从2022.08.30开始服务端不再返回user_id字段 请谨慎使用
            该接口可判断用户是否被屏蔽
            该接口rps阈值较低
        """

        from . import get_uinfo_panel

        return await get_uinfo_panel.request(self._connector, self._core, name_or_portrait)

    async def _get_uinfo_user_json(self, user_name: str) -> "get_uinfo_user_json.UserInfo_json":
        """
        接口 http://tieba.baidu.com/i/sys/user_json

        Args:
            user_name (str): 用户id user_name

        Returns:
            UserInfo_json: 包含 user_id / portrait / user_name
        """

        from . import get_uinfo_user_json

        user = await get_uinfo_user_json.request(self._connector, self._core, user_name)
        user._user_name = user_name

        return user

    async def _get_uinfo_getuserinfo(self, user_id: int) -> "get_uinfo_getuserinfo_app.UserInfo_guinfo_app":
        """
        接口 http://tiebac.baidu.com/c/u/user/getuserinfo

        Args:
            user_id (int): 用户id user_id

        Returns:
            UserInfo_guinfo_app: 包含 user_id / portrait / user_name / nick_name_old / 性别 /
                是否大神 / 是否超级会员
        """

        from . import get_uinfo_getuserinfo_app

        return await get_uinfo_getuserinfo_app.request_http(self._connector, self._core, user_id)

    async def _get_uinfo_getUserInfo(self, user_id: int) -> "get_uinfo_getUserInfo_web.UserInfo_guinfo_web":
        """
        接口 http://tieba.baidu.com/im/pcmsg/query/getUserInfo

        Args:
            user_id (int): 用户id user_id

        Returns:
            UserInfo_guinfo_web: 包含 user_id / portrait / user_name / nick_name_new

        Note:
            该接口需要BDUSS
        """

        from . import get_uinfo_getUserInfo_web

        try:
            user = await get_uinfo_getUserInfo_web.request(self._connector, self._core, user_id)
            user._user_id = user_id

        except Exception as err:
            LOG().warning(f"{err}. user={user_id}")
            user = get_uinfo_getUserInfo_web.UserInfo_guinfo_web()._init_null()

        return user

    async def tieba_uid2user_info(self, tieba_uid: int) -> "tieba_uid2user_info.UserInfo_TUid":
        """
        通过tieba_uid获取用户信息

        Args:
            tieba_uid (int): 用户id tieba_uid

        Returns:
            UserInfo_TUid: 包含较全面的用户信息

        Note:
            请注意tieba_uid与旧版user_id的区别
        """

        from . import tieba_uid2user_info

        return await tieba_uid2user_info.request_http(self._connector, self.core, tieba_uid)

    async def get_threads(
        self, fname_or_fid: Union[str, int], /, pn: int = 1, *, rn: int = 30, sort: int = 5, is_good: bool = False
    ) -> "get_threads.Threads":
        """
        获取首页帖子

        Args:
            fname_or_fid (str | int): 贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30. Max to 100.
            sort (int, optional): 排序方式 对于有热门分区的贴吧 0是热门排序 1是按发布时间 2报错 34都是热门排序 >=5是按回复时间
                对于无热门分区的贴吧 0是按回复时间 1是按发布时间 2报错 >=3是按回复时间. Defaults to 5.
            is_good (bool, optional): True则获取精品区帖子 False则获取普通区帖子. Defaults to False.

        Returns:
            Threads: 帖子列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        from . import get_threads

        return await get_threads.request_http(self._connector, self._core, fname, pn, rn, sort, is_good)

    async def get_posts(
        self,
        tid: int,
        /,
        pn: int = 1,
        *,
        rn: int = 30,
        sort: int = 0,
        only_thread_author: bool = False,
        with_comments: bool = False,
        comment_sort_by_agree: bool = True,
        comment_rn: int = 4,
        is_fold: bool = False,
    ) -> "get_posts.Posts":
        """
        获取主题帖内回复

        Args:
            tid (int): 所在主题帖tid
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 30.
            sort (int, optional): 0则按时间顺序请求 1则按时间倒序请求 2则按热门序请求. Defaults to 0.
            only_thread_author (bool, optional): True则只看楼主 False则请求全部. Defaults to False.
            with_comments (bool, optional): True则同时请求高赞楼中楼 False则返回的Posts.comments为空. Defaults to False.
            comment_sort_by_agree (bool, optional): True则楼中楼按点赞数顺序 False则楼中楼按时间顺序. Defaults to True.
            comment_rn (int, optional): 请求的楼中楼数量. Defaults to 4. Max to 50.
            is_fold (bool, optional): 是否请求被折叠的回复. Defaults to False.

        Returns:
            Posts: 回复列表
        """

        from . import get_posts

        return await get_posts.request_http(
            self._connector,
            self._core,
            tid,
            pn,
            rn,
            sort,
            only_thread_author,
            with_comments,
            comment_sort_by_agree,
            comment_rn,
            is_fold,
        )

    async def get_comments(
        self, tid: int, pid: int, /, pn: int = 1, *, is_floor: bool = False
    ) -> "get_comments.Comments":
        """
        获取楼中楼回复

        Args:
            tid (int): 所在主题帖tid
            pid (int): 所在回复pid或楼中楼pid
            pn (int, optional): 页码. Defaults to 1.
            is_floor (bool, optional): pid是否指向楼中楼. Defaults to False.

        Returns:
            Comments: 楼中楼列表
        """

        from . import get_comments

        return await get_comments.request_http(self._connector, self._core, tid, pid, pn, is_floor)

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
    ) -> "search_post.Searches":
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

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        from . import search_post

        return await search_post.request(self._connector, self._core, fname, query, pn, rn, query_type, only_thread)

    async def get_forum_detail(self, fname_or_fid: Union[str, int]) -> "get_forum_detail.Forum_detail":
        """
        通过forum_id获取贴吧信息

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            Forum_detail: 贴吧信息
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        from . import get_forum_detail

        return await get_forum_detail.request(self._connector, self._core, fid)

    async def get_bawu_info(self, fname_or_fid: Union[str, int]) -> Dict[str, List["get_bawu_info.UserInfo_bawu"]]:
        """
        获取吧务信息

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            dict[str, list[UserInfo_bawu]]: {吧务类型: list[吧务用户信息]}
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        from . import get_bawu_info

        return await get_bawu_info.request_http(self._connector, self._core, fid)

    async def get_tab_map(self, fname_or_fid: Union[str, int]) -> Dict[str, int]:
        """
        获取分区名到分区id的映射字典

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先贴吧名

        Returns:
            dict[str, int]: {分区名:分区id}
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        from . import get_tab_map

        return await get_tab_map.request_http(self._connector, self._core, fname)

    async def get_rank_users(self, fname_or_fid: Union[str, int], /, pn: int = 1) -> "get_rank_users.RankUsers":
        """
        获取pn页的等级排行榜用户列表

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            RankUsers: 等级排行榜用户列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        from . import get_rank_users

        return await get_rank_users.request(self._connector, self._core, fname, pn)

    async def get_member_users(self, fname_or_fid: Union[str, int], /, pn: int = 1) -> "get_member_users.MemberUsers":
        """
        获取pn页的最新关注用户列表

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            MemberUsers: 最新关注用户列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        from . import get_member_users

        return await get_member_users.request(self._connector, self._core, fname, pn)

    async def get_square_forums(self, cname: str, /, pn: int = 1, *, rn: int = 20) -> "get_square_forums.SquareForums":
        """
        获取吧广场列表

        Args:
            cname (str): 类别名
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 20. Max to Inf.

        Returns:
            SquareForums: 吧广场列表
        """

        from . import get_square_forums

        return await get_square_forums.request_http(self._connector, self._core, cname, pn, rn)

    async def get_homepage(
        self, _id: Union[str, int], *, with_threads: bool = True
    ) -> Tuple["get_homepage.UserInfo_home", List["get_homepage.Thread_home"]]:
        """
        获取用户个人页信息

        Args:
            _id (str | int): 用户id user_id / user_name / portrait 优先portrait
            with_threads (bool, optional): True则同时请求主页帖子列表 False则返回的threads为空. Defaults to True.

        Returns:
            tuple[UserInfo_home, list[Thread_home]]: 用户信息, list[帖子信息]
        """

        if not is_portrait(_id):
            user = await self.get_user_info(_id, ReqUInfo.PORTRAIT)
            portrait = user._portrait
        else:
            portrait = _id

        from . import get_homepage

        return await get_homepage.request_http(self._connector, self._core, portrait, with_threads)

    async def get_statistics(self, fname_or_fid: Union[str, int]) -> Dict[str, List[int]]:
        """
        获取吧务后台中最近29天的统计数据

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            dict[str, list[int]]: {字段名:按时间顺序排列的统计数据}
            {'view': 浏览量,
             'thread': 主题帖数,
             'new_member': 新增关注数,
             'post': 回复数,
             'sign_ratio': 签到率,
             'average_time': 人均浏览时长,
             'average_times': 人均进吧次数,
             'recommend': 首页推荐数}
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        from . import get_statistics

        return await get_statistics.request(self._connector, self._core, fid)

    async def get_follow_forums(
        self, _id: Union[str, int], /, pn: int = 1, *, rn: int = 50
    ) -> "get_follow_forums.FollowForums":
        """
        获取用户关注贴吧列表

        Args:
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 50. Max to Inf.

        Returns:
            FollowForums: 用户关注贴吧列表
        """

        if not isinstance(_id, int):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
            user_id = user.user_id
        else:
            user_id = _id

        from . import get_follow_forums

        return await get_follow_forums.request(self._connector, self._core, user_id, pn, rn)

    async def get_recom_status(self, fname_or_fid: Union[str, int]) -> "get_recom_status.RecomStatus":
        """
        获取大吧主推荐功能的月度配额状态

        Args:
            fname_or_fid (str | int): 目标贴吧名或fid 优先fid

        Returns:
            RecomStatus: 大吧主推荐功能的月度配额状态
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        from . import get_recom_status

        return await get_recom_status.request(self._connector, self._core, fid)

    async def block(
        self, fname_or_fid: Union[str, int], /, _id: Union[str, int], *, day: Literal[1, 3, 10] = 1, reason: str = ''
    ) -> bool:
        """
        封禁用户

        Args:
            fname_or_fid (str | int): 所在贴吧的贴吧名或fid
            _id (str | int): 用户id user_id / user_name / portrait 优先portrait
            day (Literal[1, 3, 10], optional): 封禁天数. Defaults to 1.
            reason (str, optional): 封禁理由. Defaults to ''.

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        if not is_portrait(_id):
            user = await self.get_user_info(_id, ReqUInfo.PORTRAIT)
            portrait = user._portrait
        else:
            portrait = _id

        await self.__init_tbs()

        from . import block

        return await block.request(self._connector, self._core, fname, fid, portrait, day, reason)

    async def unblock(self, fname_or_fid: Union[str, int], /, _id: Union[str, int]) -> bool:
        """
        解封用户

        Args:
            fname_or_fid (str | int): 所在贴吧的贴吧名或fid
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        if not isinstance(_id, int):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
            user_id = user._user_id
        else:
            user_id = _id

        await self.__init_tbs()

        from . import unblock

        return await unblock.request(self._connector, self._core, fname, fid, user_id)

    async def hide_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        屏蔽主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待屏蔽的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        await self.__init_tbs()

        from . import del_thread

        return await del_thread.request(self._connector, self._core, fid, tid, is_hide=True)

    async def del_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        删除主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待删除的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        await self.__init_tbs()

        from . import del_thread

        return await del_thread.request(self._connector, self._core, fid, tid, is_hide=False)

    async def del_threads(self, fname_or_fid: Union[str, int], /, tids: List[int], *, block: bool = False) -> bool:
        """
        批量删除主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tids (list[int]): 待删除的主题帖tid列表. Length Max to 30.
            block (bool, optional): 是否同时封一天. Defaults to False.

        Returns:
            bool: True成功 False失败 部分成功返回True
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        await self.__init_tbs()

        from . import del_threads

        return await del_threads.request(self._connector, self._core, fid, tids, block)

    async def del_post(self, fname_or_fid: Union[str, int], /, pid: int) -> bool:
        """
        删除回复

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            pid (int): 待删除的回复pid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        await self.__init_tbs()

        from . import del_post

        return await del_post.request(self._connector, self._core, fid, pid)

    async def del_posts(self, fname_or_fid: Union[str, int], /, pids: List[int], *, block: bool = False) -> bool:
        """
        批量删除回复

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            pids (list[int]): 待删除的回复pid列表. Length Max to 30.
            block (bool, optional): 是否同时封一天. Defaults to False.

        Returns:
            bool: True成功 False失败 部分成功返回True
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        await self.__init_tbs()

        from . import del_posts

        return await del_posts.request(self._connector, self._core, fid, pids, block)

    async def unhide_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        解除主题帖屏蔽

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int, optional): 待解除屏蔽的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        await self.__init_tbs()

        from . import recover

        return await recover.request(self._connector, self._core, fname, fid, tid, 0, is_hide=True)

    async def recover_thread(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        恢复主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int, optional): 待恢复的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        await self.__init_tbs()

        from . import recover

        return await recover.request(self._connector, self._core, fname, fid, tid, 0, is_hide=False)

    async def recover_post(self, fname_or_fid: Union[str, int], /, pid: int) -> bool:
        """
        恢复主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            pid (int, optional): 待恢复的回复pid

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        await self.__init_tbs()

        from . import recover

        return await recover.request(self._connector, self._core, fname, fid, 0, pid, is_hide=False)

    async def recover(
        self, fname_or_fid: Union[str, int], /, tid: int = 0, pid: int = 0, *, is_hide: bool = False
    ) -> bool:
        """
        帖子恢复相关操作

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int, optional): 待恢复的主题帖tid. Defaults to 0.
            pid (int, optional): 待恢复的回复pid. Defaults to 0.
            is_hide (bool, optional): True则取消屏蔽主题帖 False则恢复删帖. Defaults to False.

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        await self.__init_tbs()

        from . import recover

        return await recover.request(self._connector, self._core, fname, fid, tid, pid, is_hide)

    async def move(self, fname_or_fid: Union[str, int], /, tid: int, *, to_tab_id: int, from_tab_id: int = 0) -> bool:
        """
        将主题帖移动至另一分区

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待移动的主题帖tid
            to_tab_id (int): 目标分区id
            from_tab_id (int, optional): 来源分区id 默认为0即无分区. Defaults to 0.

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        await self.__init_tbs()

        from . import move

        return await move.request(self._connector, self._core, fid, tid, to_tab_id, from_tab_id)

    async def recommend(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        大吧主首页推荐

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid 优先fid
            tid (int): 待推荐的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        from . import recommend

        return await recommend.request(self._connector, self._core, fid, tid)

    async def good(self, fname_or_fid: Union[str, int], /, tid: int, *, cname: str = '') -> bool:
        """
        加精主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待加精的主题帖tid
            cname (str, optional): 待添加的精华分区名称 默认为''即不分区. Defaults to ''.

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        await self.__init_tbs()

        cid = await self._get_cid(fname_or_fid, cname)

        from . import good

        return await good.request(self._connector, self._core, fname, fid, tid, cid)

    async def ungood(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        撤精主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待撤精的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        await self.__init_tbs()

        from . import ungood

        return await ungood.request(self._connector, self._core, fname, fid, tid)

    async def _get_cid(self, fname_or_fid: Union[str, int], /, cname: str) -> int:
        """
        通过加精分区名获取加精分区id

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            cname (str): 加精分区名

        Returns:
            int: 加精分区id
        """

        if cname == '':
            return 0

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        from . import get_cid

        cates = await get_cid.request(self._connector, self._core, fname)

        cid = 0
        for item in cates:
            if cname == item['class_name']:
                cid = int(item['class_id'])
                break

        return cid

    async def top(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        置顶主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待置顶的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        await self.__init_tbs()

        from . import top

        return await top.request(self._connector, self._core, fname, fid, tid, is_set=True)

    async def untop(self, fname_or_fid: Union[str, int], /, tid: int) -> bool:
        """
        撤销置顶主题帖

        Args:
            fname_or_fid (str | int): 帖子所在贴吧的贴吧名或fid
            tid (int): 待撤销置顶的主题帖tid

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        await self.__init_tbs()

        from . import top

        return await top.request(self._connector, self._core, fname, fid, tid, is_set=False)

    async def get_recovers(
        self, fname_or_fid: Union[str, int], /, name: str = '', pn: int = 1
    ) -> "get_recovers.Recovers":
        """
        获取pn页的待恢复帖子列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid
            name (str, optional): 通过被删帖作者的用户名/昵称查询 默认为空即查询全部. Defaults to ''.
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            Recovers: 待恢复帖子列表
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        from . import get_recovers

        return await get_recovers.request(self._connector, self._core, fname, fid, name, pn)

    async def get_blocks(self, fname_or_fid: Union[str, int], /, name: str = '', pn: int = 1) -> "get_blocks.Blocks":
        """
        获取pn页的待解封用户列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid
            name (str, optional): 通过被封禁用户的用户名/昵称查询 默认为空即查询全部. Defaults to ''.
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            Blocks: 待解封用户列表
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        from . import get_blocks

        return await get_blocks.request(self._connector, self._core, fname, fid, name, pn)

    async def get_blacklist_users(
        self, fname_or_fid: Union[str, int], /, pn: int = 1
    ) -> "get_blacklist_users.BlacklistUsers":
        """
        获取pn页的黑名单用户列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先贴吧名
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            BlacklistUsers: 黑名单用户列表
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        from . import get_blacklist_users

        return await get_blacklist_users.request(self._connector, self._core, fname, pn)

    async def blacklist_add(self, fname_or_fid: Union[str, int], /, _id: Union[str, int]) -> bool:
        """
        添加贴吧黑名单

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先贴吧名
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        if not isinstance(_id, int):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
            user_id = user._user_id
        else:
            user_id = _id

        await self.__init_tbs()

        from . import blacklist_add

        return await blacklist_add.request(self._connector, self._core, fname, user_id)

    async def blacklist_del(self, fname_or_fid: Union[str, int], /, _id: Union[str, int]) -> bool:
        """
        移出贴吧黑名单

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid 优先贴吧名
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)

        if not isinstance(_id, int):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
            user_id = user._user_id
        else:
            user_id = _id

        await self.__init_tbs()

        from . import blacklist_del

        return await blacklist_del.request(self._connector, self._core, fname, user_id)

    async def get_unblock_appeals(
        self, fname_or_fid: Union[str, int], /, pn: int = 1, *, rn: int = 5
    ) -> "get_unblock_appeals.Appeals":
        """
        获取申诉请求列表

        Args:
            fname_or_fid (str | int): 目标贴吧的贴吧名或fid
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 5. Max to 50.

        Returns:
            Appeals: 申诉请求列表
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        await self.__init_tbs()

        from . import get_unblock_appeals

        return await get_unblock_appeals.request(self._connector, self._core, fname, fid, pn, rn)

    async def handle_unblock_appeals(
        self, fname_or_fid: Union[str, int], /, appeal_ids: List[int], *, refuse: bool = True
    ) -> bool:
        """
        拒绝或通过解封申诉

        Args:
            fname_or_fid (str | int): 申诉所在贴吧的贴吧名或fid
            appeal_ids (list[int]): 申诉请求的appeal_id列表. Length Max to 30.
            refuse (bool, optional): True则拒绝申诉 False则接受申诉. Defaults to True.

        Returns:
            bool: True成功 False失败
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        await self.__init_tbs()

        from . import handle_unblock_appeals

        return await handle_unblock_appeals.request(self._connector, self._core, fname, fid, appeal_ids, refuse)

    async def get_image(self, img_url: str) -> "np.ndarray":
        """
        从链接获取静态图像

        Args:
            img_url (str): 图像链接

        Returns:
            np.ndarray: 图像
        """

        from . import get_image

        return await get_image.request(self._connector, self._core, yarl.URL(img_url))

    async def hash2image(self, raw_hash: str, /, size: Literal['s', 'm', 'l'] = 's') -> "np.ndarray":
        """
        通过百度图库hash获取静态图像

        Args:
            raw_hash (str): 百度图库hash
            size (Literal['s', 'm', 'l'], optional): 获取图像的大小 s为宽720 m为宽960 l为原图. Defaults to 's'.

        Returns:
            np.ndarray: 图像
        """

        from . import get_image

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
            import numpy as np

            LOG().warning(f"Invalid size={size}")
            image = np.empty(0, dtype=np.uint8)
            return image

        return await get_image.request(self._connector, self._core, img_url)

    async def get_portrait(self, _id: Union[str, int], /, size: Literal['s', 'm', 'l'] = 's') -> "np.ndarray":
        """
        获取用户头像

        Args:
            _id (str | int): 用户id user_id / user_name / portrait 优先portrait
            size (Literal['s', 'm', 'l'], optional): 获取头像的大小 s为55x55 m为110x110 l为原图. Defaults to 's'.

        Returns:
            np.ndarray: 头像
        """

        if not is_portrait(_id):
            user = await self.get_user_info(_id, ReqUInfo.PORTRAIT)
            portrait = user._portrait
        else:
            portrait = _id

        from . import get_image

        if size == 's':
            path = 'n'
        elif size == 'm':
            path = ''
        elif size == 'l':
            path = 'h'
        else:
            import numpy as np

            LOG().warning(f"Invalid size={size}")
            image = np.empty(0, dtype=np.uint8)
            return image

        img_url = yarl.URL.build(scheme="http", host="tb.himg.baidu.com", path=f"/sys/portrait{path}/item/{portrait}")

        return await get_image.request(self._connector, self._core, img_url)

    async def __get_selfinfo_initNickname(self) -> bool:
        """
        获取本账号信息

        Returns:
            bool: True成功 False失败
        """

        from . import get_selfinfo_initNickname

        user = await get_selfinfo_initNickname.request(self._connector, self._core)

        if user._tieba_uid:
            self._user._user_name = user._user_name
            self._user._tieba_uid = user._tieba_uid
            return True
        else:
            return False

    async def get_newmsg(self) -> Dict[str, bool]:
        """
        获取消息通知

        Returns:
            dict[str, bool]: msg字典 value=True则表示有新内容
            {'fans': 新粉丝,
             'replyme': 新回复,
             'atme': 新@,
             'agree': 新赞同,
             'pletter': 新私信,
             'bookmark': 新收藏,
             'count': 新通知}
        """

        from . import get_newmsg

        return await get_newmsg.request(self._connector, self._core)

    async def get_replys(self, pn: int = 1) -> "get_replys.Replys":
        """
        获取回复信息

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            Replys: 回复列表
        """

        from . import get_replys

        return await get_replys.request_http(self._connector, self._core, pn)

    async def get_ats(self, pn: int = 1) -> "get_ats.Ats":
        """
        获取@信息

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            Ats: at列表
        """

        from . import get_ats

        return await get_ats.request(self._connector, self._core, pn)

    async def get_self_public_threads(self, pn: int = 1) -> List["get_user_contents.UserThread"]:
        """
        获取本人发布的公开状态的主题帖列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            list[UserThread]: 主题帖列表
        """

        user = await self.get_self_info(ReqUInfo.USER_ID)

        from .get_user_contents import get_threads

        return await get_threads.request_http(self._connector, self._core, user.user_id, pn, public_only=True)

    async def get_self_threads(self, pn: int = 1) -> List["get_user_contents.UserThread"]:
        """
        获取本人发布的主题帖列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            list[UserThread]: 主题帖列表
        """

        user = await self.get_self_info(ReqUInfo.USER_ID)

        from .get_user_contents import get_threads

        return await get_threads.request_http(self._connector, self._core, user.user_id, pn, public_only=False)

    async def get_self_posts(self, pn: int = 1) -> List["get_user_contents.UserPosts"]:
        """
        获取本人发布的回复列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            list[UserPosts]: 回复列表
        """

        user = await self.get_self_info(ReqUInfo.USER_ID)

        from .get_user_contents import get_posts

        return await get_posts.request_http(self._connector, self._core, user.user_id, pn)

    async def get_user_threads(self, _id: Union[str, int], pn: int = 1) -> List["get_user_contents.UserThread"]:
        """
        获取用户发布的主题帖列表

        Args:
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            list[UserThread]: 主题帖列表
        """

        if not isinstance(_id, int):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
            user_id = user._user_id
        else:
            user_id = _id

        from .get_user_contents import get_threads

        return await get_threads.request_http(self._connector, self._core, user_id, pn, public_only=True)

    async def get_fans(self, _id: Union[str, int, None] = None, /, pn: int = 1) -> "get_fans.Fans":
        """
        获取粉丝列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            _id (str | int | None): 用户id user_id / user_name / portrait 优先user_id
                默认为None即获取本账号信息. Defaults to None.

        Returns:
            Fans: 粉丝列表
        """

        if _id is None:
            user = await self.get_self_info(ReqUInfo.USER_ID)
            user_id = user._user_id
        elif not isinstance(_id, int):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
            user_id = user._user_id
        else:
            user_id = _id

        from . import get_fans

        return await get_fans.request(self._connector, self._core, user_id, pn)

    async def get_follows(self, _id: Union[str, int, None] = None, /, pn: int = 1) -> "get_follows.Follows":
        """
        获取关注列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            _id (str | int | None): 用户id user_id / user_name / portrait 优先user_id
                默认为None即获取本账号信息. Defaults to None.

        Returns:
            Follows: 关注列表
        """

        if _id is None:
            user = await self.get_self_info(ReqUInfo.USER_ID)
            user_id = user._user_id
        elif not isinstance(_id, int):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
            user_id = user._user_id
        else:
            user_id = _id

        from . import get_follows

        return await get_follows.request(self._connector, self._core, user_id, pn)

    async def get_self_follow_forums(self, pn: int = 1) -> "get_self_follow_forums.SelfFollowForums":
        """
        获取本账号关注贴吧列表

        Args:
            pn (int, optional): 页码. Defaults to 1.

        Returns:
            SelfFollowForums: 本账号关注贴吧列表

        Note:
            本接口需要STOKEN
        """

        from . import get_self_follow_forums

        return await get_self_follow_forums.request(self._connector, self._core, pn)

    async def get_dislike_forums(self, pn: int = 1, /, *, rn: int = 20) -> "get_dislike_forums.DislikeForums":
        """
        获取首页推荐屏蔽的贴吧列表

        Args:
            pn (int, optional): 页码. Defaults to 1.
            rn (int, optional): 请求的条目数. Defaults to 20. Max to 20.

        Returns:
            DislikeForums: 首页推荐屏蔽的贴吧列表
        """

        from . import get_dislike_forums

        return await get_dislike_forums.request_http(self._connector, self._core, pn, rn)

    async def agree(self, tid: int, pid: int = 0) -> bool:
        """
        点赞主题帖或回复

        Args:
            tid (int): 待点赞的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待点赞的回复pid. Defaults to 0.

        Returns:
            bool: True成功 False失败

        Note:
            本接口仍处于测试阶段
            高频率调用会导致<发帖秒删>！请谨慎使用！
        """

        await self.__init_tbs()

        from . import agree

        return await agree.request(self._connector, self._core, tid, pid, is_disagree=False, is_undo=False)

    async def unagree(self, tid: int, pid: int = 0) -> bool:
        """
        取消点赞主题帖或回复

        Args:
            tid (int): 待取消点赞的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待取消点赞的回复pid. Defaults to 0.

        Returns:
            bool: True成功 False失败
        """

        await self.__init_tbs()

        from . import agree

        return await agree.request(self._connector, self._core, tid, pid, is_disagree=False, is_undo=True)

    async def disagree(self, tid: int, pid: int = 0) -> bool:
        """
        点踩主题帖或回复

        Args:
            tid (int): 待点踩的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待点踩的回复pid. Defaults to 0.

        Returns:
            bool: True成功 False失败
        """

        await self.__init_tbs()

        from . import agree

        return await agree.request(self._connector, self._core, tid, pid, is_disagree=True, is_undo=False)

    async def undisagree(self, tid: int, pid: int = 0) -> bool:
        """
        取消点踩主题帖或回复

        Args:
            tid (int): 待取消点踩的主题帖或回复所在的主题帖的tid
            pid (int, optional): 待取消点踩的回复pid. Defaults to 0.

        Returns:
            bool: True成功 False失败
        """

        await self.__init_tbs()

        from . import agree

        return await agree.request(self._connector, self._core, tid, pid, is_disagree=True, is_undo=True)

    async def agree_vimage(self, _id: Union[str, int]) -> bool:
        """
        虚拟形象点赞

        Args:
            _id (str | int): 点赞对象的用户id user_id / user_name / portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        if not isinstance(_id, int):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
            user_id = user._user_id
        else:
            user_id = _id

        from . import agree_vimage

        return await agree_vimage.request(self._connector, self._core, user_id)

    async def remove_fan(self, _id: Union[str, int]) -> bool:
        """
        移除粉丝

        Args:
            _id (str | int): 待移除粉丝的id user_id / user_name / portrait 优先user_id

        Returns:
            bool: True成功 False失败
        """

        if not isinstance(_id, int):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
            user_id = user._user_id
        else:
            user_id = _id

        await self.__init_tbs()

        from . import remove_fan

        return await remove_fan.request(self._connector, self._core, user_id)

    async def follow_user(self, _id: Union[str, int]) -> bool:
        """
        关注用户

        Args:
            _id (str | int): 用户id user_id / user_name / portrait 优先portrait

        Returns:
            bool: True成功 False失败
        """

        if not is_portrait(_id):
            user = await self.get_user_info(_id, ReqUInfo.PORTRAIT)
            portrait = user._portrait
        else:
            portrait = _id

        await self.__init_tbs()

        from . import follow_user

        return await follow_user.request(self._connector, self._core, portrait)

    async def unfollow_user(self, _id: Union[str, int]) -> bool:
        """
        取关用户

        Args:
            _id (str | int): 用户id user_id / user_name / portrait 优先portrait

        Returns:
            bool: True成功 False失败
        """

        if not is_portrait(_id):
            user = await self.get_user_info(_id, ReqUInfo.PORTRAIT)
            portrait = user._portrait
        else:
            portrait = _id

        await self.__init_tbs()

        from . import unfollow_user

        return await unfollow_user.request(self._connector, self._core, portrait)

    async def follow_forum(self, fname_or_fid: Union[str, int]) -> bool:
        """
        关注贴吧

        Args:
            fname_or_fid (str | int): 要关注贴吧的贴吧名或fid 优先fid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        await self.__init_tbs()

        from . import follow_forum

        return await follow_forum.request(self._connector, self._core, fid)

    async def unfollow_forum(self, fname_or_fid: Union[str, int]) -> bool:
        """
        取关贴吧

        Args:
            fname_or_fid (str | int): 要取关贴吧的贴吧名或fid 优先fid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)
        await self.__init_tbs()

        from . import unfollow_forum

        return await unfollow_forum.request(self._connector, self._core, fid)

    async def dislike_forum(self, fname_or_fid: Union[str, int]) -> bool:
        """
        屏蔽贴吧 使其不再出现在首页推荐列表中

        Args:
            fname_or_fid (str | int): 待屏蔽贴吧的贴吧名或fid 优先fid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        from . import dislike_forum

        return await dislike_forum.request(self._connector, self._core, fid)

    async def undislike_forum(self, fname_or_fid: Union[str, int]) -> bool:
        """
        解除贴吧的首页推荐屏蔽

        Args:
            fname_or_fid (str | int): 待屏蔽贴吧的贴吧名或fid 优先fid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        from . import undislike_forum

        return await undislike_forum.request(self._connector, self._core, fid)

    async def set_thread_privacy(self, fname_or_fid: Union[str, int], /, tid: int, pid: int) -> bool:
        """
        隐藏主题帖

        Args:
            fname_or_fid (str | int): 主题帖所在贴吧的贴吧名或fid 优先fid
            tid (int): 主题帖tid
            tid (int): 主题帖pid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        from . import set_thread_privacy

        return await set_thread_privacy.request(self._connector, self._core, fid, tid, pid, is_hide=True)

    async def set_thread_public(self, fname_or_fid: Union[str, int], /, tid: int, pid: int) -> bool:
        """
        公开主题帖

        Args:
            fname_or_fid (str | int): 主题帖所在贴吧的贴吧名或fid 优先fid
            tid (int): 主题帖tid
            tid (int): 主题帖pid

        Returns:
            bool: True成功 False失败
        """

        fid = fname_or_fid if isinstance(fname_or_fid, int) else await self.get_fid(fname_or_fid)

        from . import set_thread_privacy

        return await set_thread_privacy.request(self._connector, self._core, fid, tid, pid, is_hide=False)

    async def set_profile(self, nick_name: str, sign: str = '', gender: int = 0) -> bool:
        """
        设置主页信息

        Args:
            nick_name (str): 昵称
            sign (str): 个性签名. Defaults to ''.
            gender (int): 性别 1男 2女. Defaults to 1.

        Returns:
            bool: True成功 False失败
        """

        from . import set_profile

        return await set_profile.request(self._connector, self._core, nick_name, sign, gender)

    async def set_nickname_old(self, nick_name: str) -> bool:
        """
        设置旧版昵称

        Args:
            nick_name (str): 昵称

        Returns:
            bool: True成功 False失败
        """

        from . import set_nickname_old

        return await set_nickname_old.request(self._connector, self._core, nick_name)

    async def sign_forum(self, fname_or_fid: Union[str, int]) -> bool:
        """
        单个贴吧签到

        Args:
            fname_or_fid (str | int): 要签到贴吧的贴吧名或fid 优先贴吧名

        Returns:
            bool: True成功 False失败
        """

        fname = fname_or_fid if isinstance(fname_or_fid, str) else await self.get_fname(fname_or_fid)
        await self.__init_tbs()

        from . import sign_forum

        return await sign_forum.request(self._connector, self._core, fname)

    async def sign_growth(self) -> bool:
        """
        用户成长等级任务: 签到

        Returns:
            bool: True成功 False失败
        """

        await self.__init_tbs()

        from . import sign_growth

        return await sign_growth.request_app(self._connector, self._core, act_type='page_sign')

    async def sign_growth_share(self) -> bool:
        """
        用户成长等级任务: 分享主题帖

        Returns:
            bool: True成功 False失败
        """

        await self.__init_tbs()

        from . import sign_growth

        return await sign_growth.request_app(self._connector, self._core, act_type='share_thread')

    async def add_post(self, fname_or_fid: Union[str, int], /, tid: int, content: str) -> bool:
        """
        回复主题帖

        Args:
            fname_or_fid (str | int): 要回复的主题帖所在贴吧的贴吧名或fid
            tid (int): 要回复的主题帖的tid
            content (str): 回复内容

        Returns:
            bool: 回帖是否成功

        Note:
            本接口仍处于测试阶段
            高频率调用会导致<永久封禁屏蔽>！请谨慎使用！
            已通过的测试: cookie白板号(无头像无关注吧无发帖记录 2元/个) 通过异地阿里云ip出口以3分钟的发送间隔发15条回复不吞楼不封号
        """

        if isinstance(fname_or_fid, str):
            fname = fname_or_fid
            fid = await self.get_fid(fname)
        else:
            fid = fname_or_fid
            fname = await self.get_fname(fid)

        await self.__init_tbs()
        await self.__init_client_id()

        from . import add_post

        return await add_post.request(self._connector, self._core, fname, fid, tid, content)

    async def send_msg(self, _id: Union[str, int], content: str) -> bool:
        """
        发送私信

        Args:
            _id (str | int): 用户id user_id / user_name / portrait 优先user_id
            content (str): 发送内容

        Returns:
            bool: True成功 False失败
        """

        if not isinstance(_id, int):
            user = await self.get_user_info(_id, ReqUInfo.USER_ID)
            user_id = user._user_id
        else:
            user_id = _id

        try:
            await self.__init_websocket()

            from . import send_msg

            proto = send_msg.pack_proto(user.user_id, content)
            resp = await self.send_ws_bytes(proto, cmd=205001, timeout=5.0)
            send_msg.parse_body(resp)

        except Exception as err:
            LOG().warning(f"{err}. user_id={user_id}")
            return False

        LOG().info(f"Succeeded. user_id={user_id}")
        return True
