# Tieba-Manager

[![license](https://badgen.net/github/license/Starry-OvO/Tieba-Manager?icon=github)](https://github.com/Starry-OvO/Tieba-Manager/blob/main/LICENSE)
[![release](https://badgen.net/github/release/Starry-OvO/Tieba-Manager?icon=github)](https://github.com/Starry-OvO/Tieba-Manager/releases)

## 工具链接

+ [百度贴吧接口合集](https://github.com/Starry-OvO/Tieba-Manager/blob/main/tiebaBrowser/_api.py#L393)
+ [云审查案例](https://github.com/Starry-OvO/Tieba-Manager/blob/main/cloud_review_soulknight.py)
+ [指令管理器](https://github.com/Starry-OvO/Tieba-Manager/blob/main/admin_listen.py)
+ [爬虫案例](https://github.com/Starry-OvO/Tieba-Manager/blob/main/spider.py)
+ [另一个仍在活跃更新的贴吧管理器（有用户界面 仅限Windows平台）](https://github.com/dog194/TiebaManager)

## 功能概览

+ 按回复时间/发布时间/热门序获取贴吧主题帖/精华帖列表。支持获取带转发/投票/转发嵌套投票/各种卡片的主题帖信息，支持`页码`翻页
+ 获取带图片链接、小尾巴内容、点赞情况、用户信息（`用户名` `user_id` `portrait` `等级` `性别` `是否锁回复` `是否vip` `是否大神`）、每条回复的前排楼中楼（参数支持按`点赞数`排序）的回复列表，支持`页码`翻页
+ 获取带所有前述用户信息的楼中楼列表，支持`页码`翻页
+ 根据`用户名` `昵称` `portrait` `user_id`中的任一项反查其他用户信息
+ 使用小吧主、语音小编的`BDUSS`封禁用户3/10天，支持对无`用户名`用户的封禁
+ 使用已被大吧主分配解封/恢复帖权限的吧务`BDUSS`解封/恢复帖
+ 使用吧务`BDUSS`拒绝所有申诉
+ 使用小吧主、语音小编的`BDUSS`删帖（也可以屏蔽）
+ 使用大吧主`BDUSS`推荐帖子到首页、移动帖子到指定分区、加精、撤精、置顶、撤置顶、添加黑名单、查看黑名单、取消黑名单
+ 获取用户主页信息、关注贴吧列表（包含等级、经验值信息）
+ 获取贴吧最新关注用户列表、等级排行榜
+ 使用`BDUSS`关注吧、签到吧、回帖

## 功能特点

+ 优先使用最新版贴吧app（12.22.0.3）的接口实现功能
+ 优先使用最新版贴吧app使用的[`Google Protocol Buffer (Protobuf)`](https://developers.google.cn/protocol-buffers)协议序列化网络请求&响应数据
+ 使用[`aiohttp`](https://github.com/aio-libs/aiohttp)作为网络库，所有涉及网络IO的函数均支持异步
+ 得益于[`Python`](https://www.python.org/downloads)语言的强大扩展能力，云审查管理器支持二维码识别、图像phash等功能
+ 极高的功能自由度，可以自定义复杂的正则表达式，可以从用户等级/评论图片/小尾巴内容等等方面入手判断删帖与封禁条件
+ 签到、回复、关注贴吧等摸鱼函数允许你边跑审查边水经验
+ 额外的爬虫函数，方便实现简易爬虫

## 基本环境部署

+ 确保你的[`Python`](https://www.python.org/downloads/)版本为3.9+，因为脚本中包含了较新的类型检查功能

+ 拉取代码

```bash
git clone https://github.com/Starry-OvO/Tieba-Manager.git
```

+ 修改`config/config.json`，填入你的`BDUSS`

+ `pip`安装必需的`Python`库

```bash
pip install asyncio
pip install aiohttp[speedups]
pip install lxml
pip install bs4
pip install pymysql
pip install pillow
pip install opencv-contrib-python
pip install protobuf
```

## 尝试一下

```python
# -*- coding:utf-8 -*-
import asyncio

import tiebaBrowser as tb


async def main():
    # 创建客户端，使用的BDUSS对应到键名"default"
    async with tb.Browser("default") as brow:
        # 同时请求用户个人信息和asoul吧首页前30帖
        # asyncio.gather会为两个协程brow.get_self_info和brow.get_threads自动创建任务然后“合并”为一个协程
        # await释放当前协程持有的CPU资源并等待协程asyncio.gather执行完毕
        # 参考https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio.gather
        user, threads = await asyncio.gather(brow.get_self_info(), brow.get_threads('asoul'))

        # 同步输出
        print(f"当前用户信息:{user}")
        for thread in threads:
            print(
                f"tid:{thread.tid} 最后回复时间戳:{thread.last_time} 标题:{thread.title}")

# 执行协程main
# 参考https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio.run
asyncio.run(main())
```

## 若要开启云审查功能

+ 在`config/config.json`中配置`MySQL`字段。你需要一个数据库用来缓存通过检测的回复的pid以及记录黑、白名单用户
+ 在`config/config.json`中配置`tieba_name_mapping`字段。你需要为每个贴吧设置对应的英文名以方便建立数据库
+ 使用函数[`MySQL.init_database()`](https://github.com/Starry-OvO/Tieba-Manager/blob/b887e670dba0323b54e6ca4955962778bd34c3a9/tiebaBrowser/mysql.py#L54)一键建库
+ 自定义审查行为：请参照我给出的例子自己编程修改[`cloud_review_soulknight.py`](https://github.com/Starry-OvO/Tieba-Manager/blob/main/cloud_review_soulknight.py)，这是被实际应用于[`元气骑士吧`](https://tieba.baidu.com/f?ie=utf-8&kw=%E5%85%83%E6%B0%94%E9%AA%91%E5%A3%AB)的云审查脚本，注释比较规范全面，请自行理解各api的功能

## 附加说明

+ config/config.json设置

  + `BDUSS_key`（用于快捷调出`BDUSS`）->`value`（你的`BDUSS`的实际值）
  + `MySQL` 配置用于连接到数据库的`ip` `port` `user_name` `password`等信息
  + `tieba_name_mapping` `tieba_name`（贴吧中文名）->`tieba_name_eng`（自定义的贴吧英文名，建库时用得到）

+ 各第三方库的用途说明

  + **asyncio** 支持`Python`协程相关功能
  + **aiohttp** 支持网络IO（异步）
  + **lxml** 支持HTML格式解析
  + **bs4** 解析HTML
  + **pymysql** 连接MySQL
  + **pillow** 提供解码gif图像的方法
  + **opencv-contrib-python** 提供图像哈希、定位解析二维码的方法
  + **protobuf** 支持以proto格式序列化网络请求和反序列化响应

## 编写用于一键重启的bash脚本

给出我的脚本`restart.sh`作为示例。需要重启时就`bash restart.sh`就行了

```bash
#! /bin/bash
pids=`ps -ef | grep "\.py" | grep -v grep | awk '{print $2}'`
if [ -n "$pids" ]; then
    kill $pids
fi

TIEBA_MANAGER_PATH="$HOME/Scripts/Tieba-Manager"
nohup python $TIEBA_MANAGER_PATH/admin_listen.py >/dev/null 2>&1 &
nohup python $TIEBA_MANAGER_PATH/cloud_review_soulknight.py >/dev/null 2>&1 &
nohup python $TIEBA_MANAGER_PATH/cloud_review_asoul.py >/dev/null 2>&1 &
```

## 结束

至此，所有的配置工作已经完成

Enjoy :)
