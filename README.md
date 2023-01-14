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
|    抗压背锅    | 4,559,088  |      809,881       |    1,458     |   69,858   |
|     孙笑川     | 3,183,042  |      681,571       |    6,157     |  205,739   |
|    lol半价     | 2,004,582  |      112,378       |    2,030     |   48,063   |
|      宫漫      | 1,483,956  |       42,271       |     150      |   2,309    |
|    逆水寒ol    |  766,614   |       44,014       |     181      |   3,278    |
|    新孙笑川    |  543,607   |       43,620       |     302      |   15,348   |
|     vtuber     |  221,155   |       11,315       |      61      |    929     |
|     asoul      |  155,754   |       9,692        |      52      |    316     |
|      嘉然      |   59,529   |       11,070       |      79      |   1,120    |
|      向晚      |   30,770   |       6,391        |      43      |    561     |
|      贝拉      |   21,788   |       7,496        |      33      |    541     |
|      乃琳      |   17,342   |       3,509        |      19      |    238     |
| vtuber自由讨论 |   17,235   |       4,532        |      1       |     28     |

</details>
