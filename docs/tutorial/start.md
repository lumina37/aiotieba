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

以Chorme为例，在任何一个贴吧网页下按<kbd>F12</kbd>调出开发者选项，然后你就能在下图的位置找到它

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

user_id是一个int64值

user_name portrait user_id 都是满足唯一性的用户标识符，并可以通过其中任意一个的值反查其余两个

### tieba_uid

用户个人主页ID

tieba_uid唯一，不可变，但可以为空

请注意将其与用户的user_id相区分

tieba_uid是一个uint64值（仅有一些远古时期的ip账号不符合这个规则）

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

## 获取主题帖

### 样例代码

本样例将获取并打印吧主题帖列表

```python
import asyncio

import aiotieba as tb


# [2] 异步函数——`async`关键字
async def main():
    # [6] `async with`是什么？
    async with tb.Client() as client:
        # [1] CPU在何时离开？——`await`关键字
        threads = await client.get_threads('天堂鸡汤')

    print(threads)


# [4] CPU在何时返回？——事件循环
# 官方文档：运行asyncio程序
# https://docs.python.org/zh-cn/3/library/asyncio-task.html#running-an-asyncio-program
asyncio.run(main())
```

### 样例解析

#### 什么是异步

在计算机中，CPU的速度普遍要比网络IO的速度快几个数量级。为了不让网络IO成为系统性能的瓶颈，我们会希望CPU等高速设备不要原地等待网卡慢悠悠地传输数据，而是可以把IO缓冲区交给网卡就暂时离开，去执行一些其他任务，这其中就体现了**异步**（Asynchronous）的思想。

*Asynchronous*的前缀*a-*意为*not*，*syn*意为*together*，*chrono*源自古希腊语*khronos*，意为*time*，*-ous*为形容词后缀，合起来就是*not-together-time*，不同时发生的。在计算机领域，*Asynchronous*常常用于形容“多个事件不在同一时间发生”。这里的“同一时间”所强调的并不是时间长短，而是**逻辑上的连贯性**。“时间”可以不是一个一维的时间节点，它甚至可以是一段相当长，但有逻辑连贯性的时间片段。例如我们可以说：“在应用了异步技术之后，相对于CPU及其他相关的高速设备而言，网络IO的请求事件与响应事件不在同一时间发生”。在这个描述中，CPU的“操作时间”的连贯性是如何被破坏的？这是一个理解“异步”概念的关键所在。答案是在请求发出后，CPU可以暂时离开，切换到其他地方去处理另外的工作，这是一种“逻辑”切换，也正是这种切换破坏了“时间”在逻辑上的连贯性。

#### CPU在何时离开？——`await`关键字

那么Python是如何实现异步的？在抛出一大堆错综复杂的概念来回答这个问题之前，你可以先带着一个更小的子问题来阅读下面的文章——CPU在何时离开？让我们先来看样例。

在样例`threads = await client.get_threads()`中，`client.get_threads`是一个**异步函数**，你可以把它形象地理解为“施工方案”，`client.get_threads()`调用（call）了这个异步函数，形象地理解也就是“执行施工方案”。调用异步函数不会像调用同步函数那样返回结果，而是会返回一个“施工方案的执行过程”，也就是**可等待对象**（`Awaitable`）。这里初学者一定要区分好异步函数和可等待对象这两个概念。此时，在可等待对象`client.get_threads()`的左边，那个至关重要的关键字`await`出现了。*await*意为“等待”，往往用于表达“以被动的姿态等待某事的发生”，且暗含期待之意。我们回到样例来说明Python中`await`的作用，在`threads = await client.get_threads()`中，`await`要求其所处的可等待对象`main()`必须等待后面的那个可等待对象`client.get_threads()`给出执行结果`threads`后，再继续往下执行。在这个极为拗口的表述中，第二个“可等待对象”很好理解，但第一个“可等待对象`main()`”可能就会让很多人摸不着头脑了，什么叫“可等待对象等待可等待对象”？初看不理解没关系，下面这则“八股文”也许可以解答你的疑惑——在`await`关键字的指挥下做出等待行为的是谁？正确答案是`await`所在的可等待对象`main()`，而不是`await`所在的异步函数`main`，更不应该是`client.get_threads()`或者CPU，这里涉及的问题依然是异步函数`main`和可等待对象`main()`之间的差异，是“施工方案”和“施工方案的执行过程”之间的差异，施工方案可没有“等待”、“暂停”的说法，只有施工过程可以有“暂停施工”、“等待某个任务完成再继续施工”的说法。

