# Tieba-Cloud-Review
部署于Linux系统的百度贴吧云审查&循环封禁Python脚本
## 功能特点
### 优点
+ 以客户端版api为基础开发，这意味着小吧也可以封十天、拒绝申诉、解封和恢复删帖（需要大吧主分配权限）。
+ 得益于Python语言的强大扩展能力，脚本可以支持二维码识别、dhash等方法
+ 自定义修改函数，不再拘束于傻瓜式脚本的关键词组合判断，而是可以定义复杂的正则表达式，从用户等级/评论图片等等方面入手判断删帖与封禁条件

### 缺点
- 需要一定的Python&Linux编程基础
- 需要大量依赖项，脚本部署困难

## 环境部署

第一步环境部署对初学者而言极其困难，如果第一步你就做不下去建议放弃使用该脚本

+ 在任一目录里解包工程，目录示例: **/root/scripts/Tieba-Cloud-Review**

+ 配置MySQL，使用该脚本，你需要一个数据库用来缓存通过检测的回复的**pid**以及记录黑、白名单
        
+ pip安装需要的Python库
```
pip install pymysql
pip install lxml
pip install bs4
pip install pillow
sudo yum install zbar-devel
pip install pyzbar
```
+ 附加说明

    + 如果**zbar-devel**安装失败
    
        + 你可能需要安装一个第三方yum源
        + Raven源 <https://centos.pkgs.org/8/raven-x86_64/raven-release-1.0-1.el8.noarch.rpm.html>
        + 使用```rpm -Uvh xxx.rpm```来安装Raven源
        
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
