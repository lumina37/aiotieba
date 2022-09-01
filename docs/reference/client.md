# 客户端

## 如何使用

我们在`aiotieba.Client`中封装了大量百度贴吧的官方接口，你可以把它理解成一个“客户端”

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

TODO
