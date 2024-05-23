"""
Author: windzu windzu1@gmail.com
Date: 2023-09-09 18:58:55
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-09-10 15:38:38
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""

import ast
import os
from argparse import ArgumentParser

import yaml

from .capture import Capture


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        help="config path",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="rosbag file path",
    )
    parser.add_argument(
        "--topics",
        type=ast.literal_eval,
        default='["/lidar_points/fusion", "/lidar_points/top"]',
        help="specify topics to subscribe",
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default=".pcd",
        help="specify file suffix [default: .pcd]",
    )
    parser.add_argument(
        "--store_method",
        type=str,
        default="auto",  # auto or manual
        help="specify store method [default: auto]",
    )
    parser.add_argument(
        "--store_interval",
        type=int,
        default=0,
        help="specify store interval(ms) [default: 0], 0 means store all data",
    )
    parser.add_argument(
        "--store_dims",
        type=str,
        default="xyzi",
        help="specify dims to store [default: xyzi]",
    )
    parser.add_argument(
        "--store_path",
        type=str,
        default="./pcds",
        help="specify path to store pcds [default: ./pcds]",
    )

    args = parser.parse_args(argv)

    # param check
    # check if have config file
    if args.config:
        if not os.path.exists(args.config):
            print("config file is not exist")
            return args
        else:
            with open(args.config, "r") as f:
                config = yaml.safe_load(f)
                args.topics = config.get("topics", args.topics)
                args.suffix = config.get("suffix", args.suffix)
                args.store_dims = config.get("store_dims", args.store_dims)
                args.store_path = config.get("store_path", args.store_path)

    # check if have ros bag file
    if not args.file:
        print("ros bag file is not exist")
    elif not os.path.exists(args.file):
        print(f"{args.file} not exists")
    else:
        args.file = os.path.abspath(args.file)

    # check if store_method if valid
    if args.store_method not in ["auto", "manual"]:
        print("store_method is not valid")
        raise ValueError

    return args


def main(args, unknown):
    args = parse_args(unknown)

    capture = Capture(
        file=args.file,
        topics=args.topics,
        suffix=args.suffix,
        store_method=args.store_method,
        store_interval=args.store_interval,
        store_dims=args.store_dims,
        store_path=args.store_path,
    )
    capture.run()


if __name__ == "__main__":
    main()
