# 客户端

## 如何使用

`aiotieba.Client`是aiotieba的核心入口点 (Entry Point)，其中封装了大量操作百度贴吧核心API的简便方法，你可以把它理解成一个“客户端”

我们推荐通过异步上下文管理器来使用`Client`，例如：

```python
async with aiotieba.Client("default") as client:
    ...
```

或者，你也可以手动调用`Client`的`__aenter__`方法完成资源初始化、`__aexit__`方法完成资源的释放和清理工作，例如：

```python
client = aiotieba.Client("default")
await client.__aenter__()
...
await client.__aexit__()
```

<details markdown="1"><summary>如果你不了解“上下文管理器”或“异步上下文管理器”</summary>

你可以阅读以下文章快速入门

+ [python黑魔法-上下文管理器](https://piaosanlang.gitbooks.io/faq/content/tornado/pythonhei-mo-6cd5-shang-xia-wen-guan-li-qi-ff08-contextor.html) 中文解读上下文管理器
+ [详解asyncio之异步上下文管理器](https://cloud.tencent.com/developer/article/1488125) 中文解读异步上下文管理器
+ [PEP-492](https://peps.python.org/pep-0492/#asynchronous-context-managers-and-async-with) 异步上下文管理器的PEP标准
+ [Why do we need `async for` and `async with`?](https://stackoverflow.com/questions/67092070/why-do-we-need-async-for-and-async-with) 深入解读`async for`和`async with`的作用

</details>

## 类方法文档

class aiotieba.**Client**(*BDUSS_key: Optional[str] = None*)

<div class="docstring" markdown="1">

**参数**

+ **BDUSS_key** - 用于快捷调用BDUSS

</div>

<div class="docstring" markdown="1">

**属性**

+ **BDUSS_key** *(str, 只读)* - 当前`Client`使用的BDUSS_key
+ **BDUSS** *(str, 首次写入后只读)* - 当前`Client`使用的[BDUSS](../tutorial/quickstart.md#BDUSS)
+ **STOKEN** *(str, 首次写入后只读)* - 当前`Client`使用的STOKEN
+ **timestamp_ms** *(int, 只读)* - 毫秒级本机时间戳 (13位整数)
+ **client_id** *(str, 只读)* - 返回一个可作为请求参数的client_id 例如`wappc_1653660000000_123`
+ **cuid** *(str, 只读)* - 返回一个可作为请求参数的cuid 例如`baidutiebaappe4200716-58a8-4170-af15-ea7edeb8e513`

</div>
