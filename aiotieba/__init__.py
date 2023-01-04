"""
Asynchronous I/O Client/Reviewer for Baidu Tieba

@Author: starry.qvq@gmail.com
@License: Unlicense
@Documentation: https://v-8.top/
"""

import os

from ._logger import LOG
from .client import Client
from .client.common.typedef import (
    Appeal,
    Appeals,
    At,
    Ats,
    BasicForum,
    BlacklistUsers,
    Comment,
    Comments,
    DislikeForums,
    Fans,
    FollowForums,
    Follows,
    Forum,
    FragAt,
    FragEmoji,
    FragImage,
    FragItem,
    FragLink,
    Fragments,
    FragmentUnknown,
    FragText,
    FragTiebaPlus,
    MemberUser,
    MemberUsers,
    NewThread,
    Page,
    Post,
    Posts,
    RankUser,
    RankUsers,
    RecomThreads,
    Recover,
    Recovers,
    Reply,
    Replys,
    ReqUInfo,
    Search,
    Searches,
    SelfFollowForums,
    ShareThread,
    SquareForum,
    SquareForums,
    Thread,
    Threads,
    UserInfo,
    UserPost,
    UserPosts,
    VirtualImage,
    VoteInfo,
)
from .database import MySQLDB, SQLiteDB
from .reviewer import BaseReviewer, Ops, Punish, Reviewer

__version__ = "2.10.1"

if os.name == 'posix':
    import signal

    def terminate(signal_number, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, terminate)
