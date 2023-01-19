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

**aiotieba**使用[**aiohttp**](https://github.com/aio-libs/aiohttp)封装了大量[百度贴吧核心API](https://github.com/Starry-OvO/aiotieba/blob/master/aiotieba/client)

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
+ [基于aiotieba的高弹性吧务审查框架](https://github.com/Starry-OvO/aiotieba-reviewer)
+ [贴吧protobuf定义文件合集](https://github.com/n0099/tbclient.protobuf)
