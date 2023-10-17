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
    return args


def main(args, unknown):
    args = parse_args(unknown)

    capture = Capture(
        topics=args.topics,
        suffix=args.suffix,
        store_dims=args.store_dims,
        store_path=args.store_path,
    )
    capture.run()


if __name__ == "__main__":
    main()