`main()`的这种等待行为对应于一个计算机术语**“挂起”**（suspend），后面我们都会使用这个术语来替代“暂停”等口语化的词汇。*suspend*与*pause*意思相近，但他们之间有着微妙的区别——*suspend*往往表示较长时间的暂停，譬如在快节奏游戏中的暂停我们通常会说*pause*而不是*suspend*。

在这一小节的最后，我相信各位读者已经能够从具体到抽象，自行总结出`await`的含义——Python中`await`关键字的作用就是让其当前所处的可等待对象等待右侧的可等待对象执行完毕。在本节开头提出的问题也可以解答了，在利用`await`等待一个可等待对象时，如果不能立即获得结果，CPU就会离开。

#### 异步函数——`async`关键字

在Python中，`async`关键字被用于将函数标记为异步的。不论函数体内是否需要等待（`await`），添加了`async`标记的函数都会返回一个可等待对象。

#### 什么是协程

**协程**（`Coroutine`）就是可以在中途挂起和恢复执行的函数执行过程。调用异步函数`main`所得到的可等待对象`main()`就是一个协程。

#### CPU在何时返回？——事件循环

回调函数（callback function）是这样一种函数：客户需要到柜台取货，但他又不想一直在柜台干等，就把自己的电话号码（回调函数）交给柜台，让柜台在有货之后打电话（执行回调函数）通知他来取。

**事件循环**（`EventLoop`），其中*event*意为事件，*loop*意为循环，就是用来获取事件通知，调度协程执行的循环体。事件循环在每次循环中都会做以下工作：将新增的定时任务添加到优先级队列；将已到执行时间的定时任务的回调函数添加到待执行回调函数列表；从操作系统获取事件通知（比如网卡通过硬件中断通知系统：某个socket有数据到来）并将读/写缓冲区的回调函数添加到待执行列表；最后，执行所有待执行的回调函数。CPU会在“执行回调函数”这一步骤返回先前被挂起的正在等待IO事件的协程，恢复他们的执行。

`asyncio.run`将会使用一个全局事件循环（不存在则新建）来执行作为参数的协程。`asyncio.run(main())`也就是在全局事件循环中执行协程`main()`。从`main()`到`client.get_threads()`一路往下执行，最终抵达一个底层协程，它将一个用于网络通信的socket注册到操作系统内核，然后立即返回一个`Future`对象，表示一个将要到来的结果，由于我们`await`了这个`Future`，调用链上所有的协程都被挂起，直到事件循环从操作系统获取到一个匹配的可读事件后，事件循环再执行对应读缓冲区的回调函数将协程唤醒并继续执行。

#### 为什么`await`只能在异步函数中使用？

协程有多种实现方式，而Python实现的是一种沿用了生成器机制的无栈协程。沿用生成器机制，意味着协程的上下文和生成器一样，被保存在一个对象中；无栈，意味着Python协程的调用链并不是一个栈结构，而是一个酷似链表的结构，最开始被调用的协程为链表头，通过其保存的上下文一路指向最底层的协程。而与无栈协程相对的有栈协程则与线程十分类似，不论同步函数的调用还是异步函数的调用都共享一套调用栈，因此有栈协程可以像线程一样在任何位置挂起，而无栈协程只能在特定位置（如`await`关键字标记的地方）挂起。无栈协程的一大“丑陋”之处就是`await`只能在异步函数中使用，JavaScript/Rust/C++的无栈协程都是如此，这导致如果你要使用异步特性，就必须将`async def`铺满整个调用链。

现在我们来回答标题提出的问题，如果在同步函数的调用过程中使用了`await`来等待异步结果，由于调用同步函数的返回值不是协程，不会在其中保存上下文信息，这导致我们无法在同步函数中找到那个应该恢复执行的正确位置。但如果我就是要在同步函数中记录应当恢复执行的正确位置呢？很好，那么你将实现一个有栈协程，go语言正是如此。

