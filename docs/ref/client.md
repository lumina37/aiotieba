# 客户端

## 如何使用

`aiotieba.Client`是aiotieba的核心入口点 (Entry Point)，其中封装了大量操作百度贴吧核心API的简便方法，你可以把它理解成一个“客户端”

我们推荐通过异步上下文管理器来使用`Client`，例如：

```python
async with aiotieba.Client() as client:
    ...
```

<details markdown="1"><summary>如果你不了解“上下文管理器”或“异步上下文管理器”</summary>

你可以阅读以下文章快速入门

+ [python黑魔法-上下文管理器](https://piaosanlang.gitbooks.io/faq/content/tornado/pythonhei-mo-6cd5-shang-xia-wen-guan-li-qi-ff08-contextor.html) 中文解读上下文管理器
+ [详解asyncio之异步上下文管理器](https://cloud.tencent.com/developer/article/1488125) 中文解读异步上下文管理器
+ [PEP-492](https://peps.python.org/pep-0492/#asynchronous-context-managers-and-async-with) 异步上下文管理器的PEP标准
+ [Why do we need `async for` and `async with`?](https://stackoverflow.com/questions/67092070/why-do-we-need-async-for-and-async-with) 深入解读`async for`和`async with`的作用

</details>

## Client

class `aiotieba.Client`(*BDUSS_key: str | None = None*)

### 构造参数

<div class="docstring" markdown="1">
**BDUSS_key** - 用于快捷调用BDUSS
</div>

### 类属性

<div class="docstring" markdown="1">
**BDUSS_key** - *(str)* 当前`Client`使用的BDUSS_key

**BDUSS** - *(str)* 当前`Client`使用的[BDUSS](../tutorial/quickstart.md#BDUSS)

**STOKEN** - *(str)* 当前`Client`使用的STOKEN

**is_ws_aviliable** - *(bool)* `Client.websocket`是否可用
</div>

### 类方法

async def `get_fid`(*fname: str*) -> *int*

<div class="docstring" markdown="1">
通过贴吧名获取forum_id

**参数**: 贴吧名

**返回**: [forum_id](../tutorial/quickstart.md#forum_id)
</div>


async def `get_fname`(*fid: int*) -> *str*

<div class="docstring" markdown="1">
通过forum_id获取贴吧名

**参数**: [forum_id](../tutorial/quickstart.md#forum_id)

**返回**: 贴吧名
</div>


async def `get_user_info`(*_id: str | int*, /, *require: [ReqUInfo](#requinfo) = [ReqUInfo](#requinfo).ALL*) -> *[UserInfo](typedefs.md#userinfo)*

<div class="docstring" markdown="1">
获取用户信息

**参数**:

+ _id: 用户id [user_id](../tutorial/quickstart.md#user_id) / [portrait](../tutorial/quickstart.md#portrait) / [user_name](../tutorial/quickstart.md#user_name)
+ require: 指示需要获取的字段

**返回**: 用户信息
</div>

async def `get_threads`(*fname_or_fid: str | int*, /, *pn: int = 1*, \*, *rn: int = 30*, *sort: int = 5*, *is_good: bool = False*) -> *[Threads](typedefs.md#threads)*

<div class="docstring" markdown="1">
获取首页帖子

**参数**:

+ fname_or_fid: 贴吧名或[fid](../tutorial/quickstart.md#forum_id) 优先贴吧名
+ pn: 页码
+ rn: 请求的条目数
+ sort: 排序方式<br>
  对于有热门分区的贴吧 0是热门排序 1是按发布时间 2报错 34都是热门排序 >=5是按回复时间<br>
  对于无热门分区的贴吧 0是按回复时间 1是按发布时间 2报错 >=3是按回复时间
+ is_good: True则获取精品区帖子 False则获取普通区帖子

**返回**: 帖子列表
</div>


## ReqUInfo

使用该枚举类指定待获取的用户信息字段

**USER_ID** = 1 << 0<br>
**PORTRAIT** = 1 << 1<br>
**USER_NAME** = 1 << 2<br>
**NICK_NAME** = 1 << 3<br>
**TIEBA_UID** = 1 << 4<br>
**OTHER** = 1 << 5<br>
**BASIC** = USER_ID | PORTRAIT | USER_NAME<br>
**ALL** = (1 << 6) - 1
