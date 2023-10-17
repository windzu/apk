"""
Author: windzu windzu1@gmail.com
Date: 2023-09-11 01:09:34
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-09-11 01:11:06
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""


def bin2pcd_command(args, unknown):
    print("format bin2pcd command")
    from .bin2pcd import main as bin2pcd_main

    bin2pcd_main(args, unknown)


def pcd2bin_command(args, unknown):
    print("format pcd2bin command")
    from .pcd2bin import main as pcd2bin_main

    pcd2bin_main(args, unknown)


def add_arguments(parser):
    subparsers = parser.add_subparsers(title="format commands")

    # bin2pcd
    bin2pcd_parser = subparsers.add_parser("bin2pcd", help="format bin2pcd")
    bin2pcd_parser.set_defaults(func=bin2pcd_command)

    # pcd2bin
    pcd2bin_parser = subparsers.add_parser("pcd2bin", help="format pcd2bin")
    pcd2bin_parser.set_defaults(func=pcd2bin_command)
