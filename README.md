# Tieba-Cloud-Review
部署于Linux系统的百度贴吧云审查&循环封禁Python脚本
## 功能特点
### 优点
+ 以网页版贴吧和部分客户端版本的api为基础开发
+ 支持新旧两个版本的封禁api，可以对无用户名用户进行循环
+ 得益于Python语言的强大扩展能力，脚本可以支持二维码识别
+ 自定义修改函数，不再拘束于傻瓜式脚本的关键词组合判断，而是可以定义复杂的正则表达式，从用户等级/评论图片等等方面入手判断删帖与封禁条件

### 缺点
- 需要一定的Python&Linux编程基础
- 需要大量依赖项，脚本部署困难

## 环境部署

第一步环境部署对初学者而言极其困难，如果第一步你就做不下去建议放弃使用该脚本

+ 下载压缩包并在任一目录里解包，目录示例: **/root/scripts/tieba**

+ 配置MySQL，使用该脚本，你需要一个数据库用来缓存通过检测的回复的**pid**以及记录黑、白名单
        
+ pip安装需要的Python库
```
sudo pip3 install mysql-connector
sudo pip3 install lxml
sudo pip3 install bs4
sudo pip3 install pillow
sudo yum install zbar-devel
sudo pip3 install pyzbar
```
+ 附加说明

    + 如果**zbar-devel**安装失败
    
        + 你可能需要安装一个第三方yum源
        + Raven源 <https://centos.pkgs.org/8/raven-x86_64/raven-release-1.0-1.el8.noarch.rpm.html>
        + 使用```rpm -Uvh xxx.rpm```来安装Raven源
        
    + 各第三方库的用途说明
    
        + **mysql-connector** 连接MySQL
        + **lxml** 用于BeautifulSoup解析
        + **bs4** BeautifulSoup解析HTML
        + **pillow** 图像库
        + **zbar-devel** 二维码检测的底层支持代码
        + **pyzbar** 它是zbar的一个Python封装
        
## config/config.json设置
+ BDUSS key（用于快速调用）:value（你的BDUSS）
+ MySQL 用于连接到数据库
+ tieba_name_mapping key（贴吧中文名）:value（自定义的贴吧英文名，建库时用得到）
    
## 自定义审查行为
请参照我给出的例子自己编程修改**cloud_review_soulknight.py**，注释比较规范全面，请自行理解各api的功能

## 设置定时任务
给出我的crontab设置作为示例
```
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=""
25 0 * * * . /etc/profile; python /.../block_cycle.py -bc /.../block_cycle_1.json
0 0 */3 * * . /etc/profile; python /.../block_cycle.py -bc /.../user_control/block_cycle_10.json
*/6 6-23,0 * * * . /etc/profile; python /.../cloud_review.py
*/20 1-5 * * * . /etc/profile; python /.../cloud_review.py
```

## 结束
至此，所有的配置工作已经完成

**Enjoy :)**
