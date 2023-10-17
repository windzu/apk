"""
Author: wind windzu1@gmail.com
Date: 2023-09-08 09:53:06
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-09-08 13:06:18
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
from argparse import ArgumentParser


def main():
    # args = parse_args()
    parser = ArgumentParser(description="Awesome Perception Kit")
    subparsers = parser.add_subparsers(title="commands")

    # capture
    capture_parser = subparsers.add_parser("capture", help="capture commands")
    from .capture import main as capture_main

    capture_main.add_arguments(capture_parser)

    # calibration
    calibration_parser = subparsers.add_parser(
        "calibration", help="calibration commands"
    )
    from .calibration import main as calibration_main

    calibration_main.add_arguments(calibration_parser)

    # format
    format_parser = subparsers.add_parser("format", help="format commands")
    from .format import main as format_main

    format_main.add_arguments(format_parser)

    args, unknown = parser.parse_known_args()

    if hasattr(args, "func"):
        args.func(args, unknown)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
