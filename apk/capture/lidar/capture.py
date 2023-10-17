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

import numpy as np
import rospy
from pypcd import pypcd
from sensor_msgs.msg import PointCloud2


class Capture:
    def __init__(
        self,
        topics,
        suffix,
        store_dims,
        store_path,
    ):
        self.topics = topics
        self.suffix = suffix
        self.store_dims = store_dims
        self.store_path = store_path

        self.lock = threading.Lock()
        self.captured_data = {}
        self.file_counter = {}

        if self.store_path[0] == "~":
            self.store_path = os.path.expanduser(self.store_path)

        # self.topics show be a list
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

        self.echo_info()

        # 初始化ROS节点
        rospy.init_node("capture_node", anonymous=True)

        for topic in self.topics:
            rospy.Subscriber(topic, PointCloud2, self.callback, topic)

    def echo_info(self):
        print("Capture Info:")
        print("    topics: ", self.topics)
        print("    suffix: ", self.suffix)
        print("    store_dims: ", self.store_dims)
        print("    store_path: ", self.store_path)

    def callback(self, data, topic):
        with self.lock:
            self.captured_data[topic] = data

    def save_data(self):
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

                # 构造文件名
                file_name = str(self.file_counter[sanitized_topic_name]) + self.suffix
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

                # 更新文件名计数器
                self.file_counter[sanitized_topic_name] += 1

    def run(self):
        print("Press 's' to save the point cloud data.")
        while not rospy.is_shutdown():
            key = input()
            if key == "s":
                self.save_data()
            elif key == "q":
                break
