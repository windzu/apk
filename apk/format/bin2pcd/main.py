"""
Author: wind windzu1@gmail.com
Date: 2023-11-07 17:15:41
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-11-20 19:04:58
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
"""
Author: windzu windzu1@gmail.com
Date: 2023-09-09 18:58:55
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-09-10 15:38:38
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""


from argparse import ArgumentParser

from .bin2pcd import Bin2Pcd


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="input file or folder path",
    )
    parser.add_argument(
        "--input_dims",
        type=str,
        default="xyzi",
        help="specify input file dims [default: xyzi]",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="./",
        help="specify output file or folder path [default: ./]",
    )

    args = parser.parse_args(argv)

    # check input dims
    dims = ["xyz", "xyzi", "xyzir"]
    if args.input_dims not in dims:
        raise ValueError("input dims must be one of {}".format(dims))
    return args


def main(args, unknown):
    args = parse_args(unknown)

    bin2pcd = Bin2Pcd(
        input=args.input,
        input_dims=args.input_dims,
        output=args.output,
    )
    bin2pcd.run()


if __name__ == "__main__":
    main()
