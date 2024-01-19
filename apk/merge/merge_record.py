import argparse
import os
import time
from argparse import ArgumentParser

from rich.progress import track
from rosbag import Bag, Compression

from .merge_bag import MergeBag


class MergeRecord:
    def __init__(self, records_path, file_path_list):
        self.records_path = records_path
        self.file_path_list = file_path_list

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
        scene_name = self.file_path_list[0].split("/")[-2]
        bags_folder_path = os.path.join(self.records_path, "bags")
        scene_folder_path = os.path.join(bags_folder_path, scene_name)

        # check if exit bags folder
        if not os.path.exists(scene_folder_path):
            os.makedirs(scene_folder_path)

        for i, file_path in track(enumerate(self.file_path_list)):
            recorder_file_path = file_path

            file_name = file_path.split("/")[-1]
            bag_file_path = os.path.join(scene_folder_path, file_name + ".bag")
            pb_file_path = os.path.join(scene_folder_path, file_name + ".pb.txt")

            # cp recorder2ros_config.pb.txt and change 1 2 line
            # replace first line to "bag_file_name: ${bag_file_name}"
            # replace second line to "recorder_file_name: ${recorder_file_name}"
            os.system(f"cp {self.recorder2ros_config} {pb_file_path}")

            with open(pb_file_path, "r") as f:
                lines = f.readlines()
                lines[0] = 'bag_file_name : "' + str(bag_file_path) + '"\n'
                lines[1] = 'recorder_file_name : "' + str(recorder_file_path) + '"\n'
            with open(pb_file_path, "w") as f:
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

    input_path = os.path.abspath(input_path)

    input_path_list = []
    # check input_path if is a file or folder
    if os.path.isfile(input_path):
        print("input_path should be a folder")
        return

    # get all scene file path
    scene_dict = {}
    # iter all folder in input_path
    for folder in os.listdir(input_path):
        folder_path = os.path.join(input_path, folder)
        # check if folder is a folder
        if os.path.isdir(folder_path):
            # iter all file in folder
            file_path_list = []
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                # check if file is a file
                if os.path.isfile(file_path):
                    if os.path.getsize(file_path) > 50 * 1024 * 1024:
                        file_path_list.append(file_path)
            file_path_list.sort()
            if len(file_path_list) > 0:
                scene_dict[folder] = file_path_list

    # merge record
    for scene_name in scene_dict:
        file_path_list = scene_dict[scene_name]
        merge_record = MergeRecord(
            records_path=input_path, file_path_list=file_path_list
        )
        merge_record.run()

    # generate a convert.sh
    convert_shell_path = os.path.join(input_path, "convert.sh")
    # content as below
    #     #!/bin/bash
    #     # 获取 record2bag 可执行文件的路径
    #     RECORD2BAG=$(realpath ~/repo_ws/optimus-modules/bin/recorder2rosbag)
    #
    #
    #     # 当前脚本所在目录
    #     DIR=$(dirname "$0")
    #     # get bags folder path
    #     BAGS_DIR=$(dirname "$DIR")/bags
    #
    #     # 遍历目录中的所有子文件夹
    #     for folder in $BAGS_DIR/*; do
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

    # check if exit convert_shell_path sub folder
    if not os.path.exists(os.path.dirname(convert_shell_path)):
        os.makedirs(os.path.dirname(convert_shell_path))

    with open(convert_shell_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(
            "# 获取 record2bag 可执行文件的路径\n"
            "RECORD2BAG=$(realpath ~/repo_ws/optimus-modules/bin/recorder2rosbag)\n\n"
        )
        f.write("# 当前脚本所在目录\n")
        f.write('DIR=$(dirname "$0")\n\n')
        f.write("# get bags folder path\n")
        f.write('BAGS_DIR=$(dirname "$DIR")/bags\n\n')
        f.write("# 遍历目录中的所有子文件夹\n")
        f.write("for folder in $BAGS_DIR/*; do\n")
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
