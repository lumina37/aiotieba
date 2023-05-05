# 客户端

## 如何使用

`aiotieba.Client`是aiotieba的核心入口点 (Entry Point)，其中封装了大量操作百度贴吧核心API的简便方法，你可以把它理解成一个“客户端”

我们推荐通过异步上下文管理器来使用`Client`，例如：

```python
async with aiotieba.Client() as client:
    ...
```

## Client

class `aiotieba.Client`(*BDUSS_key: str | None = None*, *try_ws: bool = False*, *proxy: tuple[[yarl.URL](https://yarl.aio-libs.org/en/latest/api.html#yarl.URL), [aiohttp.BasicAuth](https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.BasicAuth)] | bool = False*, *time_cfg: TimeConfig = TimeConfig()*, *loop: [asyncio.AbstractEventLoop](https://docs.python.org/zh-cn/3/library/asyncio-eventloop.html#event-loop) | None = None*)

### 构造参数

<div class="docstring" markdown="1">
**BDUSS_key** - 用于快捷调用BDUSS

**try_ws** - 尝试使用websocket接口

**proxy** - True则使用环境变量代理 False则禁用代理 输入一个（http代理地址, 代理验证）的元组以手动设置代理

**time_cfg** - 各种时间设置

**loop** - 事件循环
</div>

### 类属性

<div class="docstring" markdown="1">
**account** - *(Account)* 贴吧用户信息容器
</div>

### 类方法

async def `get_fid`(*fname: str*) -> *int*

<div class="docstring" markdown="1">
通过贴吧名获取forum_id

**参数**: 贴吧名

**返回**: [forum_id](../tutorial/start.md#forum_id)
</div>


async def `get_fname`(*fid: int*) -> *str*

<div class="docstring" markdown="1">
通过forum_id获取贴吧名

**参数**: [forum_id](../tutorial/start.md#forum_id)

**返回**: 贴吧名
</div>


async def `get_user_info`(*_id: str | int*, /, *require: [ReqUInfo](enum.md#requinfo) = [ReqUInfo](enum.md#requinfo).ALL*) -> *[UserInfo](classdef.md#userinfo)*

<div class="docstring" markdown="1">
获取用户信息

**参数**:

+ _id: 用户id [user_id](../tutorial/start.md#user_id) / [portrait](../tutorial/start.md#portrait) / [user_name](../tutorial/start.md#user_name)
+ require: 指示需要获取的字段

**返回**: 用户信息
</div>

async def `tieba_uid2user_info`(*tieba_uid: int*) -> *[UserInfo](classdef.md#userinfo)*

<div class="docstring" markdown="1">
通过[tieba_uid](../tutorial/start.md#tieba_uid)获取用户信息

**参数**:

+ tieba_uid: 用户id [tieba_uid](../tutorial/start.md#tieba_uid)

**返回**: 用户信息
</div>

async def `get_threads`(*fname_or_fid: str | int*, /, *pn: int = 1*, \*, *rn: int = 30*, *sort: ThreadSortType = ThreadSortType.REPLY*, *is_good: bool = False*) -> *[Threads](classdef.md#threads)*

<div class="docstring" markdown="1">
获取首页帖子

**参数**:

+ fname_or_fid: 贴吧名或[fid](../tutorial/start.md#forum_id) 优先贴吧名
+ pn: 页码
+ rn: 请求的条目数
+ sort: 排序方式<br>
  对于有热门分区的贴吧 0热门排序 1按发布时间 2关注的人 34热门排序 >=5是按回复时间<br>
  对于无热门分区的贴吧 0按回复时间 1按发布时间 2关注的人 >=3按回复时间
+ is_good: True则获取精品区帖子 False则获取普通区帖子

**返回**: 帖子列表
</div>

async def `get_posts`(*tid: int*, /, *pn: int = 1*, \*, *rn: int = 30*, *sort: PostSortType = PostSortType.ASC*, *only_thread_author: bool = False*, *with_comments: bool = False*, *comment_sort_by_agree: bool = True*, *comment_rn: int = 4*, *is_fold: bool = False*) -> *[Posts](classdef.md#posts)*

<div class="docstring" markdown="1">
获取回复列表

**参数**:

+ tid: 所在主题帖[tid](../tutorial/start.md#thread_id)
+ pn: 页码
+ rn: 请求的条目数
+ sort: 排序方式 0时间顺序 1时间倒序 2热门序
+ only_thread_author: True则只看楼主 False则请求全部
+ with_comments: True则同时请求高赞楼中楼 False则返回的Posts.comments为空
+ comment_sort_by_agree: True则楼中楼按点赞数顺序 False则楼中楼按时间顺序
+ comment_rn: 请求的楼中楼数量
+ is_fold: 是否请求被折叠的回复

**返回**: 回复列表
</div>

async def `get_comments`(*tid: int*, *pid: int*, /, *pn: int = 1*, \*, *is_comment: bool = False*) -> *[Comments](classdef.md#comments)*

<div class="docstring" markdown="1">
获取楼中楼列表

**参数**:

+ tid: 所在主题帖[tid](../tutorial/start.md#thread_id)
+ pid: 所在楼层的[pid](../tutorial/start.md#post_id)或楼中楼的[pid](../tutorial/start.md#post_id)
+ pn: 页码
+ is_comment: pid是否指向楼中楼 若指向楼中楼则获取其附近的楼中楼列表

**返回**: 楼中楼列表
</div>
