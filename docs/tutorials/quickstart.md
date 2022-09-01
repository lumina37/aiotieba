# 快速入门

## 预备知识

我们假定本教程的每位读者都拥有一定的Python编程基础

想要流畅地使用aiotieba库，你应当初步掌握Python异步编程

当然即便你没有异步编程的基础，我也会针对这部分初学者为每一行异步代码撰写详细的注释

<details markdown="1"><summary>如果你不熟悉Python异步编程</summary>

+ [轻松理解Python中的async/await](https://blog.csdn.net/Likianta/article/details/90123678) 非常易于理解的入门案例
+ [Python官方文档 协程与任务](https://docs.python.org/zh-cn/3/library/asyncio-task.html) 包含详尽Reference和配套案例的官方文档，更适合有一定基础的初学者
+ [Python Async/Await入门指南](https://zhuanlan.zhihu.com/p/27258289) 已经是17年的文章了，从生成器`yield`的角度出发介绍Python异步，对初学者不太友好，更适合拔高阅读
+ [深入理解JavaScript中的async/await](https://www.cnblogs.com/youma/p/10475214.html) JavaScript中的`Promise`与Python中的`Future`概念很相似，该教程可以帮助你快速地从Promise异步模式出发理解async-await异步模式

如果你已经从其他编程语言上积累了一些异步编程的知识，那么我建议你按**4-1-2-3**的顺序阅读

如果你只是编程初学者或者对各种异步模式一窍不通，那么我建议你按**1-2-3**的顺序阅读

</details>

## 命名约定

如果你希望从贴吧的服务器爬取数据

那么你应该对以下字段的含义有所了解

### BDUSS

贴吧的服务端使用`BDUSS`来确认用户身份

`BDUSS`是一串由纯`ascii`字符组成的，长度为`192`的字符串

!!! warning

    使用`BDUSS`可以完成**一切**不需要手机/邮箱验证码的操作，包括**发帖**/**发私信**/**获取账号上的所有历史发言**

    `BDUSS`不会在一段时间后过期，只能通过退出登录或修改密码使其失效

    因此将`BDUSS`泄露给不受信任的人可能导致长期的账号安全风险和隐私泄露风险

在浏览器的`Cookie`和各种表单参数中你都能看到它的身影

搜索 `你的浏览器型号`+`如何查看网站的Cookie` 就能知道如何获取你的贴吧账号的`BDUSS`了

以`Chorme`为例，在任何一个贴吧网页下按<kbd>F12</kbd>调出开发者选项，然后你就能在下图的位置找到它

![Chrome Cookie](https://user-images.githubusercontent.com/48282276/179938990-77139ea2-2d94-4d38-8d7d-9c6a3d99b69e.png)

### user_name

用户名

每个贴吧用户的用户名都是唯一的，但用户可以没有用户名

请注意将其与可重复的昵称`nick_name`相区分

在`utf-8`编码下，用户名的长度一般不会超过`14`个字节

### portrait

头像ID

每个贴吧用户都有且仅有一个`portrait`

`portrait`是一串由纯`ascii`字符组成的，以`tb.1.`作为开头的，长度为`33~36`的字符串（仅有一些远古时期的ip账号不符合这个规则）

譬如我的`portrait`就是`tb.1.8277e641.gUE2cTq4A4z5fi2EHn5k3Q`

你可以通过`portrait`获取用户头像，例如[我的头像](http://tb.himg.baidu.com/sys/portraith/item/tb.1.8277e641.gUE2cTq4A4z5fi2EHn5k3Q)

你可以在[client.py](https://github.com/Starry-OvO/Tieba-Manager/blob/master/aiotieba/client.py)中搜索`user.portrait`来查看`portrait`的具体应用场合

### user_id

用户ID

每个贴吧用户都有且仅有一个`user_id`

请注意将其与用户个人主页的`tieba_uid`相区分

`user_id`是一个`uint64`值（仅有一些远古时期的ip账号不符合这个规则）

你可以在[client.py](https://github.com/Starry-OvO/Tieba-Manager/blob/master/aiotieba/client.py)中搜索`user.user_id`来查看`user_id`的具体应用场合

`user_name` `portrait` `user_id` 都是满足唯一性的用户标识符，并可以通过其中任意一个的值反查其余两个

### tieba_uid

用户个人主页ID

每个贴吧用户都有且仅有一个`tieba_uid`

请注意将其与用户的`user_id`相区分

`tieba_uid`是一个`uint64`值（仅有一些远古时期的ip账号不符合这个规则）

可以通过`tieba_uid`的值反查`user_name` `portrait` `user_id`

### fid

吧ID

每个贴吧都有且仅有一个`fid`

`fid`是一个`uint64`值

你可以在[client.py](https://github.com/Starry-OvO/Tieba-Manager/blob/master/aiotieba/client.py)中搜索`fid: int`来查看使用了`fid`作为参数的接口

在贴吧混乱的字段命名中，它在某些场合下会被命名为`forum_id`

### tid

主题帖ID

每个主题帖都有且仅有一个`tid`

`tid`是一个`uint64`值

你可以在[client.py](https://github.com/Starry-OvO/Tieba-Manager/blob/master/aiotieba/client.py)中搜索`tid: int`来查看使用了`tid`作为参数的接口

在贴吧混乱的字段命名中，它在某些场合下会被命名为`thread_id`

### pid

回复ID

每个楼层、楼中楼都有且仅有一个`pid`

`pid`是一个`uint64`值

你可以在[client.py](https://github.com/Starry-OvO/Tieba-Manager/blob/master/aiotieba/client.py)中搜索`pid: int`来查看使用了`pid`作为参数的接口

在贴吧混乱的字段命名中，它在某些场合下会被命名为`post_id`


## 入门案例

*本案例将演示 如何配置BDUSS并获取账号信息*

如果你刚刚已经运行过下列代码

```python
import asyncio

import aiotieba


async def main():
    async with aiotieba.Client() as client:
        print(await client.get_threads("天堂鸡汤"))


asyncio.run(main())
```

那么你可能注意到了一条日志输出

```log
<2022-07-16 20:13:54.514> [WARN] [<module>] 配置文件./aiotieba.toml已生成 请参考注释补充个性化配置
...
```

在工作目录下，你能看到自动生成的`aiotieba.toml`配置文件

如果你需要使用账号相关的功能，那么你需要将你的[`BDUSS`](#BDUSS)填入该文件的正确位置

填写完毕的`aiotieba.toml`大概长这样

```toml
[User]

# default是自定义的BDUSS_key，你可以改成你喜欢的标识
# 该设计是为了方便通过BDUSS_key快速调用BDUSS，这样你就不用每次都填一串很长的东西作为参数
[User.default]
BDUSS = "2dNNk1wMXVSZmw2MnpkWDNqMnM4MmFaeFZYNVVPUEhPS0thNFZzUERjME52V1KpSVFBQUFBJCQAAAAAAQAAAAEAAAA0lUwndl9ndWFyZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0wPmINMD5iY" # 把你的那一串长长的BDUSS放在这
```

然后复制下列代码并运行

```python
import asyncio

import aiotieba as tb


# 定义异步函数main
# 需要明确async def...和def...在定义函数上的区别
# 对于def定义的同步函数func，func()会直接返回结果
# 而对于async def定义的异步函数afunc，afunc()只会返回一个可等待（Awaitable）的协程
# 你需要使用await或asyncio.run或其他语句来等待协程执行完毕后才能拿到返回结果
async def main():
    # 使用键名"default"对应的BDUSS创建客户端
    # async with会先调用tb.Client的__init__方法同步地创建一个实例
    # 再异步调用__aenter__方法来自动完成一些资源初始化工作（如创建连接池），并将返回值赋给client变量
    # 最后，在async with的作用域结束时，tb.Client的__aexit__方法会被自动地异步调用以完成一些清理工作（如关闭所有连接并释放资源）
    # async with...as...与with...as...的用途类似，都是为了实现优雅的初始化操作与退出操作
    # 区别仅仅在于前者调用的__aenter__和__aexit__都是异步方法，而后者调用的__enter__和__exit__都是同步方法
    # 参考官方文档：异步上下文管理器
    # https://docs.python.org/zh-cn/3/reference/datamodel.html#asynchronous-context-managers
    async with tb.Client("default") as client:
        # client.get_self_info()是一个协程对象
        # 通过在它前面添加一个await语句，我们可以以一种非阻塞的方式等待它执行完毕
        # 该协程执行完毕时，将会返回对应贴吧账号的非敏感个人信息
        # 参考官方文档：可等待对象
        # https://docs.python.org/zh-cn/3/library/asyncio-task.html#awaitables
        user = await client.get_self_info()

    # 将获取的信息打印到日志
    tb.LOG.info(f"当前用户信息: {user!r}")


# 执行协程main()
# 参考官方文档：运行asyncio程序
# https://docs.python.org/zh-cn/3/library/asyncio-task.html#running-an-asyncio-program
asyncio.run(main())
```

如果你的`BDUSS`填写无误，你会获得类似下面这样的结果

```log
<2022-07-16 20:14:34.597> [INFO] [main] 当前用户信息: {'user_id': 957339815, 'user_name': 'kk不好玩', 'portrait': 'tb.1.8277e641.gUE2cTq4A4z5fi2EHn5k3Q'}
```
