"""
Author: windzu windzu1@gmail.com
Date: 2023-11-07 23:04:47
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-11-07 23:57:11
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
import argparse
import os
import time
from argparse import ArgumentParser

from rich.progress import track
from rosbag import Bag, Compression


class MergeBag:
    def __init__(self, input_path_list, output="./output.bag", compression="lz4"):
        self.input_path_list = input_path_list
        self.output = output
        self.compression = self.parse_compression(compression)

    def run(self):
        with Bag(self.output, "w", compression=self.compression) as o:
            for file_path in track(self.input_path_list):
                with Bag(file_path, "r") as ib:
                    for topic, msg, t in ib:
                        o.write(topic, msg, t)

    @staticmethod
    def parse_compression(compression):
        if compression == "none" or compression == "NONE":
            compression = Compression.NONE
        elif compression == "bz2":
            compression = Compression.BZ2
        elif compression == "lz4":
            compression = Compression.LZ4
        return compression


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="input folder path",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="specify output file or folder path [default: ./]",
    )

    parser.add_argument(
        "--compression",
        "-c",
        type=str,
        default="lz4",
        choices=["none", "lz4", "bz2"],
        help="Compress the bag by bz2 or lz4",
    )

    parser.add_argument(
        "--mode",
        "-m",
        type=str,
        default="implicit",
        choices=["implicit", "explicit"],
        help="Specify the mode to use when merging bags.",
    )

    args = parser.parse_args(argv)
    return args


def main(args, unknown):
    args = parse_args(unknown)

    input_path = args.input
    # check input_path if exists
    if not os.path.exists(input_path):
        print(f"{input_path} not exists")
        return

    input_path_parent_path = os.path.dirname(input_path)

    input_path_list_list = []
    # check input_path if is a file or folder
    if os.path.isfile(input_path):
        print(f"{input_path} is a file,do not need to merge")
        return
    elif os.path.isdir(input_path):
        # use walk iter all folder and file in input_path
        for root, dirs, files in os.walk(input_path):
            # check if there is a bag file in the folder
            if len(files) > 0:
                input_path_list = []
                for file in files:
                    if file.endswith(".bag"):
                        input_path_list.append(os.path.join(root, file))
                if len(input_path_list) > 0:
                    input_path_list_list.append(input_path_list)

    # check output
    output_path_list = []
    for input_path_list in input_path_list_list:
        if args.output is None:
            if args.mode == "implicit":
                output_path = os.path.join(
                    os.path.dirname(input_path_list[0]), "output.bag"
                )
            elif args.mode == "explicit":
                scene_name = os.path.basename(os.path.dirname(input_path_list[0]))
                output_path = os.path.join(input_path_parent_path, f"{scene_name}.bag")
            output_path_list.append(output_path)
        else:
            output_path = os.path.join(os.path.dirname(input_path_list[0]), args.output)
            output_path_list.append(output_path)

    for input_path_list, output_path in zip(input_path_list_list, output_path_list):
        input_path_list.sort()
        merge_bag = MergeBag(
            input_path_list=input_path_list,
            compression=args.compression,
            output=output_path,
        )
        merge_bag.run()
