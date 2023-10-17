"""
Author: wind windzu1@gmail.com
Date: 2023-09-08 09:53:06
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-09-08 13:07:43
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""


def camera_command(args, unknown):
    print("capture camera command")
    from .camera import main as camera_main

    camera_main(args, unknown)


def lidar_command(args, unknown):
    print("capture lidar command")
    from .lidar import main as lidar_main

    lidar_main(args, unknown)


def add_arguments(parser):
    subparsers = parser.add_subparsers(title="capture commands")

    # camera
    camera_parser = subparsers.add_parser("camera", help="capture camera")
    camera_parser.set_defaults(func=camera_command)

    # lidar
    lidar_parser = subparsers.add_parser("lidar", help="capture lidar")
    lidar_parser.set_defaults(func=lidar_command)
