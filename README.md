<div align="center">

![Tieba-Manager](https://socialify.git.ci/Starry-OvO/Tieba-Manager/image?description=1&descriptionEditable=Asynchronous%20I%2FO%20Client%2FReviewer%20for%20Baidu%20Tieba&font=Bitter&language=1&logo=https%3A%2F%2Favatars.githubusercontent.com%2Fu%2F48282276&name=1&owner=1&pattern=Circuit%20Board&theme=Dark)

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Starry-OvO/Tieba-Manager/CI?label=CI&logo=github)](https://github.com/Starry-OvO/Tieba-Manager/actions)
[![PyPI version](https://badge.fury.io/py/aiotieba.svg)](https://badge.fury.io/py/aiotieba)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Starry-OvO/Tieba-Manager?logo=lgtm)](https://lgtm.com/projects/g/Starry-OvO/Tieba-Manager/context:python)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aiotieba)](https://pypi.org/project/aiotieba)

</div>

## 简介

**aiotieba**使用[**asyncio**](https://tutorials.python.org/zh-cn/3/library/asyncio.html)和[**aiohttp**](https://github.com/aio-libs/aiohttp)还原了**百度贴吧客户端**的[大部分核心接口](aiotieba/client.py)，并为吧务管理设计了一套[内容审查脚手架](aiotieba/reviewer.py)

<details>

<summary>贴吧接口列表</summary>

> 按**回复时间**/**发布时间**/**热门序**获取贴吧**主题帖**/**精华帖列表**。支持获取带**转发**/**投票**/**转发嵌套投票**/**各种卡片**的主题帖信息
> 
> 获取带**图片链接**/**小尾巴内容**/**点赞情况**/**用户信息**（[**用户名**](tutorials/tutorial.md#user_name)/[**portrait**](tutorials/tutorial.md#portrait)/[**user_id**](tutorials/tutorial.md#user_id)/**等级**/**性别**/**是否锁回复**）/每条回复的**前排楼中楼**（支持按或不按点赞数排序）的**楼层列表**
> 
> 获取带所有前述用户信息的**楼中楼列表**
> 
> 根据[**用户名**](tutorials/tutorial.md#user_name)/[**portrait**](tutorials/tutorial.md#portrait)/[**user_id**](tutorials/tutorial.md#user_id)中的任一项反查其他用户信息，或通过用户主页的[**tieba_uid**](tutorials/tutorial.md#tieba_uid)反查其他用户信息
> 
> 使用小吧主、语音小编的账号**删帖**/**屏蔽**/**封禁**。支持**删除视频帖**/**批量删帖**/**多于1天的封禁**
> 
> 使用已被大吧主分配解封/恢复/处理申诉权限的吧务账号**解封**/**恢复**/**处理申诉**
> 
> 使用大吧主账号**推荐帖子到首页**/**移动帖子到指定分区**/**加精**/**撤精**/**置顶**/**撤置顶**/**添加黑名单**/**查看黑名单**/**取消黑名单**
> 
> 获取其他用户的**主页信息**/**关注贴吧列表**/**关注用户列表**/**粉丝列表**/**发布的主题帖列表**
> 
> 使用当前账号**关注贴吧**/**取关贴吧**/**关注用户**/**取关用户**/**移除粉丝**/**获取屏蔽贴吧列表**/**屏蔽贴吧**/**取消屏蔽贴吧**/**点赞点踩**/**取消点赞点踩**/**签到**/**水帖**/**发送私信**/**获取回复历史**
> 
> 获取一个贴吧的**最新关注用户列表**/**等级排行榜**/**吧务列表**/**吧详情**

</details>

<details>

<summary>额外的审查功能列表</summary>

> 数据库功能：**缓存贴吧常量**（如贴吧名到fid的映射关系、用户基本信息等）/**为用户添加标记**/**为帖子或回复添加标记**/**为图像hash添加标记**
> 
> 图像处理功能：**图像解码**/**二维码解析**/**图像hash计算**

</details>

## 安装并使用

+ 检查Python版本 (**>=3.9**)

+ 安装

```bash
pip install aiotieba
```

+ 体验一下

```python
import asyncio

import aiotieba


async def main():
    async with aiotieba.Client() as client:
        print(await client.get_threads("图拉丁"))


asyncio.run(main())
```

+ 继续阅读[**入门教程**](tutorials/tutorial.md)

## 友情链接

+ [另一个仍在活跃更新的贴吧管理器（有用户界面）](https://github.com/dog194/TiebaManager)
+ [用户反馈（我的个人吧）](https://tieba.baidu.com/starry)

## 客户名单

<details>

<summary>2022.08.27更新</summary>

|      吧名      | 关注用户数 | 最近29天日均访问量 | 日均主题帖数 | 日均回复数 |
| :------------: | :--------: | :----------------: | :----------: | :--------: |
|    抗压背锅    | 3,965,757  |     1,486,045      |    3,869     |  109,791   |
|     孙笑川     | 2,366,222  |      772,065       |    8,952     |  237,511   |
|    lol半价     | 1,957,420  |      100,713       |     232      |   4,806    |
|      宫漫      | 1,317,697  |       49,323       |     241      |   3,733    |
|    新孙笑川    |  318,695   |       66,808       |     538      |   23,907   |
|     vtuber     |  212,540   |       13,339       |      81      |    767     |
|     asoul      |  158,310   |       22,251       |     221      |   1,336    |
|      嘉然      |   56,630   |       22,516       |     168      |   2,425    |
|      向晚      |   29,268   |       16,525       |     158      |   2,123    |
|      贝拉      |   21,655   |       11,522       |      57      |   1,004    |
|      乃琳      |   17,150   |       6,217        |      41      |    531     |
| vtuber自由讨论 |   16,720   |       4,625        |      4       |     96     |
| asoul一个魂儿  |   14,690   |       1,178        |      8       |     64     |
|     贝贝珈     |   1,639    |       1,019        |      2       |     29     |

</details>
