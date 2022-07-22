<div align="center">

# Tieba-Manager

[![gitee](https://img.shields.io/badge/mirror-gitee-red)](https://gitee.com/Starry-OvO/Tieba-Manager)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Starry-OvO/Tieba-Manager?logo=lgtm)](https://lgtm.com/projects/g/Starry-OvO/Tieba-Manager/context:python)
[![Code style: black](https://img.shields.io/badge/code_style-black-000000)](https://github.com/psf/black)

</div>

## 简介

`aiotieba`库是一个使用[`aiohttp`](https://github.com/aio-libs/aiohttp)实现的**异步贴吧客户端**

<details>

<summary>封装的贴吧接口列表</summary>

+ 按**回复时间**/**发布时间**/**热门序**获取贴吧**主题帖**/**精华帖列表**。支持获取带**转发**/**投票**/**转发嵌套投票**/**各种卡片**的主题帖信息
+ 获取带**图片链接**/**小尾巴内容**/**点赞情况**/**用户信息**（[**用户名**](docs/tutorial.md#user_name)/[**portrait**](docs/tutorial.md#portrait)/[**user_id**](docs/tutorial.md#user_id)/**等级**/**性别**/**是否锁回复**）/每条回复的**前排楼中楼**（支持按或不按点赞数排序）的**回复列表**
+ 获取带所有前述用户信息的**楼中楼列表**
+ 根据[**用户名**](docs/tutorial.md#user_name)/[**portrait**](docs/tutorial.md#portrait)/[**user_id**](docs/tutorial.md#user_id)中的任一项反查其他用户信息，或通过用户主页的[**tieba_uid**](docs/tutorial.md#tieba_uid)反查其他用户信息
+ 使用小吧主、语音小编的账号**删帖**/**屏蔽**/**封禁**任意用户3天或10天
+ 使用已被大吧主分配解封/恢复/处理申诉权限的吧务账号**解封**/**恢复**/**处理申诉**
+ 使用大吧主账号**推荐帖子到首页**/**移动帖子到指定分区**/**加精**/**撤精**/**置顶**/**撤置顶**/**添加黑名单**/**查看黑名单**/**取消黑名单**
+ 获取用户**主页信息**/**关注贴吧列表**/**屏蔽贴吧列表**/**关注用户列表**/**粉丝列表**/**发帖历史**/**回复历史**
+ 获取贴吧**最新关注用户列表**/**等级排行榜**/**吧务列表**/**吧详情**
+ **关注贴吧**/**取关贴吧**/**关注用户**/**取关用户**/**移除粉丝**/**屏蔽贴吧**/**取消屏蔽贴吧**/**签到**/**水帖**/**发送私信**

</details>

<details>

<summary>附加功能列表</summary>

+ 数据库功能：**缓存贴吧常量**（如贴吧名到fid的映射关系）/**为用户添加标记**/**为帖子或回复添加标记**/**为图像hash添加标记**
+ 图像处理功能：**图像解码**/**二维码解析**/**图像hash计算**

</details>

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

## 客户名单

2022.07.22更新

|      吧名      | 关注用户数 | 最近29天日均访问量 | 日均主题帖数 | 日均回复数 |
| :------------: | :--------: | :----------------: | :----------: | :--------: |
|    抗压背锅    | 3,813,406  |     1,064,757      |    3,037     |   79,190   |
|     孙笑川     | 2,117,653  |      602,511       |    6,799     |  177,652   |
|    lol半价     | 1,951,965  |      163,064       |     542      |   10,183   |
|      宫漫      | 1,287,342  |       47,223       |     254      |   3,574    |
|    新孙笑川    |  258,377   |       43,793       |     412      |   15,742   |
|     vtuber     |  209,475   |       27,556       |     214      |   2,336    |
|     asoul      |  159,132   |       41,933       |     446      |   3,502    |
|      嘉然      |   55,158   |       20,262       |     162      |   2,212    |
|      向晚      |   28,262   |       17,983       |     175      |   2,461    |
|      贝拉      |   21,597   |       15,130       |      92      |   1,725    |
|      乃琳      |   16,759   |       5,506        |      40      |    556     |
| vtuber自由讨论 |   16,537   |       2,649        |      3       |     70     |
| asoul一个魂儿  |   14,938   |       1,801        |      23      |    215     |
|     贝贝珈     |   1,657    |       1,325        |      5       |     55     |

## 友情链接

+ [另一个仍在活跃更新的贴吧管理器（有用户界面）](https://github.com/dog194/TiebaManager)
+ [用户反馈（我的个人吧）](https://tieba.baidu.com/starry)
