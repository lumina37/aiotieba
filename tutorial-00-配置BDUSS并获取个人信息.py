"""
本例中，你将学会config.toml配置文件的基本填写方法，并使用aiotieba库获取贴吧账号的个人信息

第一步
运行该教程脚本，出现错误提示: "Failed to login. reason:用户名或密码错误"
此时aiotieba将在该教程脚本的同一目录下自动生成配置文件夹config以及对应的配置示例

第二步
找到并打开配置文件夹config，打开里面的config.toml文件并按提示在相应位置填入你的BDUSS
不知道BDUSS是什么的，这个教程不适合你，建议另找更适合小白的工具

第三步
填好BDUSS后再次运行该教程脚本，成功获取用户个人信息
"""

import asyncio

import aiotieba as tb


async def main():
    # 使用键名"default"对应的BDUSS创建客户端
    async with tb.Client("default") as brow:
        # 通过在协程brow.get_self_info前添加await来等待它执行完毕，该协程返回的用户信息会被填入变量user
        user = await brow.get_self_info()

    # 将获取的信息打印到日志
    tb.LOG.info(f"当前用户信息: {user}")


# 执行协程main
# 参考https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio.run
asyncio.run(main())
