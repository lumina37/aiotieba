# 

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/48282276/217530379-1348f7c5-7056-48f4-8c64-1c74caf5497c.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://user-images.githubusercontent.com/48282276/217530385-98a2fb24-ff6e-4b27-990f-998b66c2ab5e.svg">
  <img src="https://user-images.githubusercontent.com/48282276/217530385-98a2fb24-ff6e-4b27-990f-998b66c2ab5e.svg">
</picture>
</p>

<p align="center">
<a href="https://github.com/Starry-OvO/aiotieba/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/Starry-OvO/aiotieba/CI.yml?branch=develop&label=CI&logo=github&style=flat-square" alt="GitHub Workflow Status">
</a>
<a href="https://pypi.org/project/aiotieba">
    <img src="https://img.shields.io/pypi/v/aiotieba?color=g&style=flat-square" alt="PyPI - Version">
</a>
<a href="https://pypi.org/project/aiotieba">
    <img src="https://img.shields.io/pypi/pyversions/aiotieba?style=flat-square" alt="PyPI - Python Version">
</a>
</p>

---

## 安装

```shell
pip install aiotieba
```

## 尝试一下

```python
import asyncio

import aiotieba


async def main():
    async with aiotieba.Client() as client:
        threads = await client.get_threads("天堂鸡汤")
        print(threads[3:5])


asyncio.run(main())
```

*输出样例*

```log
[{'tid': 8256346027, 'pid': 146825511891, 'user': '煞南波万', 'text': '如题，好奇大家会存什么样的图图✧◔.̮◔'}, {'tid':: 8255392021, 'pid': 146820360992, 'user': 'Yfy1357oy', 'text': '有没有一些治愈的音乐推荐呢？\n如题，范围很广阔，鼓舞人心的、轻快的、浪漫的，有词的、无词的，中文的、外文的，都可以。希望大家能从音乐中找到生活的力量'}]
```

继续阅读[**入门教程**](https://aiotieba.cc/tutorial/start)

## 项目特色

+ 收录[**数十个常用API**](https://github.com/Starry-OvO/aiotieba/tree/develop/aiotieba/api)
+ 类型注解全覆盖，方法注释全覆盖，类属性注释全覆盖，内部命名统一
+ 请求参数支持protobuf序列化
+ 支持websocket接口
+ 高一致性的密码学实现
