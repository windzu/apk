"""
Author: windzu windzu1@gmail.com
Date: 2023-09-09 18:58:55
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-09-10 15:38:38
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""


from argparse import ArgumentParser

from .pcd2bin import Pcd2Bin


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="input file or folder path",
    )
    parser.add_argument(
        "--output_dims",
        type=str,
        default="xyzi",
        help="specify output file dims [default: xyzi]",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="./",
        help="specify output file or folder path [default: ./]",
    )

    args = parser.parse_args(argv)
    return args


def main(args, unknown):
    args = parse_args(unknown)

    pcd2bin = Pcd2Bin(
        input=args.input,
        output_dims=args.output_dims,
        output=args.output,
    )
    pcd2bin.run()


if __name__ == "__main__":
    main()
