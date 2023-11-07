"""
Author: wind windzu1@gmail.com
Date: 2023-11-07 17:15:41
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-11-07 22:48:06
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
"""
Author: wind windzu1@gmail.com
Date: 2023-11-07 17:15:41
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-11-07 17:39:26
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
        # create a folder to save config file
        bags_folder_path = os.path.join(
            os.path.dirname(self.input_path_list[0]), "bags"
        )
        # check if exit bags folder
        if not os.path.exists(bags_folder_path):
            os.makedirs(bags_folder_path)

        config_folder_name = self.input_path_list[0].split("/")[-1].split(".")[0]
        config_folder_path = os.path.join(bags_folder_path, config_folder_name)

        if not os.path.exists(config_folder_path):
            os.makedirs(config_folder_path)

        bag_file_path_list = []
        for i, file_path in track(enumerate(self.input_path_list)):
            recorder_file_name = file_path
            bag_file_name = file_path + ".bag"
            bag_file_name = os.path.join(
                config_folder_path, bag_file_name.split("/")[-1]
            )
            bag_file_path_list.append(bag_file_name)

            # cp recorder2ros_config.pb.txt and change 1 2 line
            # replace first line to "bag_file_name: ${bag_file_name}"
            # replace second line to "recorder_file_name: ${recorder_file_name}"
            new_config_name = f"{config_folder_path}/{i}.pb.txt"
            os.system(f"cp {self.recorder2ros_config} {new_config_name}")

            with open(new_config_name, "r") as f:
                lines = f.readlines()
                lines[0] = 'bag_file_name : "' + str(bag_file_name) + '"\n'
                lines[1] = 'recorder_file_name : "' + str(recorder_file_name) + '"\n'
            with open(new_config_name, "w") as f:
                f.writelines(lines)


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
        print("input_path should be a folder")
        return
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

    # generate a convert.sh
    convert_shell_path = os.path.join(input_path, "bags", "convert.sh")
    # content as below
    #     #!/bin/bash
    #     # 获取 record2bag 可执行文件的路径
    #     RECORD2BAG=$(realpath ~/repo_ws/optimus-modules/bin/recorder2rosbag)
    #
    #
    #     # 当前脚本所在目录
    #     DIR=$(dirname "$0")
    #
    #     # 遍历目录中的所有子文件夹
    #     for folder in $DIR/*; do
    #         # 检查是否为目录
    #         if [ -d "$folder" ]; then
    #             # 遍历目录中的所有.pb.txt文件
    #             for file in $folder/*.pb.txt; do
    #                 # 检查文件是否存在
    #                 if [ -f "$file" ]; then
    #                     # 执行test命令
    #                     $RECORD2BAG "$file"
    #                 fi
    #             done
    #         fi
    #     done
    #
    #     # 结束脚本
    #     echo "Conversion complete."

    with open(convert_shell_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(
            "# 获取 record2bag 可执行文件的路径\n"
            "RECORD2BAG=$(realpath ~/repo_ws/optimus-modules/bin/recorder2rosbag)\n\n"
        )
        f.write("# 当前脚本所在目录\n")
        f.write('DIR=$(dirname "$0")\n\n')
        f.write("# 遍历目录中的所有子文件夹\n")
        f.write("for folder in $DIR/*; do\n")
        f.write("    # 检查是否为目录\n")
        f.write('    if [ -d "$folder" ]; then\n')
        f.write("        # 遍历目录中的所有.pb.txt文件\n")
        f.write("        for file in $folder/*.pb.txt; do\n")
        f.write("            # 检查文件是否存在\n")
        f.write('            if [ -f "$file" ]; then\n')
        f.write("                # 执行test命令\n")
        f.write('                $RECORD2BAG "$file"\n')
        f.write("            fi\n")
        f.write("        done\n")
        f.write("    fi\n")
        f.write("done\n\n")
        f.write("# 结束脚本\n")
        f.write('echo "Conversion complete."\n')

    os.system(f"chmod +x {convert_shell_path}")
