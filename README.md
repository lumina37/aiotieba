<div align="center">

# Tieba-Manager

[![gitee](https://img.shields.io/badge/mirror-gitee-red)](https://gitee.com/Starry-OvO/Tieba-Manager)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Starry-OvO/Tieba-Manager?logo=lgtm)](https://lgtm.com/projects/g/Starry-OvO/Tieba-Manager/context:python)
[![Code style: black](https://img.shields.io/badge/code_style-black-000000)](https://github.com/psf/black)

</div>

## 简介

`aiotieba`库是一个使用[`aiohttp`](https://github.com/aio-libs/aiohttp)实现的**异步贴吧客户端**

`aiotieba`封装了大量实用接口，并额外添加了一些数据库和图像处理功能以方便自动化的吧务管理

<details>

<summary>封装的实用接口列表</summary>

+ 按**回复时间**/**发布时间**/**热门序**获取贴吧**主题帖**/**精华帖列表**。支持获取带**转发**/**投票**/**转发嵌套投票**/**各种卡片**的主题帖信息
+ 获取带**图片链接**/**小尾巴内容**/**点赞情况**/**用户信息**（**用户名**/**user_id**/**portrait**/**等级**/**性别**/**是否锁回复**）/每条回复的**前排楼中楼**（支持按或不按点赞数排序）的**回复列表**
+ 获取带所有前述用户信息的**楼中楼列表**
+ 根据**用户名**/**昵称**/**portrait**/**user_id**中的任一项反查其他用户信息，或通过用户主页的**tieba_uid**反查其他用户信息
+ 使用小吧主、语音小编的`BDUSS`**删帖**/**屏蔽**/**封禁**任意用户3天或10天
+ 使用已被大吧主分配解封/恢复/处理申诉权限的吧务`BDUSS`**解封**/**恢复**/**处理申诉**
+ 使用大吧主`BDUSS`**推荐帖子到首页**/**移动帖子到指定分区**/**加精**/**撤精**/**置顶**/**撤置顶**/**添加黑名单**/**查看黑名单**/**取消黑名单**
+ 获取用户**主页信息**/**关注贴吧列表**/**屏蔽贴吧列表**/**关注用户列表**/**粉丝列表**/**发帖历史**/**回复历史**
+ 获取贴吧**最新关注用户列表**/**等级排行榜**/**吧务列表**/**吧详情**
+ 使用`BDUSS`**关注贴吧**/**取关贴吧**/**关注用户**/**取关用户**/**移除粉丝**/**屏蔽贴吧**/**取消屏蔽贴吧**/**签到**/**水帖**/**发送私信**

</details>

<details>

<summary>额外功能列表</summary>

+ 数据库功能：**缓存贴吧常量**（如贴吧名到fid的映射关系）/**为用户添加标记**/**为帖子或回复添加标记**/**为图像hash添加标记**
+ 图像处理功能：**图像解码**/**二维码解析**/**图像hash计算**

</details>

在`aiotieba`的基础上，我开发了多种自动化吧务管理工具，如[云审查工具](docs/cloud_review_tutorial.md)和[指令管理器](../../wiki/%E6%8C%87%E4%BB%A4%E7%AE%A1%E7%90%86%E5%99%A8%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6)，以及一些[实用脚本案例](docs/many_utils.md)

## 安装并使用

+ 确保你的[`Python`](https://www.python.org/downloads/)版本在`3.9`及以上

+ 拉取代码

```bash
git clone https://github.com/Starry-OvO/Tieba-Manager.git
```

+ 安装依赖项

```bash
cd ./Tieba-Manager
pip install -r requirements.txt
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

+ 继续阅读[入门教程](docs/tutorial.md)

## 友情链接

+ [另一个仍在活跃更新的贴吧管理器（有用户界面）](https://github.com/dog194/TiebaManager)
+ [用户反馈（我的个人吧）](https://tieba.baidu.com/starry)

## 客户名单

2022.07.20更新

按关注用户数降序排列

|      吧名      | 关注用户数 | 最近29天日均访问量 | 日均主题帖数 | 日均回复数 |
| :------------: | :--------: | :----------------: | :----------: | :--------: |
|    抗压背锅    | 3,792,789  |     1,060,448      |    3,089     |   78,990   |
|     孙笑川     | 2,103,350  |      593,826       |    6,628     |  174,965   |
|    lol半价     | 1,951,703  |      160,077       |     527      |   9,969    |
|      宫漫      | 1,283,331  |       46,427       |     255      |   3,520    |
|    新孙笑川    |  255,158   |       43,452       |     403      |   15,495   |
|     vtuber     |  209,219   |       23,323       |     184      |   2,024    |
|     asoul      |  159,195   |       46,927       |     498      |   4,127    |
|      嘉然      |   55,089   |       20,787       |     168      |   2,325    |
|      向晚      |   28,180   |       18,427       |     182      |   2,524    |
|      贝拉      |   21,594   |       14,850       |      88      |   1,693    |
|      乃琳      |   16,739   |       5,635        |      40      |    585     |
| vtuber自由讨论 |   16,521   |       2,473        |      3       |     71     |
| asoul一个魂儿  |   14,952   |       1,926        |      27      |    237     |
|     贝贝珈     |   1,661    |       1,366        |      5       |     57     |
