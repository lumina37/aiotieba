# Tieba-Manager

[![gitee](https://img.shields.io/badge/mirror-gitee-red)](https://gitee.com/Starry-OvO/Tieba-Manager)
[![release](https://img.shields.io/github/release/Starry-OvO/Tieba-Manager?color=blue&logo=github)](https://github.com/Starry-OvO/Tieba-Manager/releases)
[![license](https://img.shields.io/github/license/Starry-OvO/Tieba-Manager?color=blue&logo=github)](https://github.com/Starry-OvO/Tieba-Manager/blob/master/LICENSE)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Starry-OvO/Tieba-Manager?logo=lgtm)](https://lgtm.com/projects/g/Starry-OvO/Tieba-Manager/context:python)

## 功能概览

+ 按回复时间/发布时间/热门序获取贴吧主题帖/精华帖列表。支持获取带转发/投票/转发嵌套投票/各种卡片的主题帖信息
+ 获取带图片链接/小尾巴内容/点赞情况/用户信息（用户名/user_id/portrait/等级/性别/是否锁回复）/每条回复的前排楼中楼（支持按或不按点赞数排序）的回复列表
+ 获取带所有前述用户信息的楼中楼列表
+ 根据`用户名` `昵称` `portrait` `user_id`中的任一项反查其他用户信息
+ 使用小吧主、语音小编的`BDUSS`删帖/屏蔽/封禁任意用户3天或10天
+ 使用已被大吧主分配解封/恢复/处理申诉权限的吧务`BDUSS`解封/恢复/处理申诉。支持一键拒绝所有解封申诉
+ 使用大吧主`BDUSS`推荐帖子到首页/移动帖子到指定分区/加精/撤精/置顶/撤置顶/添加黑名单/查看黑名单/取消黑名单
+ 获取用户主页信息/关注贴吧列表/关注用户列表/粉丝列表/发帖历史/回复历史
+ 获取贴吧最新关注用户列表/等级排行榜/吧务列表/吧详情
+ 使用`BDUSS`关注贴吧/取关贴吧/关注用户/取关用户/移除粉丝/签到/水帖/发送私信

## 入门使用

+ 确保你的[`Python`](https://www.python.org/downloads/)版本在`3.8`及以上

+ 拉取代码并安装依赖

```bash
git clone https://github.com/Starry-OvO/Tieba-Manager.git
cd ./Tieba-Manager
pip install -r requirements.txt
```

+ 依序运行教程脚本`tutorial-*.py`，参考注释学习用法

## 若要开启云审查功能

+ 参考`config/config_full_example.yaml`中的注释完成对以下字段的配置：`database`字段，你需要一个`MySQL`数据库用来缓存通过检测的内容id以及记录用户权限级别（黑、白名单）；`fname_zh2en`字段，你需要为每个贴吧设置对应的英文名以方便建立数据库
+ 对于[宫漫吧](https://tieba.baidu.com/f?ie=utf-8&kw=%E5%AE%AB%E6%BC%AB)，配置完成的`config/config.yaml`如下所示

```yaml
BDUSS:
  starry: ABCDEFGai2LdUd5TTVHblhFeXoxdGyOVURGUE1OYzNqVXVRaWF-HnpGckRCNFJnRVFBQUFBJCQAAAAAAAAAAAEAAADiglQb0f3Osqmv0rbJ2QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMN6XGDDelxgc

database:
  host: 127.0.0.1
  port: 3306
  user: root
  password: 123456

fname_zh2en:
  宫漫: hanime
```

+ 使用函数`Database.init_database()`一键建库，如下例所示

```python
import asyncio

import aiotieba as tb


async def main():
    # 构造空审查器
    async with tb.Reviewer() as brow:
        # 使用函数Database.init_database()一键建库
        await brow.database.init_database()

asyncio.run(main())
```

+ 自定义审查行为：请参照我给出的例子自己编程修改[`cloud_review_hanime.py`](https://github.com/Starry-OvO/Tieba-Manager/blob/master/cloud_review_hanime.py)，这是被实际应用于[宫漫吧](https://tieba.baidu.com/f?ie=utf-8&kw=%E5%AE%AB%E6%BC%AB)的云审查工具
+ 运行`cloud_review_yours.py`。对`Windows`平台，建议使用`pythonw.exe`无窗口运行，对`Linux`平台，建议使用如下的`nohup`指令在后台运行

```bash
nohup python cloud_review_yours.py >/dev/null 2>&1 &
```

## 友情链接

+ [百度贴吧接口合集](https://github.com/Starry-OvO/Tieba-Manager/blob/master/aiotieba/client.py)
+ [云审查案例](https://github.com/Starry-OvO/Tieba-Manager/blob/master/cloud_review_hanime.py)
+ [指令管理器](https://github.com/Starry-OvO/Tieba-Manager/wiki/%E6%8C%87%E4%BB%A4%E7%AE%A1%E7%90%86%E5%99%A8%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6)
+ [另一个仍在活跃更新的贴吧管理器（有用户界面）](https://github.com/dog194/TiebaManager)
+ [用户反馈（我的个人吧）](https://tieba.baidu.com/f?ie=utf-8&kw=starry)

## 用户名单

云审查工具&指令管理器已在以下贴吧应用（2022.05.29更新，按启用时间先后排序）

|      吧名      | 关注用户数 | 最近29天日均访问量 | 日均主题帖数 | 日均回复数 |
| :------------: | :--------: | :----------------: | :----------: | :--------: |
| vtuber自由讨论 |   16,239   |       3,829        |      4       |    118     |
|     asoul      |  160,193   |      292,162       |    2,664     |   32,300   |
|      嘉然      |   53,082   |       31,627       |     311      |   4,453    |
|      宫漫      | 1,229,541  |       53,259       |     322      |   4,004    |
|    lol半价     | 1,931,698  |      150,617       |     497      |   9,234    |
|     孙笑川     | 1,855,993  |      495,958       |    5,428     |  144,914   |
|      向晚      |   26,867   |       27,837       |     332      |   4,155    |
|      贝拉      |   20,974   |       23,763       |     167      |   3,033    |
|    王力口乐    |   11,070   |       44,291       |     544      |   6,687    |
|      乃琳      |   16,267   |       12,427       |      84      |   1,511    |
| asoul一个魂儿  |   15,148   |       5,449        |      88      |   1,431    |
