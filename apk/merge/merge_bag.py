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
            start = time.perf_counter()
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
        help="input file or folder path",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="./output.bag",
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

    args = parser.parse_args(argv)
    return args


def main(args, unknown):
    args = parse_args(unknown)

    input_path = args.input
    # check input_path if exists
    if not os.path.exists(input_path):
        print(f"{input_path} not exists")
        return

    input_path_list = []
    # check input_path if is a file or folder
    if os.path.isfile(input_path):
        # check suffix if is .bag
        if input_path.endswith(".bag"):
            input_path_list.append(input_path)
        else:
            print(f"{input_path} is not a bag file")
            return
    elif os.path.isdir(input_path):
        # check suffix if is .bag
        for file in os.listdir(input_path):
            if file.endswith(".bag"):
                input_path_list.append(input_path + "/" + file)

    input_path_list.sort()
    merge_bag = MergeBag(
        input_path_list=input_path_list,
        compression=args.compression,
        output=args.output,
    )
    merge_bag.run()
