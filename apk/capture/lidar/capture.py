"""
Author: windzu windzu1@gmail.com
Date: 2023-09-09 18:58:55
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-09-10 15:38:58
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""

import os
import threading
import rosbag

import numpy as np
import rospy
from pypcd import pypcd
from sensor_msgs.msg import PointCloud2


class Capture:
    """capture point cloud data from ROS topic and save to file

    Args:
        topics (list): topics which need to subscribe
        suffix (str): specify file suffix [default: .pcd]
        store_dims (str): specify dims to store [default: xyzi]
        store_path (str): specify store path [default: ./]

    """

    def __init__(
        self,
        file,
        topics,
        suffix,
        store_method,
        store_interval,
        store_dims,
        store_path,
    ):
        self.file = file
        self.topics = topics
        self.suffix = suffix
        self.store_method = store_method
        self.store_interval = store_interval
        self.store_dims = store_dims
        self.store_path = store_path

        self.auto_save_flag = False
        self.lock = threading.Lock()
        self.captured_data = {}
        self.file_counter = {}

        self._param_check()
        self._echo_info()

    def _param_check(self):
        #############################################
        # necessary params check
        #############################################
        # store_path should be a valid path
        if self.store_path[0] == "~":
            self.store_path = os.path.expanduser(self.store_path)

        # self.topics should be a list
        if not isinstance(self.topics, list):
            self.topics = [self.topics]

        # self.suffix should in support_suffix list
        support_suffix = [".pcd", ".bin"]
        if self.suffix not in support_suffix:
            raise ValueError("suffix should be one of {}".format(support_suffix))

        # self.store_dims should in support_dims list
        support_dims = ["xyz", "xyzi"]
        if self.store_dims not in support_dims:
            raise ValueError("store_dims should be one of {}".format(support_dims))

        #############################################
        # store_method check
        #############################################
        if self.store_method not in ["auto", "manual"]:
            raise ValueError("store_method is not valid")
        # auto store method check
        # - should have store_interval
        # - should have file
        # - file should end with .bag
        if self.store_method == "auto":
            if self.store_interval < 0:
                raise ValueError("store_interval should not be 0")
            if not os.path.exists(self.file):
                raise ValueError("file should not be valid")
            if not self.file.endswith(".bag"):
                raise ValueError("file should end with .bag")
            self.auto_save_flag = True

    def _echo_info(self):
        print("Capture Info:")
        print("    topics: ", self.topics)
        print("    suffix: ", self.suffix)
        print("    store_dims: ", self.store_dims)
        print("    store_path: ", self.store_path)

    def callback(self, data, topic):
        with self.lock:
            self.captured_data[topic] = data

    def manual_save_data(self):
        with self.lock:
            for topic, data in self.captured_data.items():
                sanitized_topic_name = topic.replace("/", "_")
                if sanitized_topic_name[0] == "_":
                    sanitized_topic_name = sanitized_topic_name[1:]
                dir_path = os.path.join(self.store_path, sanitized_topic_name)

                # 创建文件夹
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                if sanitized_topic_name not in self.file_counter:
                    self.file_counter[sanitized_topic_name] = 0

                # 使用msg的header中的时间戳
                timestamp_ns = data.header.stamp.to_nsec()
                timestamp_ms = round(timestamp_ns / 1e6)  # 转换为毫秒

                # 构造文件名
                file_name = str(timestamp_ms) + self.suffix
                full_file_path = os.path.join(dir_path, file_name)

                # # 构造文件名
                # file_name = str(self.file_counter[sanitized_topic_name]) + self.suffix
                # full_file_path = os.path.join(dir_path, file_name)

                if self.suffix == ".pcd":
                    # 保存为PCD格式
                    pc = pypcd.PointCloud.from_msg(data)
                    pc.save_pcd(full_file_path, compression="binary_compressed")
                    print("save pcd file to: ", full_file_path)
                elif self.suffix == ".bin":
                    # 保存为bin格式
                    pc = pypcd.PointCloud.from_msg(data)
                    pc.save_bin(full_file_path, self.store_dims)
                    print("save bin file to: ", full_file_path)

                # 更新文件名计数器
                self.file_counter[sanitized_topic_name] += 1

    def auto_save_data(self, topic, data, timestamp):
        sanitized_topic_name = topic.replace("/", "_")
        if sanitized_topic_name[0] == "_":
            sanitized_topic_name = sanitized_topic_name[1:]
        folder_name = self.file.split("/")[-1].split(".")[0]
        dir_path = os.path.join(self.store_path, folder_name, sanitized_topic_name)

        # 创建文件夹
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # 构造文件名
        # file_name = str(self.file_counter[sanitized_topic_name]) + self.suffix
        file_name = str(timestamp) + self.suffix
        full_file_path = os.path.join(dir_path, file_name)

        if self.suffix == ".pcd":
            # 保存为PCD格式
            pc = pypcd.PointCloud.from_msg(data)
            pc.save_pcd(full_file_path, compression="binary_compressed")
            print("save pcd file to: ", full_file_path)
        elif self.suffix == ".bin":
            # 保存为bin格式
            pc = pypcd.PointCloud.from_msg(data)
            pc.save_bin(full_file_path, self.store_dims)
            print("save bin file to: ", full_file_path)

    def run(self):
        if self.auto_save_flag:
            self.auto_save()
        else:
            self.manual_save()

    def auto_save(self):
        print("Auto save mode")
        # use rosbag to parse rosbag file
        # - parse rosbag file
        # - get specified topics data
        # - save data to file by store_interval

        try:
            with rosbag.Bag(self.file, "r") as bag:
                for topic, msg, t in bag.read_messages():
                    if topic in self.topics:
                        # store data by store_interval
                        timpstamp = t.to_nsec()
                        # convert ns to ms with round
                        timpstamp_ms = round(timpstamp / 1e6)
                        if self.store_interval == 0:
                            self.auto_save_data(topic, msg, timpstamp_ms)
                        elif timpstamp_ms % self.store_interval == 0:
                            self.auto_save_data(topic, msg, timpstamp_ms)
        except rosbag.bag.ROSBagException as e:
            raise RuntimeError(f"Failed to open bag file {self.file}: {str(e)}")

    def manual_save(self):
        print("Manual save mode")
        # 初始化ROS节点
        rospy.init_node("capture_node", anonymous=True)

        for topic in self.topics:
            rospy.Subscriber(topic, PointCloud2, self.callback, topic)

        print("Press 's' to save the point cloud data.")
        while not rospy.is_shutdown():
            key = input()
            if key == "s":
                self.manual_save_data()
            elif key == "q":
                break
