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

本框架以提高二次开发速度为首要设计目标，命名规则统一，类型注解和方法注释完全覆盖所有用户接口，让开发者免受贴吧混乱的名称系统与不统一的接口标准的折磨

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

+ 继续阅读[**入门教程**](https://v-8.top/tutorial/quickstart)

## 友情链接

+ [另一个仍在活跃更新的贴吧管理器（有用户界面）](https://github.com/dog194/TiebaManager)
+ [用户反馈（我的个人吧）](https://tieba.baidu.com/starry)

## 客户名单

<details><summary>2023.01.09更新</summary>

|      吧名      | 关注用户数 | 最近29天日均访问量 | 日均主题帖数 | 日均回复数 |
| :------------: | :--------: | :----------------: | :----------: | :--------: |
|    抗压背锅    | 4,517,642  |      856,710       |    1,581     |   69,835   |
|     孙笑川     | 3,151,834  |      669,932       |    6,092     |  199,125   |
|    lol半价     | 2,002,779  |       98,536       |    1,499     |   33,516   |
|      宫漫      | 1,473,912  |       42,065       |     151      |   2,237    |
|    逆水寒ol    |  755,394   |       32,813       |     116      |   2,232    |
|    新孙笑川    |  532,770   |       41,530       |     293      |   14,373   |
|     vtuber     |  220,861   |       11,017       |      59      |    823     |
|     asoul      |  155,793   |       10,953       |      73      |    418     |
|      嘉然      |   59,451   |       11,428       |      85      |   1,119    |
|      向晚      |   30,744   |       7,079        |      52      |    700     |
|      贝拉      |   21,784   |       7,480        |      34      |    554     |
|      乃琳      |   17,344   |       3,588        |      21      |    275     |
| vtuber自由讨论 |   17,215   |       4,304        |      1       |     32     |

</details>
