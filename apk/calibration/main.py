"""
Author: windzu windzu1@gmail.com
Date: 2023-09-08 00:26:30
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-09-08 00:39:18
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""


def camera_command(args, unknown):
    print("camera command")
    from .camera import main as camera_main

    camera_main(args, unknown)


def lidar2camera_command(args):
    print("lidar2camera on the way")
    pass


def lidar2lidar_command(args):
    print("lidar2lidar on the way")
    pass

def read_sensing(args, unknown):
    from .read_sensing import main as read_sensing_main
    read_sensing_main(args, unknown)


def add_arguments(parser):
    subparsers = parser.add_subparsers(title="data commands")

    # camera
    camera_parser = subparsers.add_parser("camera", help="calibration camera")
    camera_parser.set_defaults(func=camera_command)

    # lidar2camera
    lidar2camera_parser = subparsers.add_parser(
        "lidar2camera", help="calibration lidar2camera"
    )
    lidar2camera_parser.set_defaults(func=lidar2camera_command)

    # lidar2lidar
    lidar2lidar_parser = subparsers.add_parser(
        "lidar2lidar", help="calibration lidar2lidar"
    )
    lidar2lidar_parser.set_defaults(func=lidar2lidar_command)

    # read_sensing
    read_sensing_parser = subparsers.add_parser(
        "read_sensing", help="read sensing data"
    )
    read_sensing_parser.set_defaults(func=read_sensing)