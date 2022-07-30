# 云审查

## 这是什么？

这是一个以`aiotieba`为基础开发的自动扫描并处理首页违规信息的管理工具

**它可以极大节约吧务人工巡逻的时间成本**

## 使用方法

+ 参考`config/config_full_example.toml`中的注释完成对`Database`字段的配置，你需要一个`MySQL`数据库用来缓存通过检测的内容id以及记录用户权限级别（黑、白名单）

+ 使用函数`Database.init_database(["贴吧名1", "贴吧名2"])`一键建库

+ 自定义审查行为：请参照我给出的例子自己编程修改[`cloud_review_vtuber.py`](../cloud_review_vtuber.py)，这是被实际应用于[vtuber吧](https://tieba.baidu.com/vtuber)的云审查工具

+ 运行`cloud_review_yours.py`（对`Windows`平台，建议使用`pythonw.exe`无窗口运行，对`Linux`平台，建议使用如下的`nohup`指令在后台运行）

```bash
nohup python cloud_review_yours.py >/dev/null 2>&1 &
```

## 扫描范围

在我给出的范例[`cloud_review_vtuber.py`](../cloud_review_vtuber.py)中，每一轮扫描都会覆盖vtuber吧首页**按回复时间顺序**的前**30个**`主题帖`；以及这些`主题帖`中最新的**30条**`回复`；以及上述所有`回复`中点赞数最高的前**10条**`楼中楼`内容

云审查工具可以检查以上内容中是否存在：

+ **违规图片**

![eg_1](https://user-images.githubusercontent.com/48282276/176145251-35f36f73-2f23-4b1f-a456-9e62f97c40af.png)

+ **违规链接**

![eg_2](https://user-images.githubusercontent.com/48282276/176145401-6b16140c-53cb-4575-9f9a-4b47540bd5a5.png)

+ **违规文字**

![eg_3](https://user-images.githubusercontent.com/48282276/176145434-d8deab64-3ceb-472b-b51d-564246162226.png)

+ **黑名单用户**

![eg_4](https://user-images.githubusercontent.com/48282276/176145443-2021e697-c858-48c3-91b4-fba409ef6e20.png)

## 实战效果

以下是应用于[`孙笑川吧`](https://tieba.baidu.com/f?ie=utf-8&kw=%E5%AD%99%E7%AC%91%E5%B7%9D)的云审查工具的实战效果。

![backstage](https://user-images.githubusercontent.com/48282276/165777398-47e00f26-a46f-4b7c-a03e-03092e5d31ba.png)

![log](https://user-images.githubusercontent.com/48282276/165776593-ab5feec4-6529-4702-82e5-1904e9e8630f.png)

## 性能测试
**测试时间**: 2022.03.30<br>
**硬件配置**: **CPU** Intel Xeon Platinum 8163 2.50GHz / **带宽** 1Mbps<br>
**扫描间隔**: 10秒<br>
**吧活跃度**: 近29天日均新增回复15977条<br>
10次扫描平均耗时 **1.252秒**

![benchmark](https://user-images.githubusercontent.com/48282276/160804519-f71a1e8d-5d9a-49a1-aac8-7119b1af5105.png)
