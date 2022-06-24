# aiotieba库使用教程

## 准备知识

想要用好`aiotieba`库，必须初步掌握`Python`异步编程

如果你不熟悉`Python`异步编程，建议阅读下列教程：

+ [轻松理解Python中的async/await](https://blog.csdn.net/Likianta/article/details/90123678) 非常易于理解的入门案例
+ [Python官方文档 协程与任务](https://docs.python.org/zh-cn/3/library/asyncio-task.html) 包含详尽Reference和配套案例的官方文档，更适合有一定基础的初学者
+ [Python Async/Await入门指南](https://zhuanlan.zhihu.com/p/27258289) 已经是17年的文章了，从生成器`yield`的角度出发介绍`Python`异步，对初学者不太友好，更适合拔高阅读
+ [深入理解JavaScript中的async/await](https://www.cnblogs.com/youma/p/10475214.html) `JavaScript`中的`Promise`与`Python`中的`Task`概念很相似，该教程可以帮助你快速地从`Promise`异步模式出发理解`async-await`异步模式

如果你已经对异步编程的相关知识非常熟悉，那么我建议你按`4-1-2-3`的顺序阅读

如果你只是编程初学者或者对各种异步模式一窍不通，那么我建议你按`1-2-3`的顺序阅读

当然即便你没有阅读上面的教程，我也会针对异步编程的初学者为每一行异步代码撰写详细的注释

## 案例1 配置BDUSS

本例中，你将学会`config.toml`配置文件的基本填写方法，并使用`aiotieba`库获取贴吧账号的个人信息

### 步骤1

在`aiotieba`文件夹的旁边新建一个`debug.py`文件。当然你也可以在任何一个可以引用到`aiotieba`库的地方新建脚本，又或是另起一个你喜欢的脚本名

将下列代码复制到`debug.py`并运行

```python
import asyncio

import aiotieba as tb


async def main():
    # 使用键名"default"对应的BDUSS创建客户端
    async with tb.Client("default") as brow:
        # 通过在协程brow.get_self_info前添加await来等待它执行完毕，该协程返回的用户信息会被填入变量user
        user = await brow.get_self_info()

    # 将获取的信息打印到日志
    tb.LOG.info(f"当前用户信息: {user}")


# 执行协程main
# 参考https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio.run
asyncio.run(main())
```
