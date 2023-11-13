"""
Author: wind windzu1@gmail.com
Date: 2023-08-31 16:05:20
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-08-31 16:08:35
Description: calib camera main function
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""

from argparse import ArgumentParser

from .sensing_reader import SensingReader
from .common import SUPPORT_CAMERA_INFO_DICT


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument(
        "--camera",
        type=str,
        help="camera model",
    )
    parser.add_argument(
        "--i2c_bus",
        type=str,
        help="i2c bus",
    )
    parser.add_argument(
        "--i2c_addr",
        type=str,
        help="i2c addr",
    )

    args = parser.parse_args(argv)

    # camera model should in support list
    camera = args.camera
    # a-z to A-Z
    camera = camera.upper()
    if camera not in SUPPORT_CAMERA_INFO_DICT.keys():
        print("camera model should in support list")
        return args

    return args


def main(args, unknown):
    args = parse_args(unknown)

    camera_model = args.camera
    i2c_bus = args.i2c_bus
    i2c_addr = args.i2c_addr

    sensing_reader = SensingReader(
        camera_model=camera_model,
        i2c_bus=i2c_bus,
        i2c_addr=i2c_addr,
    )
    sensing_reader.read()
