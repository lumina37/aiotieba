"""
@Author: starry.qvq@gmail.com
@License: Unlicense
@Homepage: https://github.com/Starry-OvO/Tieba-Manager
"""

import os

from ._helpers import DelFlag, Punish
from ._logger import LOG
from .client import Client
from .reviewer import Reviewer, ReviewUtils
from .typedefs import (
    Appeal,
    Appeals,
    At,
    Ats,
    BasicForum,
    BasicUserInfo,
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
    FragVoice,
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
    VoteInfo,
)

__version__ = "2.9.0"

if os.name == 'posix':
    import signal

    def terminate(signal_number, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, terminate)
