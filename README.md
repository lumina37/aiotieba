<p align="center">

<a href="https://socialify.git.ci">
    <img src="https://raw.githubusercontent.com/Starry-OvO/aiotieba/master/docs/img/aiotieba.svg">
</a>

</p>

<div align="center">
<p>
<a href="https://github.com/Starry-OvO/aiotieba/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/Starry-OvO/aiotieba/CI.yml?branch=develop&label=CI&logo=github" alt="GitHub Workflow Status">
</a>
<a href="https://pypi.org/project/aiotieba">
    <img src="https://img.shields.io/pypi/v/aiotieba?color=g" alt="PyPI - Version">
</a>
<a href="https://pypi.org/project/aiotieba">
    <img src="https://img.shields.io/pypi/pyversions/aiotieba" alt="PyPI - Python Version">
</a>
</p>
</div>

---

## 简介

**aiotieba**使用[**asyncio**](https://docs.python.org/zh-cn/3/library/asyncio.html)和[**httpx**](https://github.com/encode/httpx)封装了大量[百度贴吧核心API](https://github.com/Starry-OvO/aiotieba/blob/master/aiotieba/client)

本框架以提高二次开发速度为首要设计目标，命名规则统一，类型注解和方法注释完全覆盖所有用户接口

## 安装并使用

+ 安装

```shell
pip install aiotieba
```

+ 体验一下

```python
import asyncio

import aiotieba


async def main():
    async with aiotieba.Client() as client:
        print(await client.get_threads("天堂鸡汤"))


asyncio.run(main())
```

+ 继续阅读[**入门教程**](https://v-8.top/tutorial/start)

## 友情链接

+ [另一个仍在活跃更新的贴吧管理器（有用户界面）](https://github.com/dog194/TiebaManager)
+ [贴吧protobuf定义文件合集](https://github.com/n0099/tbclient.protobuf)

## 客户名单

<details><summary>2023.01.13更新</summary>

|      吧名      | 关注用户数 | 最近29天日均访问量 | 日均主题帖数 | 日均回复数 |
| :------------: | :--------: | :----------------: | :----------: | :--------: |
|    抗压背锅    | 4,552,065  |      812,535       |    1,462     |   69,771   |
|     孙笑川     | 3,177,257  |      680,498       |    6,161     |  204,330   |
|    lol半价     | 2,004,105  |      108,075       |    1,929     |   45,324   |
|      宫漫      | 1,483,281  |       42,341       |     152      |   2,335    |
|    逆水寒ol    |  764,905   |       40,229       |     159      |   2,923    |
|    新孙笑川    |  540,857   |       43,600       |     300      |   15,474   |
|     vtuber     |  221,070   |       11,236       |      60      |    912     |
|     asoul      |  155,748   |       9,865        |      53      |    323     |
|      嘉然      |   59,506   |       11,010       |      79      |   1,110    |
|      向晚      |   30,771   |       6,374        |      43      |    555     |
|      贝拉      |   21,797   |       7,341        |      33      |    533     |
|      乃琳      |   17,347   |       3,442        |      18      |    231     |
| vtuber自由讨论 |   17,228   |       4,487        |      1       |     30     |

</details>
