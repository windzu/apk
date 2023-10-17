"""
Author: wind windzu1@gmail.com
Date: 2023-09-01 14:25:23
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-09-01 14:44:40
Description: fusion main function
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""

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
        "--enable_nv",
        action="store_true",
        help="enable nv",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="/dev/video0",
        help="specify device path [default: /dev/video0]",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1280,
        help="specify image width [default: 1280]",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=720,
        help="specify image height [default: 720]",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="specify image fps [default: 30]",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="UYVY",
        help="specify image format [default: UYVY]",
    )

    parser.add_argument(
        "--store_path",
        type=str,
        default="./images",
        help="specify path to store images [default: ./images]",
    )

    args = parser.parse_args(argv)
    if args.config:
        if not os.path.exists(args.config):
            print("config file is not exist")
            return args
        else:
            with open(args.config, "r") as f:
                config = yaml.safe_load(f)
                args.enable_nv = config.get("enable_nv", args.enable_nv)
                args.device = config.get("device", args.device)
                args.width = config.get("width", args.width)
                args.height = config.get("height", args.height)
                args.fps = config.get("fps", args.fps)
                args.format = config.get("format", args.format)
                args.store_path = config.get("store_path", args.store_path)
    return args


def main(args, unknown):
    args = parse_args(unknown)

    capture = Capture(
        enable_nv=args.enable_nv,
        device=args.device,
        width=args.width,
        height=args.height,
        fps=args.fps,
        format=args.format,
        store_path=args.store_path,
    )
    capture.run()


if __name__ == "__main__":
    main()
