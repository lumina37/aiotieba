# Tieba-Manager
百度贴吧Python脚本管理器
## 功能特点
+ 全面采用app版贴吧接口。大量接口为独家开源
+ 得益于Python语言的强大扩展能力，脚本可以支持二维码识别、dhash等方法
+ 自定义修改函数，不再拘束于傻瓜式脚本的关键词组合判断，而是可以定义复杂的正则表达式，从用户等级/评论图片等等方面入手判断删帖与封禁条件


## 环境部署

+ 在任一目录里解包工程，目录示例: **/root/scripts/Tieba-Manager**

+ 配置MySQL，使用该脚本，你需要一个数据库用来缓存通过检测的回复的**pid**以及记录黑、白名单
        
+ pip安装需要的Python库
```
pip install pymysql
pip install lxml
pip install bs4
pip install pillow
pip install imagehash
yum install zbar-devel
pip install pyzbar
```
+ 附加说明
        
    + 各第三方库的用途说明
    
        + **pymysql** 连接MySQL
        + **lxml** 用于BeautifulSoup解析
        + **bs4** BeautifulSoup解析HTML
        + **pillow** 图像库
        + **zbar-devel** 二维码检测的支持库
        + **pyzbar** 它是zbar的一个Python封装
        
## config/config.json设置
+ BDUSS key（用于快速调用）:value（你的BDUSS）
+ MySQL 用于连接到数据库
+ tieba_name_mapping key（贴吧中文名）:value（自定义的贴吧英文名，建库时用得到）
    
## 自定义审查行为
请参照我给出的例子自己编程修改**cloud_review_asoul.py**，注释比较规范全面，请自行理解各api的功能

## 编写重启脚本
给出我的脚本作为示例
```
#! /bin/bash
pids=`ps -ef | grep "cloud_review_.*py" | grep -v grep | awk '{print $2}'`
if [ -n "$pids" ]; then
    kill -15 $pids
fi
nohup /usr/bin/python /home/starry/Scripts/tieba/cloud_review_asoul.py -st 20 >/dev/null 2>&1 &
```

## 结束
至此，所有的配置工作已经完成

**Enjoy :)**
