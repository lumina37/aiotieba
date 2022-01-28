# -*- coding:utf-8 -*-
import argparse
import os
import re

import tiebaBrowser
from tiebaBrowser.data_structure import UserInfo

PATH = os.path.split(os.path.realpath(__file__))[0]


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='ADMIN OPERATION', allow_abbrev=False)

    parser.add_argument('tieba_name',
                        type=str,
                        help='需要执行大吧主操作的目标贴吧吧名')
    parser.add_argument('--BDUSS_key', '-k',
                        type=str,
                        default='default',
                        help='用于获取BDUSS')

    parser.add_argument('--block', '-b',
                        type=str,
                        nargs='+',
                        help='待封10天的id',
                        metavar='STR')
    parser.add_argument('--unblock', '-u',
                        type=str,
                        nargs='+',
                        help='待解封的id',
                        metavar='STR')
    parser.add_argument('--recover', '-r',
                        type=str,
                        help='待恢复帖子的链接',
                        metavar='URL')
    parser.add_argument('--delete', '-d',
                        type=int,
                        help='待删除帖子的tid',
                        metavar='TID')
    parser.add_argument('--hide', '-hd',
                        type=int,
                        help='待屏蔽帖子的tid',
                        metavar='TID')
    parser.add_argument('--unhide', '-uh',
                        type=int,
                        help='待解除屏蔽帖子的tid',
                        metavar='TID')
    parser.add_argument('--blacklist_add', '-ba',
                        type=str,
                        nargs='+',
                        help='待加黑名单的id列表',
                        metavar='ID')
    parser.add_argument('--blacklist_cancel', '-bc',
                        type=str,
                        nargs='+',
                        help='待解黑名单的id列表',
                        metavar='ID')

    parser.add_argument('--recommend', '-rc',
                        type=int,
                        nargs='+',
                        help='待推荐帖子的tid列表',
                        metavar='TID')

    parser.add_argument('--refuse_appeals', '-ra',
                        action='store_true',
                        help='是否拒绝所有申诉')

    args = parser.parse_args()
    tieba_name = args.tieba_name
    brow = tiebaBrowser.Browser(args.BDUSS_key)

    if args.block:
        for id in args.block:
            brow.block(tieba_name, UserInfo(id), day=10)

    if args.unblock:
        for id in args.unblock:
            brow.unblock(tieba_name, id)

    if args.recover:
        tid_raw = re.search('(/p/|tid=|thread_id=)(\d+)', args.recover)
        tid = int(tid_raw.group(2)) if tid_raw else 0
        pid_raw = re.search('(pid|post_id)=(\d+)', args.recover)
        pid = int(pid_raw.group(2)) if pid_raw else 0
        brow.recover(tieba_name, tid, pid)

    if args.delete:
        brow.del_thread(tieba_name, args.delete, is_frs_mask=False)
    if args.hide:
        brow.del_thread(tieba_name, args.hide, is_frs_mask=True)
    if args.unhide:
        brow.recover(tieba_name, args.unhide, is_frs_mask=True)

    if args.blacklist_add:
        for id in args.blacklist_add:
            brow.blacklist_add(tieba_name, id)

    if args.blacklist_cancel:
        brow.blacklist_cancels(tieba_name, args.blacklist_cancel)

    if args.recommend:
        for tid in args.recommend:
            brow.recommend(tieba_name, tid)

    if args.refuse_appeals:
        brow.refuse_appeals(tieba_name)

    brow.close()
