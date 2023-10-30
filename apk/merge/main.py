"""
Author: wind windzu1@gmail.com
Date: 2023-09-08 09:53:06
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-09-08 13:07:43
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""


def bag_command(args, unknown):
    print("merge bag command")
    from .merge_bag import main as bag_main

    bag_main(args, unknown)


def record_command(args, unknown):
    print("merge record command")
    from .merge_record import main as record_main

    record_main(args, unknown)


def add_arguments(parser):
    subparsers = parser.add_subparsers(title="capture commands")

    # bag
    bag_parser = subparsers.add_parser("bag", help="merge bags")
    bag_parser.set_defaults(func=bag_command)

    # record
    record_parser = subparsers.add_parser("record", help="merge records")
    record_parser.set_defaults(func=record_command)
