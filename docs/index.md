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
</a>
<a href="https://pdm.fming.dev">
    <img src="https://img.shields.io/badge/pdm-managed-blueviolet?style=flat-square" alt="pdm-managed">
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
        for thread in threads[3:6]:
            print(thread)


asyncio.run(main())
```

*输出样例*

```log
{'tid': 8537603600, 'pid': 148268345950, 'user': 'iqhaoo', 'text': '一人发一句最喜欢的游戏台词\n楼主先来\n很喜欢lol布隆说的“夜晚越黑暗，星星就越明亮”，尤其在当下这个有着诸多缺点的世界里，这句话让我感觉舒服了很多在人们已不再相信理想主义的至暗时刻，高擎炬火之人便显得更加重要，至少我会坚持我的理想'}
{'tid': 8093410706, 'pid': 145850248077, 'user': '粉樱yyc', 'text': '大概是剪切板里的一些有意思的话\n今天看自己的剪切板快满了，稍微翻翻突然发现以前存的一些话还挺有意思，就放在这里啦\n（咦，疑似水帖啊我）'}
{'tid': 8537699088, 'pid': 148268822981, 'user': '2003hepsee', 'text': '记录一下自己人生第一次当“老师”的经历^_^\n明天我带的孩子们就“毕业”了，第一次当老师我改变了很多也收获了很多，就想着给自己记录一下这段宝贵的经历:-)'}
```

继续阅读[**入门教程**](https://aiotieba.cc/tutorial/start)

## 项目特色

+ 收录[**数十个常用API**](https://github.com/Starry-OvO/aiotieba/tree/develop/aiotieba/api)
+ 类型注解全覆盖，方法注释全覆盖，类属性注释全覆盖，内部命名统一
+ 请求参数支持protobuf序列化
+ 支持websocket接口
+ 高一致性的密码学实现
