# 客户端

## 如何使用

`aiotieba.Client`是aiotieba的核心入口点 (Entry Point)，其中封装了大量操作百度贴吧核心API的简便方法，你可以把它理解成一个“客户端”

我们推荐通过异步上下文管理器来使用`Client`，例如：

```python
async with aiotieba.Client("default") as client:
    ...
```

<details markdown="1"><summary>如果你不了解“上下文管理器”或“异步上下文管理器”</summary>

你可以阅读以下文章快速入门

+ [python黑魔法-上下文管理器](https://piaosanlang.gitbooks.io/faq/content/tornado/pythonhei-mo-6cd5-shang-xia-wen-guan-li-qi-ff08-contextor.html) 中文解读上下文管理器
+ [详解asyncio之异步上下文管理器](https://cloud.tencent.com/developer/article/1488125) 中文解读异步上下文管理器
+ [PEP-492](https://peps.python.org/pep-0492/#asynchronous-context-managers-and-async-with) 异步上下文管理器的PEP标准
+ [Why do we need `async for` and `async with`?](https://stackoverflow.com/questions/67092070/why-do-we-need-async-for-and-async-with) 深入解读`async for`和`async with`的作用

</details>

## 参考文档

class `aiotieba.Client`(*BDUSS_key: Optional[str] = None*)


### 构造参数

**BDUSS_key**

<div class="docstring" markdown="1">
用于快捷调用BDUSS
</div>


### 类属性

**BDUSS_key**

<div class="docstring" markdown="1">
当前`Client`使用的BDUSS_key

*str, 只读*
</div>

**BDUSS** 

<div class="docstring" markdown="1">
当前`Client`使用的[BDUSS](../tutorial/quickstart.md#BDUSS)

*str, 只读*
</div>

**STOKEN**

<div class="docstring" markdown="1">
当前`Client`使用的STOKEN

*str, 只读*
</div>

**is_ws_aviliable**

<div class="docstring" markdown="1">
`self.websocket`是否可用

*bool, 只读*
</div>


### 类方法

async def `login`() -> *bool*

<div class="docstring" markdown="1">
登录并获取tbs和当前账号的简略版用户信息

**Returns**: True成功 False失败
</div>

async def `get_fid`(*fname: str*) -> *int*

<div class="docstring" markdown="1">
通过贴吧名获取forum_id

**Returns**: [forum_id](../tutorial/quickstart.md#forum_id)
</div>
