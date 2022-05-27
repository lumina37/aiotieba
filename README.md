# Tieba-Manager

[![gitee](https://img.shields.io/badge/mirror-gitee-red)](https://gitee.com/Starry-OvO/Tieba-Manager)
[![release](https://img.shields.io/github/release/Starry-OvO/Tieba-Manager?color=blue&logo=github)](https://github.com/Starry-OvO/Tieba-Manager/releases)
[![license](https://img.shields.io/github/license/Starry-OvO/Tieba-Manager?color=blue&logo=github)](https://github.com/Starry-OvO/Tieba-Manager/blob/main/LICENSE)
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
+ 使用`BDUSS`关注吧/关注用户/取关用户/移除粉丝/签到/水帖/发送私信

## 准备使用

+ 确保你的[`Python`](https://www.python.org/downloads/)版本在`3.8`及以上

+ 拉取代码并安装依赖

```bash
git clone https://github.com/Starry-OvO/Tieba-Manager.git
cd ./Tieba-Manager
pip install -r requirements.txt
```

+ 修改`config/config-example.yaml`，填入你的`BDUSS`，将文件名修改为`config.yaml`

```yaml
BDUSS:
  default: ABCDEFGai2LdUd5TTVHblhFeXoxdGyOVURGUE1OYzNqVXVRaWF-HnpGckRCNFJnRVFBQUFBJCQAAAAAAAAAAAEAAADiglQb0f3Osqmv0rbJ2QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMN6XGDDelxgc
```

## 尝试一下

```python
import asyncio

import tiebaBrowser as tb


async def main():
    # 使用键名"default"对应的BDUSS创建客户端
    async with tb.Browser("default") as brow:
        # 同时请求用户个人信息和asoul吧首页前30帖
        # asyncio.gather会为两个协程brow.get_self_info和brow.get_threads自动创建任务然后“合并”为一个协程
        # await释放当前协程持有的CPU资源并等待协程asyncio.gather执行完毕
        # 参考https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio.gather
        user, threads = await asyncio.gather(brow.get_self_info(), brow.get_threads('asoul'))

    # 将获取的信息打印到日志
    tb.log.info(f"当前用户信息: {user}")
    for thread in threads:
        tb.log.info(f"tid: {thread.tid} 最后回复时间戳: {thread.last_time} 标题: {thread.title}")


# 执行协程main
# 参考https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio.run
asyncio.run(main())
```

## 若要开启云审查功能

+ 在`config/config.yaml`中：配置`database`字段，你需要一个`MySQL`数据库用来缓存通过检测的内容id以及记录用户权限级别（黑、白名单）；配置`fname_zh2en`字段，你需要为每个贴吧设置对应的英文名以方便建立数据库
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

import tiebaBrowser as tb


async def main():
    # 使用空字符串构造审查器
    async with tb.Reviewer('', '') as brow:
        # 使用函数Database.init_database()一键建库
        await brow.database.init_database()

asyncio.run(main())
```

+ 自定义审查行为：请参照我给出的例子自己编程修改[`cloud_review_hanime.py`](https://github.com/Starry-OvO/Tieba-Manager/blob/main/cloud_review_hanime.py)，这是被实际应用于[宫漫吧](https://tieba.baidu.com/f?ie=utf-8&kw=%E5%AE%AB%E6%BC%AB)的云审查工具
+ 运行`cloud_review_yours.py`。对`Windows`平台，建议使用`pythonw.exe`无窗口运行，对`Linux`平台，建议使用如下的`nohup`指令在后台运行

```bash
nohup python cloud_review_yours.py >/dev/null 2>&1 &
```

## 友情链接

+ [百度贴吧接口合集](https://github.com/Starry-OvO/Tieba-Manager/blob/main/tiebaBrowser/_api.py)
+ [云审查案例](https://github.com/Starry-OvO/Tieba-Manager/blob/main/cloud_review_hanime.py)
+ [指令管理器](https://github.com/Starry-OvO/Tieba-Manager/wiki/%E6%8C%87%E4%BB%A4%E7%AE%A1%E7%90%86%E5%99%A8%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6)
+ [另一个仍在活跃更新的贴吧管理器（有用户界面）](https://github.com/dog194/TiebaManager)
+ [用户反馈（我的个人吧）](https://tieba.baidu.com/f?ie=utf-8&kw=starry)

## 用户名单

云审查工具&指令管理器已在以下贴吧应用（2022.05.27更新，按启用时间先后排序）

|      吧名      | 关注用户数 | 最近29天日均访问量 | 日均主题帖数 | 日均回复数 |
| :------------: | :--------: | :----------------: | :----------: | :--------: |
| vtuber自由讨论 |   16,230   |       3,842        |      4       |    125     |
|     asoul      |  160,200   |      278,228       |    2,547     |   30,344   |
|      嘉然      |   52,884   |       26,603       |     278      |   3,738    |
|      宫漫      | 1,228,526  |       54,140       |     331      |   4,191    |
|    lol半价     | 1,929,451  |      157,847       |     522      |   9,940    |
|     孙笑川     | 1,843,333  |      499,688       |    5,452     |  147,333   |
|      向晚      |   26,599   |       23,235       |     276      |   3,366    |
|      贝拉      |   20,944   |       22,203       |     162      |   2,913    |
|    王力口乐    |   10,808   |       40,972       |     534      |   6,570    |
|      乃琳      |   16,212   |       11,534       |      82      |   1,420    |
| asoul一个魂儿  |   15,154   |       4,797        |      79      |   1,293    |
