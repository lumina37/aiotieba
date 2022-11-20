"""
Asynchronous I/O Client/Reviewer for Baidu Tieba

@Author: starry.qvq@gmail.com
@License: Unlicense
@Documentation: https://v-8.top/
"""

import os

from ._logger import LOG
from .client import Client, ReqUInfo
from .database import MySQLDB, SQLiteDB
from .reviewer import BaseReviewer, Ops, Punish, Reviewer
from .typedef import (
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

__version__ = "2.9.6"

if os.name == 'posix':
    import signal

    def terminate(signal_number, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, terminate)
