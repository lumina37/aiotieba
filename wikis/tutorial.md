# aiotieba库使用教程

## 准备知识

想要用好`aiotieba`库，必须初步掌握`Python`异步编程

如果你不熟悉`Python`异步编程，建议阅读下列教程：

+ [轻松理解Python中的async/await](https://blog.csdn.net/Likianta/article/details/90123678) 非常易于理解的入门案例
+ [Python官方文档 协程与任务](https://docs.python.org/zh-cn/3/library/asyncio-task.html) 包含详尽Reference和配套案例的官方文档，更适合有一定基础的初学者
+ [Python Async/Await入门指南](https://zhuanlan.zhihu.com/p/27258289) 已经是17年的文章了，从生成器`yield`的角度出发介绍`Python`异步，对初学者不太友好，更适合拔高阅读
+ [深入理解JavaScript中的async/await](https://www.cnblogs.com/youma/p/10475214.html) `JavaScript`中的`Promise`与`Python`中的`Future`概念很相似，该教程可以帮助你快速地从`Promise`异步模式出发理解`async-await`异步模式

如果你已经对异步编程的相关知识非常熟悉，那么我建议你按`4-1-2-3`的顺序阅读

如果你只是编程初学者或者对各种异步模式一窍不通，那么我建议你按`1-2-3`的顺序阅读

当然即便你没有阅读上面的教程，我也会针对异步编程的初学者为每一行异步代码撰写详细的注释

## 案例1 配置BDUSS

本例中，你将学会`config.toml`配置文件的基本填写方法，并使用`aiotieba`库获取贴吧账号的非敏感个人信息

### 步骤1

在`aiotieba`文件夹的旁边新建一个`debug.py`文件。当然你也可以在任何一个可以引用到`aiotieba`库的地方新建脚本，又或是另起一个你喜欢的脚本名

将下列代码复制到`debug.py`并运行

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
    tb.LOG.info(f"当前用户信息: {user}")


# 执行协程main()
# 参考官方文档：运行asyncio程序
# https://docs.python.org/zh-cn/3/library/asyncio-task.html#running-an-asyncio-program
asyncio.run(main())
```

然后，你会获得如下结果

```log
<2022-07-07 09:44:31> [WARNING] Failed to login. reason:用户名或密码错误
<2022-07-07 09:44:31> [INFO] 当前用户信息: {'user_id': 0, 'user_name': '', 'portrait': ''}
```

### 步骤2

此时在`debug.py`的同级目录下会生成一个`config`文件夹，点开里面自动生成的`config.toml`文件，将你的`BDUSS`填入正确的位置

`BDUSS`的提取方式请自行搜索[浏览器如何获取BDUSS](https://cn.bing.com/search?q=%E6%B5%8F%E8%A7%88%E5%99%A8%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96BDUSS)

填写完毕的`config.toml`大概长这样

```toml
[User]

[User.default]
BDUSS = "2dNNk1wMXVSZmw2MnpkWDNqMnM4MmFaeFZYNVVPUEhPS0thNFZzUERjME52V1KpSVFBQUFBJCQAAAAAAQAAAAEAAAA0lUwndl9ndWFyZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0wPmINMD5iY" # 把你的那一串长长的BDUSS放在这
```

### 步骤3

再次运行`debug.py`，如果你的`BDUSS`填写无误，你就能得到类似这样的用户个人信息

```log
<2022-07-07 09:45:22> [INFO] 当前用户信息: {'user_id': 957339815, 'user_name': 'kk不好玩', 'portrait': 'tb.1.8277e641.gUE2cTq4A4z5fi2EHn5k3Q'}
```

## 案例2 简单并发爬虫

将下列代码复制到`debug.py`并运行

```python
import asyncio

import aiotieba as tb


async def main():
    # 使用键名"default"对应的BDUSS创建客户端
    async with tb.Client("default") as client:
        # 下面这行语句会同时请求用户个人信息和图拉丁吧首页前30帖
        # 你可以将若干协程作为参数传入asyncio.gather，这里传入的参数为client.get_self_info()和client.get_threads('图拉丁')
        # asyncio.gather会为每个传入的协程创建对应的任务来同时执行它们（并发）
        # 同时asyncio.gather(...)也会返回一个协程，在前面添加await等待其执行完毕
        # 执行完毕后，返回数据的顺序与传入参数的顺序一致，即user对应client.get_self_info()，threads对应client.get_threads('图拉丁')
        # 参考官方文档：并发运行任务
        # https://docs.python.org/zh-cn/3/library/asyncio-task.html#running-tasks-concurrently
        user, threads = await asyncio.gather(client.get_self_info(), client.get_threads('图拉丁'))

    # 将获取的信息打印到日志
    tb.LOG.info(f"当前用户信息: {user}")
    for thread in threads:
        # threads支持迭代，因此可以使用for循环逐条打印主题帖信息
        tb.LOG.info(f"tid: {thread.tid} 最后回复时间戳: {thread.last_time} 标题: {thread.title}")


# 使用asyncio.run执行协程main
asyncio.run(main())
```

运行效果如下所示

```log
<2022-07-07 09:45:42> [INFO] 当前用户信息: {'user_id': 957339815, 'user_name': 'kk不好玩', 'portrait': 'tb.1.8277e641.gUE2cTq4A4z5fi2EHn5k3Q'}
<2022-07-07 09:45:42> [INFO] tid: 2949701560 最后回复时间戳: 1656889189 标题: 【重要更新】百度图拉丁吧吧规 20140329
<2022-07-07 09:45:42> [INFO] tid: 7911527420 最后回复时间戳: 1657158340 标题: 今天再说说12代的优点，说完了缺点后
<2022-07-07 09:45:42> [INFO] tid: 7910840295 最后回复时间戳: 1657158332 标题: 如何评价？
<2022-07-07 09:45:42> [INFO] tid: 7910097451 最后回复时间戳: 1657158331 标题: 这个东西到底在哪里？
<2022-07-07 09:45:42> [INFO] tid: 7910487139 最后回复时间戳: 1657158332 标题: 现在小作坊固态行业都这么卷了吗……
<2022-07-07 09:45:42> [INFO] tid: 7907834173 最后回复时间戳: 1657158331 标题: 听说这个吧大神比较多，求帮忙
<2022-07-07 09:45:42> [INFO] tid: 7910901069 最后回复时间戳: 1657158328 标题: 真正的风冷暴力测试，直接上气炉！
<2022-07-07 09:45:42> [INFO] tid: 7910574837 最后回复时间戳: 1657158327 标题: PDD是真NB
<2022-07-07 09:45:42> [INFO] tid: 7910037909 最后回复时间戳: 1657158321 标题: 这几个主板有人要吗？免费送了
<2022-07-07 09:45:42> [INFO] tid: 7907730590 最后回复时间戳: 1657158321 标题: 装机小白请牛爷爷们帮忙看下配置单
<2022-07-07 09:45:42> [INFO] tid: 7911532293 最后回复时间戳: 1657158312 标题: 为啥投诉不了捏？
<2022-07-07 09:45:42> [INFO] tid: 7911448545 最后回复时间戳: 1657149836 标题: 有没有大佬知道这什么情况，开机挺长时间显示器才有画面，然后直接跳过了系统欢迎界面进入桌面了。，显示器是144hz，DP显卡是rx6600
<2022-07-07 09:45:42> [INFO] tid: 7911094891 最后回复时间戳: 1657158301 标题: npc显示器如何有大佬知道的吗
<2022-07-07 09:45:42> [INFO] tid: 7911504740 最后回复时间戳: 1657158289 标题: 大神快来给小白支招，水一水也好
<2022-07-07 09:45:42> [INFO] tid: 7908724714 最后回复时间戳: 1657158287 标题: 老铁们来看看，钱是不是花在了刀把上？
<2022-07-07 09:45:42> [INFO] tid: 6745079417 最后回复时间戳: 1657158286 标题:
<2022-07-07 09:45:42> [INFO] tid: 7911226971 最后回复时间戳: 1657157487 标题: 到我了到我了
<2022-07-07 09:45:42> [INFO] tid: 7908370452 最后回复时间戳: 1657158277 标题: 我是不是买贵了
<2022-07-07 09:45:42> [INFO] tid: 7911562434 最后回复时间戳: 1657158275 标题: 老家伙们快进来
<2022-07-07 09:45:42> [INFO] tid: 7903290923 最后回复时间戳: 1657103009 标题: 《梦幻西游》新出了一件装备卖了1180万
<2022-07-07 09:45:42> [INFO] tid: 7911257482 最后回复时间戳: 1657158271 标题: 来！估个价吧
<2022-07-07 09:45:42> [INFO] tid: 7911519914 最后回复时间戳: 1657158263 标题: 萌新不懂就问
<2022-07-07 09:45:42> [INFO] tid: 7911420437 最后回复时间戳: 1657158262 标题: 1800拿下i5 12490F套装他不香么
<2022-07-07 09:45:42> [INFO] tid: 7910620273 最后回复时间戳: 1657158260 标题: 人傻钱多的表弟配的电脑
<2022-07-07 09:45:42> [INFO] tid: 7911492735 最后回复时间戳: 1657158256 标题: 感谢图吧各路大佬的指导，小弟昨晚已完成下单，现来汇报作业
<2022-07-07 09:45:42> [INFO] tid: 7911187553 最后回复时间戳: 1657158254 标题: 开机键盘鼠标都不亮显卡风扇不转是为什么
<2022-07-07 09:45:42> [INFO] tid: 7911282738 最后回复时间戳: 1657158252 标题: 3050显卡，84度！！
<2022-07-07 09:45:42> [INFO] tid: 7911535524 最后回复时间戳: 1657158252 标题: 台式电脑开不开机
<2022-07-07 09:45:42> [INFO] tid: 7908618366 最后回复时间戳: 1657158249 标题: 遇到一个很糟心的事情，各位大佬来帮我看一下
<2022-07-07 09:45:42> [INFO] tid: 7911568034 最后回复时间戳: 1657158246 标题: 出个未拆封的12400f
```

## 案例3 多协程爬虫

将下列代码复制到`debug.py`并运行

```python
import asyncio
import time
from typing import List

import aiotieba as tb


async def crawler(fname: str):
    """
    获取贴吧名为fname的贴吧的前32页中浏览量最高的10个主题帖

    Args:
        fname (str): 贴吧名
    """

    start_time = time.perf_counter()
    tb.LOG.info("Spider start")

    # thread_list用来保存主题帖列表
    thread_list: List[tb.Thread] = []

    # 使用键名"default"对应的BDUSS创建客户端
    async with tb.Client("default") as client:

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
                    # asyncio.wait_for用于等待一个协程执行完毕直到超时
                    # timeout=1即把超时时间设为1秒
                    # 如果超过1秒未获取到新的页码pn，asyncio.wait_for将抛出asyncio.TimeoutError
                    pn = await asyncio.wait_for(task_queue.get(), timeout=1)
                    tb.LOG.debug(f"Worker#{i} handling pn:{pn}")
                except asyncio.TimeoutError:
                    # 捕获asyncio.TimeoutError以退出协程
                    if is_running is False:
                        # 如果is_running为False，意味着不需要再轮询task_queue获取新任务
                        tb.LOG.debug(f"Worker#{i} quit")
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

    tb.LOG.info(f"Spider complete. Time cost: {time.perf_counter()-start_time:.4f} secs")

    # 按主题帖浏览量降序排序
    thread_list.sort(key=lambda thread: thread.view_num, reverse=True)
    # 将浏览量最高的10个主题帖的信息打印到日志
    for i, thread in enumerate(thread_list[0:10], 1):
        tb.LOG.info(f"Rank#{i} view_num:{thread.view_num} title:{thread.title}")


# 执行协程crawler
asyncio.run(crawler("图拉丁"))
```

运行效果如下图所示

```log
<2022-07-07 09:46:11> [INFO] Spider start
<2022-07-07 09:46:11> [DEBUG] Worker#0 handling pn:32
<2022-07-07 09:46:11> [DEBUG] Worker#1 handling pn:31
<2022-07-07 09:46:11> [DEBUG] Worker#2 handling pn:30
<2022-07-07 09:46:11> [DEBUG] Worker#3 handling pn:29
<2022-07-07 09:46:11> [DEBUG] Worker#4 handling pn:28
<2022-07-07 09:46:11> [DEBUG] Worker#5 handling pn:27
<2022-07-07 09:46:11> [DEBUG] Worker#6 handling pn:26
<2022-07-07 09:46:11> [DEBUG] Worker#7 handling pn:25
<2022-07-07 09:46:12> [DEBUG] Worker#5 handling pn:24
<2022-07-07 09:46:12> [DEBUG] Worker#7 handling pn:23
<2022-07-07 09:46:12> [DEBUG] Worker#0 handling pn:22
<2022-07-07 09:46:12> [DEBUG] Worker#6 handling pn:21
<2022-07-07 09:46:12> [DEBUG] Worker#1 handling pn:20
<2022-07-07 09:46:12> [DEBUG] Worker#4 handling pn:19
<2022-07-07 09:46:12> [DEBUG] Worker#3 handling pn:18
<2022-07-07 09:46:12> [DEBUG] Worker#2 handling pn:17
<2022-07-07 09:46:12> [DEBUG] Worker#5 handling pn:16
<2022-07-07 09:46:13> [DEBUG] Worker#7 handling pn:15
<2022-07-07 09:46:13> [DEBUG] Worker#6 handling pn:14
<2022-07-07 09:46:13> [DEBUG] Worker#0 handling pn:13
<2022-07-07 09:46:13> [DEBUG] Worker#1 handling pn:12
<2022-07-07 09:46:13> [DEBUG] Worker#2 handling pn:11
<2022-07-07 09:46:13> [DEBUG] Worker#5 handling pn:10
<2022-07-07 09:46:13> [DEBUG] Worker#6 handling pn:9
<2022-07-07 09:46:13> [DEBUG] Worker#7 handling pn:8
<2022-07-07 09:46:13> [DEBUG] Worker#4 handling pn:7
<2022-07-07 09:46:13> [DEBUG] Worker#3 handling pn:6
<2022-07-07 09:46:13> [DEBUG] Worker#1 handling pn:5
<2022-07-07 09:46:13> [DEBUG] Worker#0 handling pn:4
<2022-07-07 09:46:13> [DEBUG] Worker#2 handling pn:3
<2022-07-07 09:46:13> [DEBUG] Worker#7 handling pn:2
<2022-07-07 09:46:14> [DEBUG] Worker#6 handling pn:1
<2022-07-07 09:46:15> [DEBUG] Worker#4 quit
<2022-07-07 09:46:15> [DEBUG] Worker#3 quit
<2022-07-07 09:46:15> [DEBUG] Worker#1 quit
<2022-07-07 09:46:15> [DEBUG] Worker#2 quit
<2022-07-07 09:46:15> [DEBUG] Worker#0 quit
<2022-07-07 09:46:15> [DEBUG] Worker#7 quit
<2022-07-07 09:46:15> [DEBUG] Worker#6 quit
<2022-07-07 09:46:15> [DEBUG] Worker#5 quit
<2022-07-07 09:46:15> [INFO] Spider complete. Time cost: 3.7627 secs
<2022-07-07 09:46:15> [INFO] Rank#1 view_num:2999226 title:图拉丁吧刷经验专用贴，水请来这水！ 新版
<2022-07-07 09:46:15> [INFO] Rank#2 view_num:1671595 title:【重要更新】百度图拉丁吧吧规 20140329
<2022-07-07 09:46:15> [INFO] Rank#3 view_num:350415 title:【圾佬乐园】图吧垃圾回收站(2021年冬季)
<2022-07-07 09:46:15> [INFO] Rank#4 view_num:256031 title:真的有这么贫穷的人吗
<2022-07-07 09:46:15> [INFO] Rank#5 view_num:161073 title:XDM我人嘛了
<2022-07-07 09:46:15> [INFO] Rank#6 view_num:154823 title:第一次当垃圾佬，激动，分享 一下
<2022-07-07 09:46:15> [INFO] Rank#7 view_num:127481 title:现在的矿工这么实在了吗？
<2022-07-07 09:46:15> [INFO] Rank#8 view_num:107671 title:没想到显卡方便出同城居然发生了这样的…
<2022-07-07 09:46:15> [INFO] Rank#9 view_num:84939 title:还望先生救我，无线网卡往哪装哇大佬们
<2022-07-07 09:46:15> [INFO] Rank#10 view_num:83830 title:无聊打开电脑看了一眼配置
```

## 结语

使用异步请求相当于用更高的调度成本换取更低的时间成本，以克服客户端在同步IO上的速度瓶颈

想进一步了解如何使用`aiotieba`优雅地实现一些实用功能，请阅读[实用工具合集](many_utils.md)
