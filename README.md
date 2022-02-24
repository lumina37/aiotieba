# Tieba-Manager

百度贴吧管理器 / 爬虫工具 / 接口合集

## 功能特点

+ 优先使用app版贴吧接口，更新进度紧贴官方版本。部分接口为独家开源
+ 得益于Python语言的强大扩展能力，脚本可以支持二维码识别、dhash等方法
+ 自定义修改函数，不再拘束于傻瓜式脚本的关键词组合判断，而是可以定义复杂的正则表达式，从用户等级/评论图片等等方面入手判断删帖与封禁条件
+ 签到、回复、关注贴吧等摸鱼函数允许你边跑审查边水经验
+ 多样的爬虫函数，方便实现简易爬虫

## 基本环境部署

+ 确保你的Python版本在3.9及以上。脚本中包含了较新的类型检查功能

+ 在任一目录里解包工程，目录示例: **/root/scripts/Tieba-Manager**

+ 修改config/config.json，填入你的BDUSS

+ pip安装必需的Python库

```bash
pip install requests
pip install lxml
pip install bs4
pip install pymysql
pip install pillow
pip install opencv-contrib-python
```

## 若要开启云审查功能

+ 记得import tiebaBrowser.cloud_review以解锁云审查功能
+ 在config/config.json中配置MySQL连接。你需要一个数据库用来缓存通过检测的回复的**pid**以及记录黑、白名单用户
+ 在config/config.json中配置tieba_name_mapping。你需要为每个贴吧设置对应的英文名以方便建立数据库
+ 使用函数init_database一键建库
+ 自定义审查行为。请参照我给出的例子自己编程修改**cloud_review_asoul.py**，注释比较规范全面，请自行理解各api的功能

## 附加说明

+ config/config.json设置

  + BDUSS key（用于快速调用）:value（你的BDUSS）
  + MySQL 用于连接到数据库
  + tieba_name_mapping key（贴吧中文名）:value（自定义的贴吧英文名，建库时用得到）

+ 各第三方库的用途说明

  + **requests** 支持最基本的网络IO功能
  + **lxml** 支持BeautifulSoup以lxml格式解析HTML
  + **bs4** 解析HTML
  + **pymysql** 连接MySQL
  + **pillow** 提供解码gif图像的方法
  + **opencv-contrib-python** 提供图像哈希、定位解析二维码的方法

## 编写用于一键重启的bash脚本

给出我的脚本作为示例

```bash
#! /bin/bash
pids=`ps -ef | grep "cloud_review_.*py" | grep -v grep | awk '{print $2}'`
if [ -n "$pids" ]; then
    kill -15 $pids
fi
nohup /usr/bin/python /home/starry/Scripts/tieba/cloud_review_asoul.py -st 20 >/dev/null 2>&1 &
```

## 结束

至此，所有的配置工作已经完成

Enjoy :)
