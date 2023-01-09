from ._classdef.contents import (
    TypeFragAt,
    TypeFragEmoji,
    TypeFragImage,
    TypeFragItem,
    TypeFragLink,
    TypeFragmentUnknown,
    TypeFragText,
    TypeFragTiebaPlus,
)
from .get_comments._classdef import Comment, Comments
from .get_homepage._classdef import UserInfo_home
from .get_posts._classdef import Post, Posts
from .get_threads._classdef import ShareThread, Thread, Threads
from .get_unblock_appeals._classdef import Appeal

TypeUserInfo = UserInfo_home
