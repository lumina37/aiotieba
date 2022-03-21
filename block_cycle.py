# -*- coding:utf-8 -*-
import argparse
import asyncio
import json

import tiebaBrowser as tb

if __name__ == '__main__':

    async def main():

        parser = argparse.ArgumentParser(
            description='Block Tieba ID', allow_abbrev=False)
        parser.add_argument('--BDUSS_key', '-k',
                            type=str,
                            default='default',
                            help='用于获取BDUSS')
        parser.add_argument('--block_ctrl_filepath', '-bc',
                            type=str,
                            help='block_control.json的路径',
                            default='config/block_control.json',
                            metavar='FILEPATH')
        args = parser.parse_args()

        with open(args.block_ctrl_filepath, 'r', encoding='utf-8-sig') as block_ctrl_file:
            block_list = json.loads(block_ctrl_file.read())

        async with tb.Browser(args.BDUSS_key) as brow:

            for i, block in enumerate(block_list):
                user = tb.UserInfo()
                user.user_name = block.get('user_name', '')
                user.nick_name = block.get('nick_name', '')
                user.portrait = block.get('portrait', '')

                flag = await brow.block(block['tieba_name'], user,
                                        block['day'], block.get('reason', ''))
                if not flag:
                    block['reason'] = 'ERROR'

                block_list[i] = block

        with open(args.block_ctrl_filepath, 'w', encoding='utf-8-sig') as block_ctrl_file:
            json_str = json.dumps(block_list, ensure_ascii=False,
                                  indent=2, separators=(',', ':'))
            block_ctrl_file.write(json_str)

    asyncio.run(main())
