# 实用工具

## 签到

```python
from __future__ import annotations

import asyncio

import aiotieba as tb


async def sign(BDUSS_key: str, *, retry_times: int = 0):
    """
    各种签到

    Args:
        BDUSS (str): 用于创建客户端
        retry_times (int, optional): 重试次数. Defaults to 0.
    """

    async with tb.Client(BDUSS_key) as client:
        # 成长等级签到
        for _ in range(retry_times):
            await asyncio.sleep(1.0)
            if await client.sign_growth():
                break
        # 分享任务
        for _ in range(retry_times):
            await asyncio.sleep(1.0)
            if await client.sign_growth_share():
                break
        # 虚拟形象点赞
        for _ in range(retry_times):
            await asyncio.sleep(1.0)
            if await client.agree_vimage(6050811555):
                break
        # 互关任务
        for _ in range(retry_times):
            await asyncio.sleep(1.0)
            someone = 'tb.1.2fc1394a.ukuFqA26BTuAeXqYr1Nmwg'
            success = False
            success = await client.unfollow_user(someone)
            if not success:
                continue
            success = await client.follow_user(someone)
            if not success:
                continue
            if success:
                break
        # 签到
        retry_list: list[str] = []
        for pn in range(1, 9999):
            forums = await client.get_self_follow_forums(pn)
            retry_list += [forum.fname for forum in forums]
            if not forums.has_more:
                break
        for _ in range(retry_times + 1):
            new_retry_list: list[str] = []
            for fname in retry_list:
                ret = await client.sign_forum(fname)
                if ret.err is not None and ret.err.code not in [160002, 340006]:
                    new_retry_list.append(fname)
                await asyncio.sleep(1.0)
            if not new_retry_list:
                break
            retry_list = new_retry_list


async def main():
    await sign("在此处输入待签到账号的BDUSS", retry_times=3)
    await sign("在此处输入另一个待签到账号的BDUSS", retry_times=3)


asyncio.run(main())
```

## 将个人主页的帖子全部设为隐藏

```python
import asyncio

import aiotieba as tb


async def main():
    async with tb.Client("在此处输入你的BDUSS") as client:
        # 海象运算符(:=)会在创建threads变量并赋值的同时返回该值，方便while语句检查其是否为空
        # 更多信息请搜索“Python海象运算符”
        while threads := await client.get_user_threads():
            await asyncio.gather(*[client.set_thread_private(thread.fid, thread.tid, thread.pid) for thread in threads])


asyncio.run(main())
```

## 屏蔽贴吧，使它们不再出现在你的首页推荐里

```python
import asyncio

import aiotieba as tb


async def main():
    async with tb.Client("在此处输入你的BDUSS") as client:
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


async def main():
    async with tb.Client("在此处输入你的BDUSS") as client:
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

## 清除旧版乱码昵称

```python
import asyncio

import aiotieba as tb


async def main():
    async with tb.Client("在此处输入你的BDUSS") as client:
        user = await client.get_self_info(tb.ReqUInfo.USER_NAME)
        await client.set_nickname_old(user.user_name)


asyncio.run(main())
```

## 清空粉丝列表（无法复原的危险操作，请谨慎使用！）

```python
import asyncio

import aiotieba as tb


async def main():
    async with tb.Client("在此处输入你的BDUSS") as client:
        while fans := await client.get_fans():
            await asyncio.gather(*[client.remove_fan(fan.user_id) for fan in fans])


asyncio.run(main())
```

## 清除所有历史回复（无法复原的危险操作，请谨慎使用！）

```python
import asyncio

import aiotieba as tb


async def main():
    async with tb.Client("在此处输入你的BDUSS") as client:
        while posts_list := await client.get_user_posts():
            await asyncio.gather(*[client.del_post(post.fid, post.tid, post.pid) for posts in posts_list for post in posts])


asyncio.run(main())
```