#### `async with`是什么？

也就是一个异步版本的上下文生成器，在使用`__init__`初始化对象之后使用对象的异步方法`__aenter__`进行异步初始化工作（比如创建连接池），使用异步方法`__aexit__`进行异步清理工作（比如关闭所有连接）。

## 配置文件

如果你需要使用账号，那么你必须使用配置文件

### 准备工作

在工作目录下新建配置文件`aiotieba.toml`

参考[文档](config.md)将你的BDUSS填写如下

```toml
[User]

[User.default]
BDUSS = "..."
```

### 样例代码

本样例将获取并打印当前账号的用户信息

```python
import asyncio

import aiotieba as tb


async def main():
    async with tb.Client("default") as client:
        user = await client.get_self_info()

    print(user)

asyncio.run(main())
```

### 期望结果

如果你的`BDUSS`填写无误，你会获得类似下面这样的结果

```log
{'user_id': 957339815, 'user_name': 'Starry_OvO', 'portrait': 'tb.1.8277e641.gUE2cTq4A4z5fi2EHn5k3Q', 'show_name': 'Starry_OvO', 'tieba_uid': '316436307', 'glevel': 0, 'gender': 0, 'age': 0.0, 'post_num': 0, 'sign': '', 'vimage': '', 'ip': '', 'priv_like': 1}
```

## 多账号

### 准备工作

在`aiotieba.toml`中添加一个新账户，例如：

```toml
[User]

[User.default]
BDUSS = "..."

[User.anotherKey]
BDUSS = "..."
```

然后你就可以通过输入不同的`BDUSS_key`来使用不同的账号

### 样例代码

本样例将获取并打印多个账号的用户信息

```python
import asyncio

import aiotieba as tb


async def main():
    async with tb.Client("default") as client:
        user = await client.get_self_info()
        print(f"默认账号的用户信息: {user!r}")
    async with tb.Client("anotherKey") as client:
        user = await client.get_self_info()
        print(f"另一个账号的用户信息: {user!r}")


asyncio.run(main())
```

## 简单并发爬虫

### 样例代码

本样例将同时请求用户个人信息和天堂鸡汤吧首页前30帖，并将他们打印出来

```python
import asyncio

import aiotieba as tb


async def main():
    async with tb.Client("default") as client:
        # [1] 什么是`asyncio.gather`？
        # 参考官方文档：并发运行任务
        # https://docs.python.org/zh-cn/3/library/asyncio-task.html#running-tasks-concurrently
        user, threads = await asyncio.gather(client.get_self_info(), client.get_threads('天堂鸡汤'))

    # 将获取的信息打印到日志
    print(f"当前用户信息: {user!r}")
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
当前用户信息: {'user_id': 957339815, 'user_name': 'Starry_OvO', 'portrait': 'tb.1.8277e641.gUE2cTq4A4z5fi2EHn5k3Q', 'nick_name': 'ºStarry'}
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
    tb.LOG().info("Spider start")

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
                    # asyncio.wait_for会等待作为参数的协程执行完毕直到超时
                    # timeout=1即把超时时间设为1秒
                    # 如果超过1秒未获取到新的页码pn，asyncio.wait_for(...)将抛出asyncio.TimeoutError
                    pn = await asyncio.wait_for(task_queue.get(), timeout=1)
                    tb.LOG().debug(f"Worker#{i} handling pn:{pn}")
                except asyncio.TimeoutError:
                    # 捕获asyncio.TimeoutError以退出协程
                    if is_running is False:
                        # 如果is_running为False，意味着不需要再轮询task_queue获取新任务
                        tb.LOG().debug(f"Worker#{i} quit")
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

    tb.LOG().info(f"Spider complete. Time cost: {time.perf_counter()-start_time:.4f} secs")

    # 按主题帖浏览量降序排序
    thread_list.sort(key=lambda thread: thread.view_num, reverse=True)
    # 将浏览量最高的10个主题帖的信息打印到日志
    for i, thread in enumerate(thread_list[0:10], 1):
        tb.LOG().info(f"Rank#{i} view_num:{thread.view_num} title:{thread.title}")


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
