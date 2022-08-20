<div align="center">

![Tieba-Manager](https://socialify.git.ci/Starry-OvO/Tieba-Manager/image?description=1&descriptionEditable=Asynchronous%20I%2FO%20Client%2FReviewer%20for%20Baidu%20Tieba&font=Bitter&language=1&logo=https%3A%2F%2Favatars.githubusercontent.com%2Fu%2F48282276&name=1&owner=1&pattern=Circuit%20Board&theme=Dark)

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Starry-OvO/Tieba-Manager/CI?label=CI&logo=github)](https://github.com/Starry-OvO/Tieba-Manager/actions)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Starry-OvO/Tieba-Manager?logo=lgtm)](https://lgtm.com/projects/g/Starry-OvO/Tieba-Manager/context:python)
[![Code style: black](https://img.shields.io/badge/code_style-black-000000)](https://github.com/psf/black)

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

+ 检查Python版本

aiotieba需要**Python>=3.9**和[**CPython**](https://www.python.org/downloads/)

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

## 客户名单

2022.08.20更新

|      吧名      | 关注用户数 | 最近29天日均访问量 | 日均主题帖数 | 日均回复数 |
| :------------: | :--------: | :----------------: | :----------: | :--------: |
|    抗压背锅    | 3,936,224  |     1,260,571      |    2,714     |   92,072   |
|     孙笑川     | 2,315,491  |      743,139       |    8,692     |  223,208   |
|    lol半价     | 1,957,169  |      109,517       |     285      |   5,608    |
|      宫漫      | 1,314,492  |       51,454       |     247      |   3,727    |
|    新孙笑川    |  306,332   |       58,692       |     489      |   20,007   |
|     vtuber     |  211,954   |       15,185       |     102      |    959     |
|     asoul      |  158,475   |       25,388       |     261      |   1,617    |
|      嘉然      |   56,377   |       23,981       |     164      |   2,403    |
|      向晚      |   29,030   |       16,878       |     162      |   2,276    |
|      贝拉      |   21,631   |       12,378       |      63      |   1,132    |
|      乃琳      |   17,139   |       6,873        |      46      |    601     |
| vtuber自由讨论 |   16,675   |       4,416        |      4       |     89     |
| asoul一个魂儿  |   14,716   |       1,240        |      8       |     68     |
|     贝贝珈     |   1,644    |       1,140        |      2       |     34     |

## 友情链接

+ [另一个仍在活跃更新的贴吧管理器（有用户界面）](https://github.com/dog194/TiebaManager)
+ [用户反馈（我的个人吧）](https://tieba.baidu.com/starry)
