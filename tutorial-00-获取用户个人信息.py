"""
本例中，你将学会如何使用aiotieba库获取贴吧个人信息

第一步
运行该教程脚本，出现错误提示：用户名或密码错误，无法获取个人信息
此时aiotieba将在该教程脚本的同一目录下自动生成配置文件夹config以及对应的配置示例

第二步
找到并打开配置文件夹.../Tieba-Manager/config，打开config.yaml文件并按提示在相应位置填入你的BDUSS

第三步
填好BDUSS后再次运行该教程脚本，成功获取用户个人信息
"""

import asyncio

import aiotieba as tb


async def main():
    async with tb.Client("default") as brow:
        user = await brow.get_self_info()

    tb.log.info(f"当前用户信息: {user}")


asyncio.run(main())
