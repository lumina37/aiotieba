# -*- coding:utf-8 -*-
import argparse
import json

import tiebaBrowser

if __name__ == '__main__':

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

    try:
        with open(args.block_ctrl_filepath, 'r', encoding='utf-8-sig') as block_ctrl_file:
            block_list = json.loads(block_ctrl_file.read())
    except FileExistsError:
        tiebaBrowser.log.critical("block control json not exist! Please create it!")
        raise
    except AttributeError:
        tiebaBrowser.log.critical("Incorrect format of block_control.json!")
        raise

    brow = tiebaBrowser.Browser(args.BDUSS_key)

    for i, block in enumerate(block_list):
        user = tiebaBrowser.UserInfo()
        user.user_name = block.get('user_name', '')
        user.nick_name = block.get('nick_name', '')
        user.portrait = block.get('portrait', '')

        flag = True
        if user.user_name or user.nick_name or user.portrait:
            flag, user = brow.block(
                block['tieba_name'], user, block['day'], block.get('reason','null'))

        block['user_name'] = user.user_name
        block['nick_name'] = user.nick_name
        block['portrait'] = user.portrait
        if not flag:
            block['reason'] = 'ERROR'

        block_list[i] = block

    with open(args.block_ctrl_filepath, 'w', encoding='utf-8-sig') as block_ctrl_file:
        json_str = json.dumps(block_list, ensure_ascii=False,
                              indent=2, separators=(',', ':'))
        block_ctrl_file.write(json_str)

    brow.close()
