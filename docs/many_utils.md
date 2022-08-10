# 实用工具

## 签到水经验

```python
import asyncio
from typing import List

import aiotieba as tb


class WaterTask(object):

    __slots__ = ['fname', 'tid', 'times']

    def __init__(self, fname: str, tid: int, times: int = 6) -> None:
        self.fname = fname
        self.tid = tid
        self.times = times


async def water(BDUSS_key: str, tasks: List[WaterTask]) -> None:
    """
    水帖

    Args:
        BDUSS_key (str): 用于创建客户端
        tasks (List[WaterTask]): 水帖任务列表
    """

    async with tb.Client(BDUSS_key) as client:
        for task in tasks:
            for i in range(task.times):
                await client.add_post(task.fname, task.tid, str(i))
                await asyncio.sleep(120)


async def agree(BDUSS_key: str, tids: List[int], *, max_times: int = 3):
    """
    点赞楼层刷经验

    Args:
        BDUSS_key (str): 用于创建客户端
        tids (list[int]): tid列表 对每个tid的最后一楼执行点赞操作
        times (int, optional): 点赞轮数 每轮包含一次点赞和一次取消赞. Defaults to 3.
    """

    async with tb.Client(BDUSS_key) as client:

        for tid in tids:

            posts = await client.get_posts(tid, 0xFFFF, rn=0, sort=1)
            tid = posts[-1].tid
            pid = posts[-1].pid

            for _ in range(max_times):
                await client.agree(tid, pid)
                await asyncio.sleep(6)
                await client.unagree(tid, pid)
                await asyncio.sleep(6)


async def sign(BDUSS_key: str, *, retry_times: int = 0) -> None:
    """
    签到

    Args:
        BDUSS_key (str): 用于创建客户端
        retry_times (int, optional): 重试次数. Defaults to 0.
    """

    async with tb.Client(BDUSS_key) as client:

        retry_list: List[str] = []
        for pn in range(1, 9999):
            forums = await client.get_self_follow_forums(pn)
            retry_list += [forum.fname for forum in forums]
            if not forums.has_more:
                break

        for _ in range(retry_times + 1):
            new_retry_list: List[str] = []
            for fname in retry_list:
                if not await client.sign_forum(fname):
                    new_retry_list.append(fname)
            if not new_retry_list:
                break
            retry_list = new_retry_list


async def main() -> None:

    agree_tids = [2986143112, 3611123694, 7689322018, 7966279046]

    await asyncio.gather(
        # 大号每天在lol半价吧和v吧水6帖 在个人吧水1帖以保证吧主不掉
        water(
            "default",
            [
                WaterTask("lol半价", 2986143112),
                WaterTask("v", 3611123694),
                WaterTask("starry", 6154402005, 1),
            ],
        ),
        # 大小号每天签到 大号每次签到重试3轮 确保连签不断 小号只重试1轮
        sign("default", retry_times=3),
        sign("backup", retry_times=1),
        # 大小号每天点赞刷经验
        agree("default", agree_tids, max_times=1),
        agree("backup", agree_tids, max_times=1),
    )


asyncio.run(main())
```

## 将个人主页的帖子全部设为隐藏

```python
import asyncio

import aiotieba as tb


async def main() -> None:

    async with tb.Client("default") as client:
        # 海象运算符(:=)会在创建threads变量并赋值的同时返回该值，方便while语句检查其是否为空
        # 更多信息请搜索“Python海象运算符”
        while threads := await client.get_self_public_threads():
            await asyncio.gather(*[client.set_privacy(thread.fid, thread.tid, thread.pid) for thread in threads])


asyncio.run(main())
```

## 屏蔽贴吧，使它们不再出现在你的首页推荐里

```python
import asyncio

import aiotieba as tb


async def main() -> None:
    async with tb.Client("default") as client:
        await asyncio.gather(
            *[
                client.dislike_forum(fname)
                for fname in [
                    "贴吧名A",
                    "贴吧名B",
                    "贴吧名C",
                ]  # 把你要屏蔽的贴吧名填在这个列表里
            ]
        )


asyncio.run(main())
```

## 解除多个贴吧的屏蔽状态

```python
import asyncio

import aiotieba as tb


async def main() -> None:
    async with tb.Client("default") as client:
        # 此列表用于设置例外
        # 将你希望依然保持屏蔽的贴吧名填在这个列表里
        preserve_fnames = [
            "保持屏蔽的贴吧名A",
            "保持屏蔽的贴吧名B",
            "保持屏蔽的贴吧名C",
        ]
        while 1:
            forums = await client.get_dislike_forums()
            await asyncio.gather(
                *[client.undislike_forum(forum.fid) for forum in forums if forum.fname not in preserve_fnames]
            )
            if not forums.has_more:
                break


asyncio.run(main())
```

## 清空default账号的粉丝列表（无法复原的危险操作，请谨慎使用！）

```python
import asyncio

import aiotieba as tb


async def main() -> None:
    async with tb.Client("default") as client:
        while fans := await client.get_fans():
            await asyncio.gather(*[client.remove_fan(fan.user_id) for fan in fans])


asyncio.run(main())
```

## 清除default账号的所有历史回复（无法复原的危险操作，请谨慎使用！）

```python
import asyncio

import aiotieba as tb


async def main() -> None:
    async with tb.Client('default') as client:
        while posts_list := await client.get_self_posts():
            await asyncio.gather(
                *[client.del_post(post.fid, post.pid) for posts in posts_list for post in posts]
            )


asyncio.run(main())
```
