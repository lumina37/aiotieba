# 入门教程

阅读本教程，你至少需要对Python的 **上下文管理器** `with...as...` 和 **迭代器** `for...in...` 有基本的印象，因为本文不会对这些重要的基本概念做过于深入的解释

推荐在本地新建一个`.py`文件来运行样例

## 命名约定

贴吧服务端使用以下名称表示特定的数据

### BDUSS

贴吧服务端使用BDUSS来确认用户身份

BDUSS是一串由纯ascii字符组成的，长度为192的字符串

!!! warning

    使用BDUSS可以完成**一切**不需要手机/邮箱验证码的操作，包括**发帖**/**发私信**/**获取账号上的所有历史发言**

    BDUSS的过期时间长达数年，一般只能通过退出登录或修改密码使其失效

    因此将BDUSS泄露给不受信任的人可能导致长期的账号安全风险和隐私泄露风险

在浏览器的Cookie和各种表单参数中你都能看到它的身影

搜索 你的浏览器型号+如何查看网站的Cookie 就能知道如何获取你的贴吧账号的BDUSS了

以Chrome为例，在任何一个贴吧网页下按<kbd>F12</kbd>调出开发者选项，然后你就能在下图的位置找到它

![Chrome Cookie](https://user-images.githubusercontent.com/48282276/179938990-77139ea2-2d94-4d38-8d7d-9c6a3d99b69e.png)

### user_name

用户名

user_name唯一，但可变，且可以是空值

请注意与nick_name相区分

### portrait

头像ID

每个贴吧用户都有且仅有一个portrait

portrait是一串由纯ascii字符组成的，以tb.1.作为开头的，长度为33~36的字符串（仅有一些远古时期的ip账号不符合这个规则）

譬如我的portrait就是tb.1.8277e641.gUE2cTq4A4z5fi2EHn5k3Q

你可以通过portrait获取用户头像，例如[我的头像](http://tb.himg.baidu.com/sys/portraith/item/tb.1.8277e641.gUE2cTq4A4z5fi2EHn5k3Q)

### user_id

用户ID

user_id唯一，不可变，不能为空

请注意将其与用户个人主页的tieba_uid相区分

user_id是一个uint64值（仅有一些远古时期的ip账号不符合这个规则）

user_name portrait user_id 都是满足唯一性的用户标识符，并可以通过其中任意一个的值反查其余两个

### tieba_uid

用户个人主页ID

tieba_uid唯一，不可变，但可以为空

请注意将其与用户的user_id相区分

tieba_uid是一个uint64值

可以通过tieba_uid的值反查user_name portrait user_id

### forum_id

吧ID，简称fid

每个贴吧都有且仅有一个fid

### thread_id

主题帖ID，简称tid

每个主题帖都有且仅有一个tid

### post_id

回复ID，简称pid

每个楼层、楼中楼都有且仅有一个pid

## 关于异步编程

如果你不了解Python异步编程，请先阅读[异步编程入门教程](async_start.md)

## 迈出第一步

一个非常简单的入门案例

### 样例代码

本样例将获取并打印当前账号的用户信息

```python
import asyncio

import aiotieba as tb

BDUSS = "在这里输入你账号的BDUSS"


async def main():
    async with tb.Client(BDUSS) as client:
        user = await client.get_self_info()

    print(user)


asyncio.run(main())
```

### 期望结果

如果你的[`BDUSS`](#bduss)填写无误，你会获得类似下面这样的结果

```log
AAAA（你的用户名）
```

## 内容的层次结构

本样例将协助你理解“主题帖-回复-楼中楼”的三级层次结构，以及如何解析富媒体内容

### 样例代码

本样例将逐级获取并打印“主题帖-回复-楼中楼”中各层级的部分内容

```python
import asyncio

import aiotieba as tb


async def main():
    async with tb.Client() as client:
        threads = await client.get_threads("天堂鸡汤")
        for thread in threads[3:6]:
            print(thread)  # 打印整个主题帖
            print(thread.contents)  # 打印主题帖中的内容碎片（含富媒体信息）
            print(thread.contents.emojis)  # 仅打印表情相关的内容碎片

        selected_thread = threads[4]
        posts = await client.get_posts(selected_thread.tid)
        for post in posts[3:6]:
            print(post)  # 打印整个回复
            print(post.contents)  # 打印回复中的内容碎片
            print(post.contents.imgs)  # 仅打印图片相关的内容碎片

        for post in posts:
            if post.reply_num == 0:
                continue
            comments = await client.get_comments(post.tid, post.pid)
            for comment in comments:
                print(comment)  # 打印整个楼中楼
                print(comment.contents.ats)  # 仅打印@相关的内容碎片
                break


asyncio.run(main())
```

## 运行时更改BDUSS

该案例演示了如何在运行时更改BDUSS

建议为每个账号新建`Client`，以避免误用遗留的websocket连接

同样地，你也可以直接向`Client.account`赋值以动态变更用户参数

### 样例代码

本样例将获取并打印当前账号的用户信息

```python
import asyncio

import aiotieba as tb


async def main():
    async with tb.Client() as client:
        client.account.BDUSS = "在这里输入你账号的BDUSS"
        user = await client.get_self_info()

    print(user)


asyncio.run(main())
```

### 期望结果

如果你的[`BDUSS`](#bduss)填写无误，你会获得类似下面这样的结果

```log
AAAA（你的用户名）
```

## 多账号

如何同时使用多个账号？

### 样例代码

本样例将获取并打印多个账号的用户信息

```python
import asyncio

import aiotieba as tb

BDUSS1 = "在这里输入第一个账号的BDUSS"
BDUSS2 = "在这里输入第二个账号的BDUSS"


async def main():
    async with tb.Client(BDUSS1) as client1, tb.Client(BDUSS2) as client2:
        user1 = await client1.get_self_info()
        user2 = await client2.get_self_info()
        print(f"账号1: {user1}, 账号2: {user2}")


asyncio.run(main())
```

### 期望结果

如果你的[`BDUSS`](#bduss)填写无误，你会获得类似下面这样的结果

```log
账号1: AAAA, 账号2: BBBB
```

## Account的序列化与反序列化

该功能可以用于导出账号参数

### 样例代码

本样例将演示账号参数的导出与导入，并使用导入生成的Account获取用户信息

```python
import asyncio

import aiotieba as tb

BDUSS = "在这里输入你账号的BDUSS"


async def main():
    account1 = tb.Account(BDUSS)
    dic = account1.to_dict()
    print(dic)
    account2 = tb.Account.from_dict(dic)
    assert account1.BDUSS == account2.BDUSS

    async with tb.Client(account=account2) as client:
        user = await client.get_self_info()

    print(user)


asyncio.run(main())
```

### 期望结果

如果你的[`BDUSS`](#bduss)填写无误，你会获得类似下面这样的结果

```log
{'BDUSS': '...'}
AAAA（你的用户名）
```

## 简单并发爬虫

### 样例代码

本样例将同时请求用户个人信息和天堂鸡汤吧首页前30帖，并将他们打印出来

```python
import asyncio

import aiotieba as tb

BDUSS = "在这里输入你账号的BDUSS"


async def main():
    async with tb.Client(BDUSS) as client:
        # [1] 什么是`asyncio.gather`？
        # 参考官方文档：并发运行任务
        # https://docs.python.org/zh-cn/3/library/asyncio-task.html#running-tasks-concurrently
        user, threads = await asyncio.gather(client.get_self_info(), client.get_threads("天堂鸡汤"))

    # 将获取的信息打印到日志
    print(f"当前用户: {user}")
    for thread in threads:
        # Threads支持迭代，因此可以使用for循环逐条打印主题帖信息
        # 当然了，Threads也支持使用下标的随机访问
        print(f"tid: {thread.tid} 最后回复时间戳: {thread.last_time} 标题: {thread.title}")


# 使用asyncio.run执行协程main
asyncio.run(main())
```

### 样例解析

#### 什么是`asyncio.gather`？

你可以将若干协程作为参数传入`asyncio.gather`，样例中传入了两个协程。如果你忘记了协程和异步函数之间的区别，请及时复习。

`asyncio.gather`会为每个传入的协程创建对应的任务来同时执行它们（并发），同时`asyncio.gather(...)`自身也是一个协程，在前面添加`await`以要求主协程`main()`等待其执行完毕。执行完毕后，返回数据的顺序与传入协程的顺序一致，即`user`对应`client.get_self_info()`，`threads`对应`client.get_threads(...)`

### 期望结果

运行效果如下所示

```log
当前用户: Starry_OvO
tid: 7595618217 最后回复时间戳: 1672461980 标题: 关于负能量帖子的最新规定
tid: 8204562074 最后回复时间戳: 1672502281 标题: 外卖超时退单，心理煎熬
tid: 8165883863 最后回复时间戳: 1672502270 标题: 【记录】我这半醉半醒的人生啊
tid: 8204618726 最后回复时间戳: 1672502254 标题: 记录一下编导生的日常
tid: 8202743003 最后回复时间戳: 1672502252 标题: 2023会更好吗？或者，又是一年的碌碌无为
tid: 8204456677 最后回复时间戳: 1672502301 标题: 2023新年倒计时开始，有人的话请回复
tid: 8203409990 最后回复时间戳: 1672502197 标题: 年尾了，谢谢你们
tid: 8203959170 最后回复时间戳: 1672502156 标题: 求祝福
tid: 8188549079 最后回复时间戳: 1672502122 标题: pollen's club
tid: 8204240728 最后回复时间戳: 1672502091 标题: 这是孩子最贵重的东西
tid: 8200916354 最后回复时间戳: 1672502023 标题: 这个是真的吗
tid: 8204206290 最后回复时间戳: 1672501931 标题: 家里突然多了只狗，请大家取个名字
tid: 8204353842 最后回复时间戳: 1672501936 标题: 一个很好的外卖小哥
tid: 8204583367 最后回复时间戳: 1672501911 标题: 何等奇迹！坚韧灵魂！
tid: 8204431580 最后回复时间戳: 1672501835 标题: 大家今年想怎么跨年呢？
tid: 8204442527 最后回复时间戳: 1672501832 标题: 吧友们，快过年了能不能发一些温馨可爱的图
tid: 8202573308 最后回复时间戳: 1672501923 标题:
tid: 8202504004 最后回复时间戳: 1672501740 标题: 吧友们，想听到那4个字
tid: 8203284120 最后回复时间戳: 1672501971 标题: 看到评论区 觉得很暖心 想给吧友分享分享
tid: 8203290932 最后回复时间戳: 1672502300 标题:
tid: 8202592714 最后回复时间戳: 1672501686 标题: 不要走啊狗狗
tid: 8165292224 最后回复时间戳: 1672501498 标题: 你想要只肥啾吗？
tid: 8202351346 最后回复时间戳: 1672501588 标题: 这就是缘分吗？
tid: 8204609134 最后回复时间戳: 1672501304 标题:
tid: 8204575619 最后回复时间戳: 1672501526 标题: 标题五个字
tid: 8199583210 最后回复时间戳: 1672501343 标题: 一些有趣的图图
tid: 8204401395 最后回复时间戳: 1672494092 标题: 兄弟们  初来乍到
tid: 8200191186 最后回复时间戳: 1672500928 标题: 我妈做了一件好事
tid: 8204273523 最后回复时间戳: 1672500829 标题: 你如初待我模样
```

## 任务队列实现多协程爬虫

### 样例代码

本样例将通过任务队列实现一个多协程爬虫，快速爬取天堂鸡汤吧的前32页共960条主题帖，并打印其中浏览量最高的10条

```python
from __future__ import annotations

import asyncio
import time

import aiotieba as tb
from aiotieba.logging import get_logger as LOG

BDUSS = "在这里输入你账号的BDUSS"


async def crawler(fname: str):
    """
    获取贴吧名为fname的贴吧的前32页中浏览量最高的10个主题帖

    Args:
        fname (str): 贴吧名
    """

    start_time = time.perf_counter()
    LOG().info("Spider start")

    # thread_list用来保存主题帖列表
    thread_list: list[tb.typing.Thread] = []

    # 使用键名"default"对应的BDUSS创建客户端
    async with tb.Client(BDUSS) as client:
        # asyncio.Queue是一个任务队列
        # maxsize=8意味着缓冲区长度为8
        # 当缓冲区被填满时，调用Queue.put的协程会被阻塞
        task_queue = asyncio.Queue(maxsize=8)
        # 当is_running被设为False后，消费者会在超时后退出
        is_running = True

        async def producer():
            """
            生产者协程
            """

            for pn in range(32, 0, -1):
                # 生产者使用Queue.put不断地将页码pn填入任务队列task_queue
                await task_queue.put(pn)
            # 这里需要nonlocal来允许对闭包外的变量的修改操作（类似于引用传递和值传递的区别）
            nonlocal is_running
            # 将is_running设置为False以允许各消费协程超时退出
            is_running = False

        async def worker(i: int):
            """
            消费者协程

            Args:
                i (int): 协程编号
            """

            while 1:
                try:
                    # 消费者协程不断地使用Queue.get从task_queue中拉取由生产者协程提供的页码pn作为任务
                    # asyncio.wait_for会等待作为参数的协程执行完毕直到超时
                    # timeout=1即把超时时间设为1秒
                    # 如果超过1秒未获取到新的页码pn，asyncio.wait_for(...)将抛出asyncio.TimeoutError
                    pn = await asyncio.wait_for(task_queue.get(), timeout=1)
                    LOG().debug(f"Worker#{i} handling pn:{pn}")
                except asyncio.TimeoutError:
                    # 捕获asyncio.TimeoutError以退出协程
                    if is_running is False:
                        # 如果is_running为False，意味着不需要再轮询task_queue获取新任务
                        LOG().debug(f"Worker#{i} quit")
                        # 消费者协程通过return退出
                        return
                else:
                    # 执行被分派的任务，即爬取pn页的帖子列表
                    threads = await client.get_threads(fname, pn)
                    # 这里的nonlocal同样是为了修改闭包外的变量thread_list
                    nonlocal thread_list
                    thread_list += threads

        # 创建8个消费者协程
        workers = [worker(i) for i in range(8)]
        # 使用asyncio.gather并发执行
        # 需要注意这里*workers中的*意为将列表展开成多个参数
        # 因为asyncio.gather只接受协程作为参数，不接受协程列表
        await asyncio.gather(*workers, producer())

    LOG().info(f"Spider complete. Time cost: {time.perf_counter() - start_time:.4f} secs")

    # 按主题帖浏览量降序排序
    thread_list.sort(key=lambda thread: thread.view_num, reverse=True)
    # 将浏览量最高的10个主题帖的信息打印到日志
    for i, thread in enumerate(thread_list[0:10], 1):
        LOG().info(f"Rank#{i} view_num:{thread.view_num} title:{thread.title}")


# 执行协程crawler
asyncio.run(crawler("天堂鸡汤"))
```

### 期望结果

运行效果如下图所示

```log
<2023-01-01 00:03:01.195> [INFO] [crawler] Spider start
<2023-01-01 00:03:01.198> [DEBUG] [worker] Worker#0 handling pn:32
<2023-01-01 00:03:01.242> [DEBUG] [worker] Worker#1 handling pn:31
<2023-01-01 00:03:01.245> [DEBUG] [worker] Worker#2 handling pn:30
<2023-01-01 00:03:01.245> [DEBUG] [worker] Worker#3 handling pn:29
<2023-01-01 00:03:01.246> [DEBUG] [worker] Worker#4 handling pn:28
<2023-01-01 00:03:01.247> [DEBUG] [worker] Worker#5 handling pn:27
<2023-01-01 00:03:01.248> [DEBUG] [worker] Worker#6 handling pn:26
<2023-01-01 00:03:01.248> [DEBUG] [worker] Worker#7 handling pn:25
<2023-01-01 00:03:01.599> [DEBUG] [worker] Worker#7 handling pn:24
<2023-01-01 00:03:01.626> [DEBUG] [worker] Worker#4 handling pn:23
<2023-01-01 00:03:01.685> [DEBUG] [worker] Worker#2 handling pn:22
<2023-01-01 00:03:01.711> [DEBUG] [worker] Worker#5 handling pn:21
<2023-01-01 00:03:01.744> [DEBUG] [worker] Worker#3 handling pn:20
<2023-01-01 00:03:01.768> [DEBUG] [worker] Worker#0 handling pn:19
<2023-01-01 00:03:01.776> [DEBUG] [worker] Worker#1 handling pn:18
<2023-01-01 00:03:01.777> [DEBUG] [worker] Worker#6 handling pn:17
<2023-01-01 00:03:01.974> [DEBUG] [worker] Worker#5 handling pn:16
<2023-01-01 00:03:02.041> [DEBUG] [worker] Worker#7 handling pn:15
<2023-01-01 00:03:02.043> [DEBUG] [worker] Worker#4 handling pn:14
<2023-01-01 00:03:02.072> [DEBUG] [worker] Worker#6 handling pn:13
<2023-01-01 00:03:02.083> [DEBUG] [worker] Worker#2 handling pn:12
<2023-01-01 00:03:02.145> [DEBUG] [worker] Worker#3 handling pn:11
<2023-01-01 00:03:02.190> [DEBUG] [worker] Worker#0 handling pn:10
<2023-01-01 00:03:02.197> [DEBUG] [worker] Worker#1 handling pn:9
<2023-01-01 00:03:02.365> [DEBUG] [worker] Worker#7 handling pn:8
<2023-01-01 00:03:02.379> [DEBUG] [worker] Worker#2 handling pn:7
<2023-01-01 00:03:02.425> [DEBUG] [worker] Worker#5 handling pn:6
<2023-01-01 00:03:02.547> [DEBUG] [worker] Worker#6 handling pn:5
<2023-01-01 00:03:02.579> [DEBUG] [worker] Worker#4 handling pn:4
<2023-01-01 00:03:02.606> [DEBUG] [worker] Worker#3 handling pn:3
<2023-01-01 00:03:02.635> [DEBUG] [worker] Worker#0 handling pn:2
<2023-01-01 00:03:02.640> [DEBUG] [worker] Worker#1 handling pn:1
<2023-01-01 00:03:03.789> [DEBUG] [worker] Worker#5 quit
<2023-01-01 00:03:03.820> [DEBUG] [worker] Worker#7 quit
<2023-01-01 00:03:03.821> [DEBUG] [worker] Worker#2 quit
<2023-01-01 00:03:03.821> [DEBUG] [worker] Worker#6 quit
<2023-01-01 00:03:03.882> [DEBUG] [worker] Worker#4 quit
<2023-01-01 00:03:03.975> [DEBUG] [worker] Worker#0 quit
<2023-01-01 00:03:03.975> [DEBUG] [worker] Worker#1 quit
<2023-01-01 00:03:03.976> [INFO] [crawler] Spider complete. Time cost: 2.7822 secs
<2023-01-01 00:03:03.977> [INFO] [crawler] Rank#1 view_num:295571 title:各位发点暖心小故事吧我先来
<2023-01-01 00:03:03.978> [INFO] [crawler] Rank#2 view_num:285897 title:解决压力大
<2023-01-01 00:03:03.978> [INFO] [crawler] Rank#3 view_num:255771 title:人活着是为了什么
<2023-01-01 00:03:03.978> [INFO] [crawler] Rank#4 view_num:243325 title:面藕，我的面藕😭
<2023-01-01 00:03:03.979> [INFO] [crawler] Rank#5 view_num:222611 title:什么事情是你长大很久之后才明白的？
<2023-01-01 00:03:03.979> [INFO] [crawler] Rank#6 view_num:216527 title:教你谈恋爱
<2023-01-01 00:03:03.979> [INFO] [crawler] Rank#7 view_num:214848 title:你已经是只狗了！
<2023-01-01 00:03:03.980> [INFO] [crawler] Rank#8 view_num:208130 title:好温暖呀~
<2023-01-01 00:03:03.980> [INFO] [crawler] Rank#9 view_num:206946 title:好温柔的叔叔啊😭
<2023-01-01 00:03:03.980> [INFO] [crawler] Rank#10 view_num:203606 title:你会不会删掉已故亲人的联系方式？
```
