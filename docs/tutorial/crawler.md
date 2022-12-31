# 爬虫教程

***请认真阅读代码注释***

## 入门案例

*本案例将演示 如何实现一个简单并发爬虫*

复制下列代码并运行

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
        user, threads = await asyncio.gather(client.get_self_info(), client.get_threads('天堂鸡汤'))

    # 将获取的信息打印到日志
    tb.LOG.info(f"当前用户信息: {user!r}")
    for thread in threads:
        # threads支持迭代，因此可以使用for循环逐条打印主题帖信息
        tb.LOG.info(f"tid: {thread.tid} 最后回复时间戳: {thread.last_time} 标题: {thread.title}")


# 使用asyncio.run执行协程main
asyncio.run(main())
```

运行效果如下所示

```log
<2022-12-31 23:58:23.779> [INFO] [main] 当前用户信息: {'user_id': 957339815, 'user_name': 'Starry_OvO', 'portrait': 'tb.1.8277e641.gUE2cTq4A4z5fi2EHn5k3Q', 'nick_name': 'ºStarry'}
<2022-12-31 23:58:23.781> [INFO] [main] tid: 7595618217 最后回复时间戳: 1672461980 标题: 关于负能量帖子的最新规定
<2022-12-31 23:58:23.781> [INFO] [main] tid: 8204562074 最后回复时间戳: 1672502281 标题: 外卖超时退单，心理煎熬
<2022-12-31 23:58:23.781> [INFO] [main] tid: 8165883863 最后回复时间戳: 1672502270 标题: 【记录】我这半醉半醒的人生啊
<2022-12-31 23:58:23.782> [INFO] [main] tid: 8204618726 最后回复时间戳: 1672502254 标题: 记录一下编导生的日常
<2022-12-31 23:58:23.782> [INFO] [main] tid: 8202743003 最后回复时间戳: 1672502252 标题: 2023会更好吗？或者，又是一年的碌碌无为
<2022-12-31 23:58:23.783> [INFO] [main] tid: 8204456677 最后回复时间戳: 1672502301 标题: 2023新年倒计时开始，有人的话请回复
<2022-12-31 23:58:23.783> [INFO] [main] tid: 8203409990 最后回复时间戳: 1672502197 标题: 年尾了，谢谢你们
<2022-12-31 23:58:23.783> [INFO] [main] tid: 8203959170 最后回复时间戳: 1672502156 标题: 求祝福
<2022-12-31 23:58:23.784> [INFO] [main] tid: 8188549079 最后回复时间戳: 1672502122 标题: pollen's club
<2022-12-31 23:58:23.784> [INFO] [main] tid: 8204240728 最后回复时间戳: 1672502091 标题: 这是孩子最贵重的东西
<2022-12-31 23:58:23.784> [INFO] [main] tid: 8200916354 最后回复时间戳: 1672502023 标题: 这个是真的吗
<2022-12-31 23:58:23.785> [INFO] [main] tid: 8204206290 最后回复时间戳: 1672501931 标题: 家里突然多了只狗，请大家取个名字
<2022-12-31 23:58:23.785> [INFO] [main] tid: 8204353842 最后回复时间戳: 1672501936 标题: 一个很好的外卖小哥
<2022-12-31 23:58:23.785> [INFO] [main] tid: 8204583367 最后回复时间戳: 1672501911 标题: 何等奇迹！坚韧灵魂！
<2022-12-31 23:58:23.786> [INFO] [main] tid: 8204431580 最后回复时间戳: 1672501835 标题: 大家今年想怎么跨年呢？
<2022-12-31 23:58:23.786> [INFO] [main] tid: 8204442527 最后回复时间戳: 1672501832 标题: 吧友们，快过年了能不能发一些温馨可爱的图
<2022-12-31 23:58:23.786> [INFO] [main] tid: 8202573308 最后回复时间戳: 1672501923 标题:
<2022-12-31 23:58:23.786> [INFO] [main] tid: 8202504004 最后回复时间戳: 1672501740 标题: 吧友们，想听到那4个字
<2022-12-31 23:58:23.787> [INFO] [main] tid: 8203284120 最后回复时间戳: 1672501971 标题: 看到评论区 觉得很暖心 想给吧友分享分享
<2022-12-31 23:58:23.787> [INFO] [main] tid: 8203290932 最后回复时间戳: 1672502300 标题:
<2022-12-31 23:58:23.787> [INFO] [main] tid: 8202592714 最后回复时间戳: 1672501686 标题: 不要走啊狗狗
<2022-12-31 23:58:23.788> [INFO] [main] tid: 8165292224 最后回复时间戳: 1672501498 标题: 你想要只肥啾吗？
<2022-12-31 23:58:23.788> [INFO] [main] tid: 8202351346 最后回复时间戳: 1672501588 标题: 这就是缘分吗？
<2022-12-31 23:58:23.788> [INFO] [main] tid: 8204609134 最后回复时间戳: 1672501304 标题:
<2022-12-31 23:58:23.789> [INFO] [main] tid: 8204575619 最后回复时间戳: 1672501526 标题: 标题五个字
<2022-12-31 23:58:23.789> [INFO] [main] tid: 8199583210 最后回复时间戳: 1672501343 标题: 一些有趣的图图
<2022-12-31 23:58:23.789> [INFO] [main] tid: 8204401395 最后回复时间戳: 1672494092 标题: 兄弟们  初来乍到
<2022-12-31 23:58:23.789> [INFO] [main] tid: 8200191186 最后回复时间戳: 1672500928 标题: 我妈做了一件好事
<2022-12-31 23:58:23.790> [INFO] [main] tid: 8204273523 最后回复时间戳: 1672500829 标题: 你如初待我模样
```

## 进阶案例

*本案例将演示 如何通过任务队列实现一个多协程爬虫*

复制下列代码并运行

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

## 结语

在同步IO下，脚本的效率瓶颈大多来自于等待响应的耗时

而在异步IO下，脚本的效率瓶颈大多来自于服务端的 rps (Request per Second) 限制

使用异步IO替代同步IO，相当于用更高的调度成本换取更高的并行度，进而提高脚本效率
