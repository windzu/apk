"""
Author: windzu windzu1@gmail.com
Date: 2023-11-06 23:34:28
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-11-06 23:42:31
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
import argparse
import os
import time
from argparse import ArgumentParser

from rich.progress import track
from rosbag import Bag, Compression

from .merge_bag import MergeBag


class MergeRecord:
    def __init__(self, input_path_list, merge_bag_flag=False):
        self.input_path_list = input_path_list
        self.merge_bag_flag = merge_bag_flag

        recorder2rosbag_path = "~/repo_ws/optimus-modules/bin/recorder2rosbag"
        recorder2rosbag_path = os.path.expanduser(recorder2rosbag_path)
        self.recorder2rosbag = recorder2rosbag_path

        recorder2ros_config_path = (
            "~/repo_ws/optimus/recorder2bag/conf/recorder2ros_config.pb.txt"
        )
        recorder2ros_config_path = os.path.expanduser(recorder2ros_config_path)
        self.recorder2ros_config = recorder2ros_config_path

    def run(self):
        bag_file_path_list = []
        for file_path in track(self.input_path_list):
            recorder_file_name = file_path
            bag_file_name = file_path + ".bag"
            bag_file_path_list.append(bag_file_name)

            # rewrite recorder2ros_config.pb.txt
            # replace first line to "bag_file_name: ${bag_file_name}"
            # replace second line to "recorder_file_name: ${recorder_file_name}"
            with open(self.recorder2ros_config, "r") as f:
                lines = f.readlines()
                lines[0] = f"bag_file_name: {bag_file_name}\n"
                lines[1] = f"recorder_file_name: {recorder_file_name}\n"
            with open(self.recorder2ros_config, "w") as f:
                f.writelines(lines)

            # run recorder2rosbag
            os.system(f"{self.recorder2rosbag} {self.recorder2ros_config}")

        # merge bag
        if self.merge_bag_flag:
            output_bag_file_name = self.input_path_list[0].split("/")[-1].split(".")[0]
            output_bag_file_path = (
                os.path.dirname(self.input_path_list[0])
                + "/"
                + output_bag_file_name
                + ".bag"
            )
            # apk merge bag -i ./bags -o ./bags/output.bag
            merge_bag = MergeBag(
                input_path_list=bag_file_path_list, output=output_bag_file_path
            )
            merge_bag.run()


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="input file or folder path",
    )
    parser.add_argument(
        "--merge_bag",
        "-m",
        action="store_true",
        default=False,
        help="merge bag file flag",
    )
    args = parser.parse_args(argv)
    return args


def main(args, unknown):
    args = parse_args(unknown)

    # check if exit ~/repo_ws/optimus-modules/bin/recorder2rosbag
    recorder2rosbag_path = "~/repo_ws/optimus-modules/bin/recorder2rosbag"
    recorder2rosbag_path = os.path.expanduser(recorder2rosbag_path)
    if not os.path.exists(recorder2rosbag_path):
        print("Please install recorder2rosbag first!")
        return

    # check if exit ~/repo_ws/optimus/recorder2bag/conf/recorder2ros_config.pb.txt
    recorder2ros_config_path = (
        "~/repo_ws/optimus/recorder2bag/conf/recorder2ros_config.pb.txt"
    )
    recorder2ros_config_path = os.path.expanduser(recorder2ros_config_path)
    if not os.path.exists(recorder2ros_config_path):
        print("Please install recorder2rosbag first!")
        return

    input_path = args.input
    # check input_path if exists
    if not os.path.exists(input_path):
        print(f"{input_path} not exists")
        return

    merge_bag_flag = args.merge_bag

    input_path_list = []
    # check input_path if is a file or folder
    if os.path.isfile(input_path):
        input_path_list.append(input_path)
    elif os.path.isdir(input_path):
        for file in os.listdir(input_path):
            if file.split(".")[-2] == "record":
                input_path_list.append(input_path + "/" + file)

    input_path_list.sort()

    # split input_path_list to multi list by filename
    input_path_list_split = {}
    for file_path in input_path_list:
        file_name = file_path.split("/")[-1]
        file_prefix = file_name.split(".")[0]
        if file_prefix not in input_path_list_split:
            input_path_list_split[file_prefix] = [file_path]
        else:
            input_path_list_split[file_prefix].append(file_path)

    # merge record
    for file_prefix in input_path_list_split:
        input_path_list = input_path_list_split[file_prefix]
        merge_record = MergeRecord(
            input_path_list=input_path_list,
            merge_bag_flag=merge_bag_flag,
        )
        merge_record.run()
