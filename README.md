# Tieba-Manager

[![gitee](https://img.shields.io/badge/mirror-gitee-red)](https://gitee.com/Starry-OvO/Tieba-Manager)
[![release](https://img.shields.io/github/release/Starry-OvO/Tieba-Manager?color=blue&logo=github)](../../releases)
[![license](https://img.shields.io/github/license/Starry-OvO/Tieba-Manager?color=blue&logo=github)](LICENSE)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Starry-OvO/Tieba-Manager?logo=lgtm)](https://lgtm.com/projects/g/Starry-OvO/Tieba-Manager/context:python)

## 简介

`aiotieba`库是一个使用`aiohttp`实现的异步贴吧客户端，封装了下列实用接口并额外添加了一些数据库和图像处理功能以方便自动化的吧务管理

封装的官方接口包括

+ 按回复时间/发布时间/热门序获取贴吧主题帖/精华帖列表。支持获取带转发/投票/转发嵌套投票/各种卡片的主题帖信息
+ 获取带图片链接/小尾巴内容/点赞情况/用户信息（用户名/user_id/portrait/等级/性别/是否锁回复）/每条回复的前排楼中楼（支持按或不按点赞数排序）的回复列表
+ 获取带所有前述用户信息的楼中楼列表
+ 根据`用户名` `昵称` `portrait` `user_id`中的任一项反查其他用户信息，或通过用户主页的`tieba_uid`反查其他用户信息
+ 使用小吧主、语音小编的`BDUSS`删帖/屏蔽/封禁任意用户3天或10天
+ 使用已被大吧主分配解封/恢复/处理申诉权限的吧务`BDUSS`解封/恢复/处理申诉。支持一键拒绝所有解封申诉
+ 使用大吧主`BDUSS`推荐帖子到首页/移动帖子到指定分区/加精/撤精/置顶/撤置顶/添加黑名单/查看黑名单/取消黑名单
+ 获取用户主页信息/关注贴吧列表/屏蔽贴吧列表/关注用户列表/粉丝列表/发帖历史/回复历史
+ 获取贴吧最新关注用户列表/等级排行榜/吧务列表/吧详情
+ 使用`BDUSS`关注贴吧/取关贴吧/关注用户/取关用户/移除粉丝/屏蔽贴吧/取消屏蔽贴吧/签到/水帖/发送私信

额外功能包括

+ 数据库功能：缓存贴吧常量（如贴吧名到fid的映射关系）/为用户添加标记/为帖子或回复添加标记/为图像hash添加标记
+ 图像处理功能：图像解码/二维码解析/图像hash计算

在`aiotieba`的基础上，我开发了多种自动化吧务管理工具，如[云审查工具](wikis/cloud_review_introduction.md)和[指令管理器](../../wiki/%E6%8C%87%E4%BB%A4%E7%AE%A1%E7%90%86%E5%99%A8%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6)，以及一些[自动化脚本的案例](wikis/many_utils.md)

## 入门教程

+ 确保你的[`Python`](https://www.python.org/downloads/)版本在`3.9`及以上

+ 下载仓库并安装依赖

```bash
git clone https://github.com/Starry-OvO/Tieba-Manager.git
cd ./Tieba-Manager
pip install -r requirements.txt
```

+ **实操教程请参考**[aiotieba入门教程](wikis/tutorial.md)

## 若要启用云审查功能

+ 参考`config/config_full_example.toml`中的注释完成对`Database`字段的配置，你需要一个`MySQL`数据库用来缓存通过检测的内容id以及记录用户权限级别（黑、白名单）

+ 使用函数`Database.init_database(["贴吧名1", "贴吧名2"])`一键建库

+ 自定义审查行为：请参照我给出的例子自己编程修改[`cloud_review_hanime.py`](cloud_review_hanime.py)，这是被实际应用于[宫漫吧](https://tieba.baidu.com/f?ie=utf-8&kw=%E5%AE%AB%E6%BC%AB)的云审查工具

+ 运行`cloud_review_yours.py`（对`Windows`平台，建议使用`pythonw.exe`无窗口运行，对`Linux`平台，建议使用如下的`nohup`指令在后台运行）

```bash
nohup python cloud_review_yours.py >/dev/null 2>&1 &
```

## 友情链接

+ [另一个仍在活跃更新的贴吧管理器（有用户界面）](https://github.com/dog194/TiebaManager)
+ [用户反馈（我的个人吧）](https://tieba.baidu.com/f?ie=utf-8&kw=starry)

## 客户名单

云审查工具&指令管理器已在以下贴吧应用（2022.07.03更新，按启用时间先后排序）

|      吧名      | 关注用户数 | 最近29天日均访问量 | 日均主题帖数 | 日均回复数 |
| :------------: | :--------: | :----------------: | :----------: | :--------: |
| vtuber自由讨论 |   16,441   |       2,794        |      3       |     82     |
|     asoul      |  159,518   |       95,846       |     970      |   9,829    |
|      嘉然      |   54,676   |       27,148       |     237      |   3,495    |
|      宫漫      | 1,257,365  |       46,541       |     279      |   3,394    |
|    lol半价     | 1,945,812  |      151,266       |     516      |   8,880    |
|     孙笑川     | 2,008,794  |      540,728       |    5,974     |  159,059   |
|    新孙笑川    |  236,223   |       37,578       |     366      |   12,404   |
|      向晚      |   27,936   |       23,311       |     243      |   3,139    |
|      贝拉      |   21,354   |       15,549       |      81      |   1,533    |
|    王力口乐    |   12,842   |       42,705       |     432      |   5,890    |
|      乃琳      |   16,648   |       7,624        |      54      |    864     |
| asoul一个魂儿  |   15,038   |       3,710        |      49      |    542     |
|     贝贝珈     |   1,672    |       1,337        |      7       |     82     |
|    抗压背锅    | 3,698,726  |      945,436       |    2,410     |   70,454   |
