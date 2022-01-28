# -*- coding:utf-8 -*-
import argparse
import csv
import os
import re
import sys
import time

import imagehash

import tiebaBrowser

PATH = os.path.split(os.path.realpath(sys.argv[0]))[0]


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='MySQL操作', allow_abbrev=False)
    parser.add_argument('tieba_name',
                        type=str,
                        help='贴吧名')
    parser.add_argument('-id', '-i',
                        type=str,
                        help='用户id')
    parser.add_argument('-img',
                        type=str,
                        help='图像id')
    parser.add_argument('--post_id', '-p',
                        type=int,
                        help='白名单pid')

    parser.add_argument('--search', '-s',
                        action='store_true',
                        help='是否查询状态')
    parser.add_argument('--flag', '-f',
                        action='store_true',
                        help='是否设置为true')
    parser.add_argument('--delete', '-d',
                        action='store_true',
                        help='是否从表中删除')

    parser.add_argument('--delete_new', '-dn',
                        type=int,
                        help='是否删除最近n小时的pid记录',
                        metavar='HOUR')
    args = parser.parse_args()

    brow = tiebaBrowser.CloudReview('default', args.tieba_name)

    if args.delete_new:
        brow.mysql.del_pids(args.tieba_name, args.delete_new)

    if args.id:
        if args.delete:
            brow.del_user_id(args.id)
        elif args.search:
            user = tiebaBrowser.UserInfo(args.id)
            user = brow.get_userinfo_weak(user)
            print(brow.mysql.is_user_id_white(args.tieba_name, user.user_id))
        else:
            brow.update_user_id(args.id, args.flag)

    if args.img:
        img_url = f"http://tiebapic.baidu.com/forum/pic/item/{args.img}.jpg"
        try:
            image = brow.url2image(
                f"http://tiebapic.baidu.com/forum/pic/item/{args.img}.jpg")
            img_hash = str(imagehash.dhash(image))
        except Exception as err:
            brow.log.error(f"Failed to get dhash of {args.img}. reason:{err}")
        else:
            if args.delete:
                brow.mysql.del_img_hash(args.tieba_name, img_hash)
            elif args.search:
                print(brow.mysql.has_img_hash(args.tieba_name, img_hash))
            else:
                brow.mysql.add_img_hash(args.tieba_name, img_hash, args.img)

    if args.post_id:
        if args.delete:
            brow.mysql.del_pid(args.tieba_name, args.post_id)
        elif args.search:
            print(brow.mysql.has_pid(args.tieba_name, args.post_id))
        else:
            brow.mysql.add_pid(args.tieba_name, args.post_id)

    brow.close()
